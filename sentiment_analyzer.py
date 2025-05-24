import numpy as np
from scipy.special import softmax
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import logging
from exceptions import ModelError
from config import config

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    def __init__(self):
        self.tokenizer = None
        self.model = None
        self.id2label = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentiment analysis model"""
        try:
            logger.info(f"Loading model: {config.MODEL_NAME}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                config.MODEL_NAME, 
                cache_dir=config.CACHE_DIR
            )
            
            self.model = AutoModelForSequenceClassification.from_pretrained(
                config.MODEL_NAME, 
                cache_dir=config.CACHE_DIR
            )
            
            self.id2label = self.model.config.id2label
            self.model.eval()
            
            # Move to GPU if available
            if torch.cuda.is_available():
                self.model = self.model.cuda()
                logger.info("Model moved to GPU")
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.exception("Failed to load model")
            raise ModelError(f"Model loading failed: {str(e)}")
    
    def _chunk_text(self, text):
        """Split text into chunks"""
        sentences = text.split(". ")
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence + "." if not sentence.endswith(".") else sentence
            
            if len(current_chunk) + len(sentence) <= config.CHUNK_SIZE:
                current_chunk += " " + sentence if current_chunk else sentence
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def analyze(self, text):
        """Analyze sentiment"""
        try:
            chunks = self._chunk_text(text)
            logger.info(f"Processing {len(chunks)} chunks")
            
            all_probs = []
            
            for chunk in chunks:
                try:
                    inputs = self.tokenizer(
                        chunk, 
                        return_tensors="pt", 
                        truncation=True, 
                        padding=True,
                        max_length=512
                    )
                    
                    # Move to GPU if available
                    if torch.cuda.is_available():
                        inputs = {k: v.cuda() for k, v in inputs.items()}
                    
                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        logits = outputs.logits[0].cpu().numpy()
                    
                    probs = softmax(logits)
                    all_probs.append(probs)
                    
                except Exception as e:
                    logger.error(f"Error processing chunk: {e}")
                    continue
            
            if not all_probs:
                raise ModelError("No chunks processed successfully")
            
            # Calculate average probabilities
            all_probs = np.array(all_probs)
            avg_probs = np.mean(all_probs, axis=0)
            
            # Create result
            scores = {
                self.id2label[i].lower(): round(float(avg_probs[i]), 4)
                for i in range(len(avg_probs))
            }
            
            prominent_sentiment = max(scores, key=scores.get).upper()
            
            return {
                "model": config.MODEL_NAME,
                "scores": scores,
                "prominent_sentiment": prominent_sentiment,
                "num_chunks": len(chunks),
                "confidence": round(float(max(avg_probs)), 4)
            }
            
        except Exception as e:
            logger.exception("Sentiment analysis failed")
            raise ModelError(f"Analysis failed: {str(e)}")
