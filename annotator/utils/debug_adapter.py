from dspy.adapters.json_adapter import JSONAdapter

class DebugJSONAdapter(JSONAdapter):
    def parse(self, signature, completion: str):
        # 🔎 Print raw LLM output before any regex/JSON repair
        print("\n================ RAW LM OUTPUT ================\n")
        print(completion)
        print("\n==============================================\n")
        
        # Call the normal JSONAdapter parsing logic
        return super().parse(signature, completion)
