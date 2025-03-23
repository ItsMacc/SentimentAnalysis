from SentimentAnalysis.Exceptions.errors import ModelNotSupportedError

def detect_sarcasm(model, *args):
    if model not in ["2.0", "3.0"]:
        raise ModelNotSupportedError(model, "Sarcasm Detection")
    pass

def conversation_score(model, *args):
    if model not in ["2.0", "3.0"]:
        raise ModelNotSupportedError(model, "Conversation Score")
    pass