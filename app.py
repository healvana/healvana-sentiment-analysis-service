import logging
import sys
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_restx import Api, Resource, fields, Namespace
import uuid
import time
from config import config
from exceptions import *
from validator import validate_text, validate_url
from text_extractor import TextExtractor
from sentiment_analyzer import SentimentAnalyzer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Swagger API
api = Api(
    app,
    version='1.0.0',
    title='Mental Health Sentiment Analysis API',
    description='AI-powered sentiment analysis for mental health content in text and web pages',
    doc='/docs/',  # Swagger UI will be available at /docs/
    prefix='/api'  # All API endpoints will be prefixed with /api
)

# Create namespaces for better organization
analysis_ns = Namespace('analysis', description='Sentiment Analysis Operations')
health_ns = Namespace('health', description='Health Check Operations')

api.add_namespace(analysis_ns)
api.add_namespace(health_ns)

# Define request/response models for Swagger documentation
analysis_request_model = api.model('AnalysisRequest', {
    'type': fields.String(required=True, description='Input type', enum=['text', 'url'], example='text'),
    'input': fields.String(required=True, description='Text content or URL to analyze', example='I am feeling great today!')
})

scores_model = api.model('Scores', {
    'positive': fields.Float(description='Positive sentiment score', example=0.8234),
    'negative': fields.Float(description='Negative sentiment score', example=0.1245),
    'neutral': fields.Float(description='Neutral sentiment score', example=0.0521)
})

analysis_response_model = api.model('AnalysisResponse', {
    'model': fields.String(description='AI model used for analysis', example='waimoe/mental-health-sentiment-analysis-model'),
    'scores': fields.Nested(scores_model, description='Detailed sentiment scores'),
    'prominent_sentiment': fields.String(description='Most prominent sentiment', example='POSITIVE'),
    'num_chunks': fields.Integer(description='Number of text chunks processed', example=1),
    'confidence': fields.Float(description='Confidence score (0-1)', example=0.8234),
    'request_id': fields.String(description='Unique request identifier', example='123e4567-e89b-12d3-a456-426614174000'),
    'timestamp': fields.String(description='Analysis timestamp', example='2025-01-01T12:00:00.000Z')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message', example='Input required'),
    'request_id': fields.String(description='Request identifier', example='123e4567-e89b-12d3-a456-426614174000')
})

health_response_model = api.model('HealthResponse', {
    'status': fields.String(description='Service status', enum=['healthy', 'unhealthy'], example='healthy'),
    'timestamp': fields.String(description='Check timestamp', example='2025-01-01T12:00:00.000Z')
})

# Initialize components
text_extractor = TextExtractor()
sentiment_analyzer = SentimentAnalyzer()

@app.before_request
def before_request():
    """Log request start"""
    request.start_time = time.time()
    request.request_id = str(uuid.uuid4())
    if request.endpoint not in ['static', 'favicon', 'restx_doc.static']:
        logger.info(f"Request {request.request_id}: {request.method} {request.path}")

@app.after_request
def after_request(response):
    """Log request end"""
    if hasattr(request, 'start_time') and request.endpoint not in ['static', 'favicon', 'restx_doc.static']:
        duration = time.time() - request.start_time
        logger.info(f"Request {getattr(request, 'request_id', 'unknown')} completed in {duration:.3f}s - Status: {response.status_code}")
    response.headers['X-Request-ID'] = getattr(request, 'request_id', 'unknown')
    return response

# Frontend routes (non-API)
@app.route('/')
def index():
    """Serve the frontend interface"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

# API Routes with Swagger documentation
@health_ns.route('')
class HealthCheck(Resource):
    @health_ns.doc('health_check')
    @health_ns.marshal_with(health_response_model)
    @health_ns.response(200, 'Service is healthy')
    @health_ns.response(503, 'Service is unhealthy')
    def get(self):
        """
        Check API health status
        
        Performs a quick test of the sentiment analysis model to ensure the service is operational.
        """
        try:
            # Quick test
            sentiment_analyzer.analyze("test")
            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat()
            }, 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }, 503

@analysis_ns.route('')
class SentimentAnalysis(Resource):
    @analysis_ns.doc('analyze_sentiment')
    @analysis_ns.expect(analysis_request_model)
    @analysis_ns.marshal_with(analysis_response_model)
    @analysis_ns.response(200, 'Analysis completed successfully')
    @analysis_ns.response(400, 'Bad request - validation error', error_model)
    @analysis_ns.response(422, 'Unprocessable entity - text extraction failed', error_model)
    @analysis_ns.response(503, 'Service unavailable - model error', error_model)
    def post(self):
        """
        Analyze sentiment in text or web content
        
        Analyzes the sentiment of provided text or extracts and analyzes text from a given URL.
        The API uses advanced AI models specifically trained for mental health sentiment analysis.
        
        **Input Types:**
        - `text`: Direct text analysis
        - `url`: Extract and analyze text from web page
        
        **Supported Sentiments:**
        - Positive, Negative, Neutral (and other model-specific categories)
        
        **Text Limits:**
        - Maximum text length: 10,000 characters
        - URL content limit: 5MB
        - Request timeout: 10 seconds
        """
        try:
            data = request.get_json()
            
            if not data:
                return {"error": "JSON data required", "request_id": getattr(request, 'request_id', 'unknown')}, 400
            
            input_type = data.get("type", "").strip().lower()
            input_value = data.get("input", "").strip()
            
            if not input_value:
                return {"error": "Input required", "request_id": getattr(request, 'request_id', 'unknown')}, 400
            
            # Process input
            if input_type == "url":
                validated_url = validate_url(input_value)
                text = text_extractor.extract_text(validated_url)
            elif input_type == "text":
                text = validate_text(input_value)
            else:
                return {"error": "Type must be 'text' or 'url'", "request_id": getattr(request, 'request_id', 'unknown')}, 400
            
            # Analyze sentiment
            result = sentiment_analyzer.analyze(text)
            result["request_id"] = getattr(request, 'request_id', 'unknown')
            result["timestamp"] = datetime.utcnow().isoformat()
            
            logger.info(f"Analysis completed: {result['prominent_sentiment']}")
            return result, 200
            
        except ValidationError as e:
            return {"error": str(e), "request_id": getattr(request, 'request_id', 'unknown')}, 400
        except TextExtractionError as e:
            return {"error": str(e), "request_id": getattr(request, 'request_id', 'unknown')}, 422
        except ModelError as e:
            return {"error": "Analysis failed", "request_id": getattr(request, 'request_id', 'unknown')}, 503
        except Exception as e:
            logger.exception("Unexpected error")
            return {"error": "Internal error", "request_id": getattr(request, 'request_id', 'unknown')}, 500

# Legacy API endpoint for backward compatibility
@app.route('/analyze', methods=['POST'])
def legacy_analyze():
    """Legacy endpoint for backward compatibility"""
    return SentimentAnalysis().post()

@app.route('/health', methods=['GET'])
def legacy_health():
    """Legacy health endpoint for backward compatibility"""
    return HealthCheck().get()

# API info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        "name": "Mental Health Sentiment Analysis API",
        "version": "1.0.0",
        "documentation": {
            "swagger_ui": f"http://{config.HOST}:{config.PORT}/docs/",
            "openapi_spec": f"http://{config.HOST}:{config.PORT}/swagger.json"
        },
        "endpoints": {
            "POST /api/analysis": "Analyze sentiment (documented)",
            "GET /api/health": "Health check (documented)",
            "POST /analyze": "Legacy analyze endpoint",
            "GET /health": "Legacy health endpoint",
            "GET /": "Web interface",
            "GET /docs/": "Swagger documentation"
        },
        "usage": {
            "web_interface": f"http://{config.HOST}:{config.PORT}/",
            "api_documentation": f"http://{config.HOST}:{config.PORT}/docs/",
            "text_analysis": {
                "method": "POST",
                "url": "/api/analysis",
                "body": {"type": "text", "input": "your text here"}
            },
            "url_analysis": {
                "method": "POST", 
                "url": "/api/analysis",
                "body": {"type": "url", "input": "https://example.com"}
            }
        }
    })

@app.errorhandler(404)
def not_found(error):
    if request.path.startswith('/api/'):
        return jsonify({"error": "API endpoint not found"}), 404
    return render_template('index.html')  # Serve frontend for non-API routes

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == "__main__":
    logger.info("Starting Mental Health Sentiment Analysis API with Swagger Documentation")
    logger.info(f"Config: DEBUG={config.DEBUG}, PORT={config.PORT}")
    logger.info(f"Frontend: http://{config.HOST}:{config.PORT}")
    logger.info(f"API Documentation: http://{config.HOST}:{config.PORT}/docs/")
    logger.info(f"API Endpoints: http://{config.HOST}:{config.PORT}/api/")
    logger.info(f"Legacy Endpoints: http://{config.HOST}:{config.PORT}/analyze")
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
