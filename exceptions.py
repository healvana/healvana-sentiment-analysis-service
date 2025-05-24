class SentimentAnalysisError(Exception):
    pass

class TextExtractionError(SentimentAnalysisError):
    pass

class ModelError(SentimentAnalysisError):
    pass

class ValidationError(SentimentAnalysisError):
    pass
