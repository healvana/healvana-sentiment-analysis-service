import os

class Config:
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Model
    MODEL_NAME = os.getenv("MODEL_NAME", "waimoe/mental-health-sentiment-analysis-model")
    CACHE_DIR = os.getenv("CACHE_DIR", "./models")
    MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "10000"))
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "510"))
    
    # URL Processing
    URL_TIMEOUT = int(os.getenv("URL_TIMEOUT", "10"))
    MAX_URL_SIZE = int(os.getenv("MAX_URL_SIZE", "5242880"))  # 5MB

config = Config()
