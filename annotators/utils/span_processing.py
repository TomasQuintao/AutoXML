from rapidfuzz import fuzz
import re

# WARNING: If correctIndex takes too long, 
# change adjustMargins to stop after the ratio decreases n times

def correctIndex(spans, doc, threshold=0.85):
    """Finds the most similar same size string for each span
       in the doc, and then adjusts the margins if needed"""
    
    new_spans = []
    for span in spans:
        
        string = span['text']
        (start, end) = findIndex(string, span['start'], doc, threshold)
        
        if((start, end) == (0,0)): # No match
            continue
        
        new_span = {'text': doc[start:end], 'label': span['label'], 'start': start, 'end': end} 
        
        new_spans.append(new_span)
    
    return new_spans


def findIndex(string, start, doc, threshold):
    
    window = len(string)
    pair = (0,0)
    last_i = 0
    
    for i in range(len(doc)-window+1):
        
        slize = doc[i:i+window]
        
        ratio = fuzz.ratio(string, slize)

        if (ratio > threshold):
            pair = (i, i+window)
            threshold = ratio
            last_i = i
        # In case there are several matches, choose the closest one
        elif (ratio == threshold and abs(start-i) < abs(start-last_i)):
            pair = (i, i+window)
            threshold = ratio
            last_i = i
    
    # Check if the margins are correct
    if pair != (0,0):
        pair = adjustMargins(pair, string, doc, threshold)
    
    return pair

def adjustMargins(pair, string, doc, threshold):
    
    start, end = pair
    new_start, new_end = pair
    slize = doc[start:end]
        
    # Beggining incorrect
    if (slize[0] != string[0]):

        # Outwards
        if(start > 0):
            for i in range(1, start+1):
                new_slize = doc[start-i:end]
                ratio = fuzz.ratio(string, new_slize)
                
                if ratio > threshold:
                    threshold = ratio
                    new_start = start-i
                    
        # If not outwards, then inward
        if(new_start == pair[0]):
            for i in range(1, end-start+1):
                new_slize = doc[start+i:end]
                ratio = fuzz.ratio(string, new_slize)
 
                if ratio > threshold:
                    threshold = ratio
                    new_start = start+i
                    
    # End incorrect
    if (slize[-1] != string[-1]):
        
        end_file = len(doc)-1
        # Outwards
        if(end < end_file):
            for i in range(1, end_file-end+1):
                new_slize = doc[start:end+i]
                ratio = fuzz.ratio(string, new_slize)
                
                if ratio > threshold:
                    threshold = ratio
                    new_end = end+i
                    
        # If not outwards, then inward
        if(new_end == pair[1]):
            for i in range(1, end-start+1):
                new_slize = doc[start:end-i]
                ratio = fuzz.ratio(string, new_slize)

                if ratio >= threshold:
                    threshold = ratio
                    new_end = end-i

    return (new_start, new_end)

def stripSpans(spans):
    
    for span in spans:
        text = span['text']
        start = span['start']
        end = span['end']
        
        left = len(text) - len(text.lstrip())
        right = len(text) - len(text.rstrip())
        
        span['text'] = text.strip()
        span['start'] = start + left
        end = span['end'] = end - right
    
    return spans