import requests
from goose3 import Goose
import logging
from exceptions import TextExtractionError
from config import config

logger = logging.getLogger(__name__)

class TextExtractor:
    def __init__(self):
        self.goose = Goose()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SentimentAnalyzer/1.0'
        })
    
    def extract_text(self, url):
        """Extract text from URL"""
        try:
            logger.info(f"Extracting text from: {url}")
            
            # Check content size
            try:
                head_response = self.session.head(url, timeout=config.URL_TIMEOUT)
                content_length = head_response.headers.get('content-length')
                if content_length and int(content_length) > config.MAX_URL_SIZE:
                    raise TextExtractionError(f"Content too large: {content_length} bytes")
            except Exception:
                pass  # Continue anyway
            
            # Extract text
            article = self.goose.extract(url=url)
            
            if not article.cleaned_text:
                raise TextExtractionError("No readable text found")
            
            logger.info(f"Extracted {len(article.cleaned_text)} characters")
            return article.cleaned_text
            
        except requests.exceptions.Timeout:
            raise TextExtractionError("Request timeout")
        except requests.exceptions.ConnectionError:
            raise TextExtractionError("Connection failed")
        except Exception as e:
            logger.exception("Text extraction failed")
            raise TextExtractionError(f"Extraction failed: {str(e)}")
