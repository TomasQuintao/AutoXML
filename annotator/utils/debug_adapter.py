from dspy.adapters.json_adapter import JSONAdapter

class DebugJSONAdapter(JSONAdapter):
    def parse(self, signature, completion: str):
        print("\n================ RAW LM OUTPUT ================\n")
        print(completion)
        print("\n==============================================\n")
        
        return super().parse(signature, completion)
