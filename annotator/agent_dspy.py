import os, dspy, re, sys, spacy
from typing import Literal, TypedDict
from spacy.scorer import Scorer
from spacy.tokens import Doc
from dspy.evaluate import Evaluate

from annotator.utils.span_processing import correctIndex, stripSpans
from annotator.utils.debug_adapter import DebugJSONAdapter
from annotator.dtd_parser.functions import parseDTD, get_labels

def genSignature(dtd):
    ##TODO: Decide if the dtd is provided in the prompt instead of with every example
    
    dtd_tree = parseDTD(dtd)
    labels = get_labels(dtd_tree) 

    LABELS = Literal [*labels]
               
    class Span(TypedDict):
        text : str
        label : LABELS
        start : int
        end : int
    
    class ExtractAnnotations(dspy.Signature):
        """
        Identify and label spans of text using the tags provided by the DTD.
        Follow these rules strictly:
            1. DTD Compliance: Only use tags defined in the provided DTD and follow the DTD structure and hierarchy.
            2. Original Text: Do not alter the text you capture in any way, this includes white space characters.
            3. Hierarchical Annotation: - First identify and annotate major sections.
                                        - Then annotate the finer spans inside each section.
                                        - Maintain proper nesting according to the DTD.
        """ 
        
        raw_text : str = dspy.InputField(desc="Raw text to be annotated")
        dtd : str = dspy.InputField(desc="The DTD you must follow")
        spans : list[Span] = dspy.OutputField(desc="List of spans identified in the raw text")
        
    return ExtractAnnotations
    
class Annotator(dspy.Module):
    """A text annotator"""

    def __init__(self, dtd: str, threshold: float = 0.85):
        super().__init__()
        
        self.dtd = dtd
        self.threshold = threshold
        self.signature = genSignature(dtd)
        self.extractor = dspy.Predict(self.signature)

    def forward(self, raw_text: str):
        """Run annotation and apply post-processing"""
        
        try:
            annotation = self.extractor(raw_text=raw_text, dtd=self.dtd)
            raw_spans = annotation.spans
        except Exception as e:
            print("Warning: DSPy failed to parse structured output:", e)
            raw_spans = []
        
        #print(len(raw_spans))
        #print("\nMISALIGNED\n", annotation.spans)
        aligned_spans = correctIndex(raw_spans, raw_text, threshold=self.threshold)
        #print("\nALIGNED\n", aligned_spans)
        spans = stripSpans(aligned_spans)
        
        return dspy.Prediction(spans=spans)


def genAgent(dtd, examples, modelID, api_key, optimization="few_shot", max_tokens=4000):
    
    api_key = os.getenv(api_key)
    if not api_key:
        raise RuntimeError(
            """The environment variable 'TOGETHER_AI_API_KEY' is not set. 
            Set it before running this script."""
        )
        
    model_family = modelID.split("/")[-1].lower() if "/" in modelID else modelID.lower()
    # Recognize OpenAI reasoning models (o1, o3, o4, gpt-5 family)
    model_pattern = re.match(r"^(?:o[1345]|gpt-5)(?:-(?:mini|nano))?", model_family)
    
    if model_pattern:
        temperature = 1.0
        max_tokens = 20000
    else:
        temperature = 0.0

    lm = dspy.LM(modelID, temperature=temperature, api_key=api_key,
                max_tokens=max_tokens, verbose=True)
    dspy.settings.adapter = DebugJSONAdapter()
    dspy.configure(lm=lm)
    
    annotator = Annotator(dtd)
    
    if (examples != []):
        
        if (optimization == "prompt"):
            #to be finished
            pass
        else:
            if (optimization != "few_shot"):
                print(f"Warning: Invalid optimization setting -> {optimization}.",
                      "Must be set to 'few_shot' or 'prompt'. Using 'few_shot' as default.")
            
            optimizer = dspy.LabeledFewShot(k=len(examples))
            annotator = optimizer.compile(student=annotator, trainset=examples) 
    else:
        print("Using uncompiled annotator")
    
    return annotator, lm
    
def metric_f1(example, prediction, trace=None):
    
    text = example.raw_text
    
    eg_spans = example.spans
    pred_spans = prediction.spans
    #print("\nGOLD\n",eg_spans,"\nPRED\n",pred_spans)
    
    nlp = spacy.blank('en')
    spancat = nlp.add_pipe("spancat")
    scorer = Scorer(nlp)
    
    eg_doc = nlp.make_doc(text)
    spans = []
    for eg_span in eg_spans:
        span = eg_doc.char_span(eg_span['start'], eg_span['end'], label=eg_span['label'])
        if span:
            spans.append(span)
    eg_doc.spans['sc'] = spans
    
    pred_doc = nlp.make_doc(text)
    spans = []
    for pred_span in pred_spans:
        span = pred_doc.char_span(pred_span['start'], pred_span['end'], label=pred_span['label'])
        if span:
            spans.append(span)
    pred_doc.spans['sc'] = spans
    
    # score function receives a list as input
    scores = scorer.score([spacy.training.Example(eg_doc, pred_doc)])
    
    return scores['spans_sc_f']
    
# Set up the evaluator, which can be re-used in your code.
#evaluator = Evaluate(devset=devset, num_threads=1, display_progress=True, display_table=5)

# EVALUATION #
#evaluator(dtd_annotator, metric=metric_f1)


