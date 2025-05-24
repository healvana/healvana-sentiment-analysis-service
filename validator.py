import re
from urllib.parse import urlparse
from exceptions import ValidationError

def validate_text(text):
    """Simple text validation"""
    if not text or not text.strip():
        raise ValidationError("Text cannot be empty")
    
    text = text.strip()
    
    if len(text) > 10000:
        raise ValidationError("Text too long (max 10000 characters)")
    
    # Basic sanitization
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    return text

def validate_url(url):
    """Simple URL validation"""
    if not url or not url.strip():
        raise ValidationError("URL cannot be empty")
    
    url = url.strip()
    
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise ValidationError("Invalid URL format")
        
        if parsed.scheme not in ['http', 'https']:
            raise ValidationError("Only HTTP/HTTPS URLs allowed")
            
        return url
    except Exception:
        raise ValidationError("Invalid URL format")
