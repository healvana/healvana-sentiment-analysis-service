# Healvana Sentiment Analysis API

### 🤖 LLM Based Analysis
- **Analysis Models**: Uses `waimoe/mental-health-sentiment-analysis-model` for accurate psychological sentiment detection
- **Multi-Modal Input**: Analyze both direct text and web page content via URL
- **Confidence Scoring**: Get confidence levels for all sentiment predictions
- **Chunked Processing**: Handles long texts by intelligently splitting into manageable chunks
- **GPU Acceleration**: Automatic GPU detection and utilization when available

## Quick Start

### Option 1: One-Click Setup (Recommended)
```bash
git clone https://github.com/healvana/healvana-sentiment-api.git
cd healvana-sentiment-api
./start_with_swagger.sh
```

### Option 2: Docker Deployment
```bash
git clone https://github.com/healvana/healvana-sentiment-api.git
cd healvana-sentiment-api
docker-compose up --build
```

### Option 3: Manual Setup
```bash
git clone https://github.com/healvana/healvana-sentiment-api.git
cd healvana-sentiment-api
pip install -r requirements.txt
python app.py
```

After starting the service, access:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs/
- **Health Check**: http://localhost:8000/health

## API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
Currently, no authentication is required. Rate limiting is applied based on IP address.

### Content Type
All API requests must use `Content-Type: application/json`

### Endpoints Overview

| Endpoint | Method | Description | Documentation |
|----------|--------|-------------|---------------|
| `/` | GET | Web interface | Interactive UI |
| `/docs/` | GET | Swagger documentation | API explorer |
| `/api/analysis` | POST | Sentiment analysis | Documented endpoint |
| `/api/health` | GET | Health check | System status |
| `/health` | GET | Legacy health check | Backward compatibility |
| `/analyze` | POST | Legacy analysis | Backward compatibility |
| `/api/info` | GET | API information | Service metadata |

## Usage Examples

### 📝 Text Analysis

**Web Interface:**
1. Navigate to `http://localhost:8000`
2. Select "Text Analysis"
3. Enter your text and click "Analyze Sentiment"

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "type": "text",
    "input": "I am feeling incredibly optimistic about my recovery journey!"
  }'
```

**Python Example:**
```python
import requests

response = requests.post('http://localhost:8000/api/analysis', json={
    'type': 'text',
    'input': 'I am feeling great about my mental health progress!'
})

result = response.json()
print(f"Sentiment: {result['prominent_sentiment']}")
print(f"Confidence: {result['confidence']:.2%}")
```

**JavaScript Example:**
```javascript
const response = await fetch('http://localhost:8000/api/analysis', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    type: 'text',
    input: 'I feel amazing today!'
  })
});

const result = await response.json();
console.log(`Sentiment: ${result.prominent_sentiment}`);
console.log(`Confidence: ${(result.confidence * 100).toFixed(1)}%`);
```

### 🔗 URL Analysis

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "type": "url",
    "input": "https://example.com/mental-health-article"
  }'
```

**Response Format:**
```json
{
  "model": "waimoe/mental-health-sentiment-analysis-model",
  "scores": {
    "positive": 0.8745,
    "negative": 0.0823,
    "neutral": 0.0432,
    "anxiety": 0.0123,
    "depression": 0.0087
  },
  "prominent_sentiment": "POSITIVE",
  "num_chunks": 3,
  "confidence": 0.8745,
  "request_id": "123e4567-e89b-12d3-a456-426614174000",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Model Configuration
MODEL_NAME=waimoe/mental-health-sentiment-analysis-model
CACHE_DIR=./models
MAX_TEXT_LENGTH=10000
CHUNK_SIZE=510

# URL Processing
URL_TIMEOUT=10
MAX_URL_SIZE=5242880

# Logging
LOG_LEVEL=INFO
```

### Configuration Options

| Variable | Description | Default | Production Value |
|----------|-------------|---------|------------------|
| `HOST` | Server bind address | `0.0.0.0` | `0.0.0.0` |
| `PORT` | Server port | `8000` | `8000` |
| `DEBUG` | Debug mode | `False` | `False` |
| `MODEL_NAME` | HuggingFace model | `waimoe/mental-health-sentiment-analysis-model` | Same |
| `CACHE_DIR` | Model cache directory | `./models` | `/app/models` |
| `MAX_TEXT_LENGTH` | Maximum text length | `10000` | `10000` |
| `CHUNK_SIZE` | Text chunk size | `510` | `510` |
| `URL_TIMEOUT` | URL request timeout | `10` | `10` |
| `MAX_URL_SIZE` | Max URL content size | `5242880` (5MB) | `5242880` |
| `LOG_LEVEL` | Logging level | `INFO` | `INFO` |

## Deployment

### Docker Deployment (Recommended)

**Production Docker Compose:**
```yaml
version: '3.8'
services:
  healvana-api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

**Deployment Commands:**
```bash
# Build and deploy
docker-compose up --build -d

# View logs
docker-compose logs -f

# Scale service
docker-compose up --scale healvana-api=3

# Stop service
docker-compose down
```

### Manual Production Deployment

**Using Gunicorn:**
```bash
# Install dependencies
pip install -r requirements.txt

# Start with Gunicorn
gunicorn -c gunicorn.conf.py app:app
```

**Systemd Service (Linux):**
```ini
[Unit]
Description=Healvana Sentiment Analysis API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/healvana-api
Environment=PATH=/opt/healvana-api/venv/bin
ExecStart=/opt/healvana-api/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Kubernetes Deployment

**Basic Kubernetes Manifest:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: healvana-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: healvana-api
  template:
    metadata:
      labels:
        app: healvana-api
    spec:
      containers:
      - name: healvana-api
        image: healvana/sentiment-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DEBUG
          value: "False"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: healvana-api-service
spec:
  selector:
    app: healvana-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Development

### Local Development Setup

```bash
# Clone repository
git clone https://github.com/your-username/healvana-sentiment-api.git
cd healvana-sentiment-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Start development server
python app.py
```

### Project Structure

```
healvana-sentiment-api/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── exceptions.py             # Custom exceptions
├── validator.py              # Input validation
├── text_extractor.py         # URL text extraction
├── sentiment_analyzer.py     # AI sentiment analysis
├── requirements.txt          # Python dependencies
├── gunicorn.conf.py         # Production server config
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service deployment
├── templates/
│   └── index.html          # Web interface
├── static/
│   ├── style.css           # Frontend styling
│   └── script.js           # Frontend JavaScript
├── logs/                   # Application logs
├── models/                 # AI model cache
├── scripts/
│   ├── start_with_swagger.sh
│   ├── test_swagger.sh
│   └── deploy.sh
└── README.md               # This file
```

### Code Style

The project follows Python best practices:
- **PEP 8** compliance for code formatting
- **Type hints** where applicable
- **Docstrings** for all functions and classes
- **Error handling** with custom exceptions
- **Logging** for debugging and monitoring

### Testing

**Manual Testing:**

**Load Testing:**
```bash
# Using Apache Bench
ab -n 100 -c 10 -T application/json -p test_data.json http://localhost:8000/api/analysis

# Using curl for health checks
curl -w "@curl-format.txt" -s http://localhost:8000/health
```

## API Reference

### POST /api/analysis

Analyze sentiment in text or web content.

**Request Body:**
```json
{
  "type": "text|url",
  "input": "content_to_analyze"
}
```

**Parameters:**
- `type` (string, required): Input type - either "text" or "url"
- `input` (string, required): Text content or URL to analyze

**Response:**
```json
{
  "model": "string",
  "scores": {
    "positive": 0.0,
    "negative": 0.0,
    "neutral": 0.0
  },
  "prominent_sentiment": "string",
  "num_chunks": 0,
  "confidence": 0.0,
  "request_id": "string",
  "timestamp": "string"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad request (validation error)
- `422` - Unprocessable entity (text extraction failed)
- `503` - Service unavailable (model error)

### GET /api/health

Check service health status.

**Response:**
```json
{
  "status": "healthy|unhealthy",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

**Status Codes:**
- `200` - Service is healthy
- `503` - Service is unhealthy

### GET /api/info

Get API information and usage examples.

**Response:**
```json
{
  "name": "Mental Health Sentiment Analysis API",
  "version": "1.0.0",
  "documentation": {
    "swagger_ui": "http://localhost:8000/docs/",
    "openapi_spec": "http://localhost:8000/swagger.json"
  },
  "endpoints": {...},
  "usage": {...}
}
```

## Error Handling

### Error Response Format

All errors follow a consistent format:

```json
{
  "error": "Error description",
  "request_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### Common Error Codes

| Code | Description | Common Causes |
|------|-------------|---------------|
| 400 | Bad Request | Invalid input format, missing required fields |
| 422 | Unprocessable Entity | URL extraction failed, content not accessible |
| 429 | Too Many Requests | Rate limit exceeded |
| 503 | Service Unavailable | Model loading failed, internal service error |
| 500 | Internal Server Error | Unexpected application error |

### Input Validation

**Text Input:**
- Maximum length: 10,000 characters
- XSS protection: Script tags removed
- Empty input validation

**URL Input:**
- Valid HTTP/HTTPS URLs only
- Content size limit: 5MB
- Request timeout: 10 seconds
- Basic SSRF protection

## Monitoring

### Health Checks

**Endpoints for Load Balancers:**
- `GET /health` - Basic health check
- `GET /api/health` - Detailed health status

**Health Check Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T12:00:00.000Z"
}
```

### Logging

**Log Levels:**
- `INFO` - Request/response logging
- `WARNING` - Validation errors, rate limits
- `ERROR` - Model errors, system failures
- `DEBUG` - Detailed debugging information

**Log Format:**
```
2025-01-01 12:00:00,000 - app - INFO - Request 123e4567: POST /api/analysis
2025-01-01 12:00:01,234 - app - INFO - Request 123e4567 completed in 1.234s - Status: 200
```

### Metrics

**Performance Metrics:**
- Request count and rate
- Response times (avg, p95, p99)
- Error rates by type
- Model inference times
- Memory and CPU usage

**Business Metrics:**
- Analysis requests by type (text vs URL)
- Sentiment distribution
- Confidence score distribution
- Request geographical distribution

## Performance

### Optimization Features

**Model Optimization:**
- GPU acceleration when available
- Model caching to avoid reloading
- Batch processing for multiple requests
- Text chunking for large inputs

**Response Optimization:**
- Gzip compression
- Efficient JSON serialization
- Minimal response payloads
- HTTP keep-alive connections

### Scaling Considerations

**Horizontal Scaling:**
- Stateless design enables easy scaling
- Load balancer health checks supported
- Container-ready for orchestration
- Shared model cache via volumes

**Vertical Scaling:**
- GPU acceleration support
- Configurable worker processes
- Memory-efficient model loading
- CPU optimization for inference

### Performance Benchmarks

**Typical Response Times:**
- Text analysis (< 1000 chars): 200-500ms
- Text analysis (1000-5000 chars): 500ms-1s
- URL analysis: 1-3s (depends on page size)
- Health check: < 50ms

**Throughput:**
- Single instance: 10-50 requests/second
- With GPU: 50-100 requests/second
- Concurrent processing: 4-8 workers

## Security

### Input Security

**Validation:**
- Input length limits
- URL format validation
- XSS protection
- Content type validation

**SSRF Protection:**
- Blocked localhost access
- URL scheme restrictions
- Content size limits
- Request timeouts

### Application Security

**Headers:**
- Request ID tracking
- CORS configuration
- Content-Type enforcement
- Error message sanitization

**Rate Limiting:**
- IP-based rate limiting
- Configurable limits
- Graceful degradation
- Clear error messages

## Contributing

### Development Workflow

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** following the code style guidelines
4. **Add tests** for new functionality
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Code Standards

- Follow PEP 8 for Python code formatting
- Add docstrings to all functions and classes
- Include type hints where appropriate
- Write clear, descriptive commit messages
- Update documentation for new features

### Testing Guidelines

- Test all new endpoints thoroughly
- Verify error handling scenarios
- Check edge cases and input validation
- Ensure backward compatibility
- Test deployment scenarios

## Troubleshooting

### Common Issues

**Model Loading Errors:**
```bash
# Clear model cache
rm -rf models/
python app.py  # Will re-download model
```

**Port Already in Use:**
```bash
# Find process using port 8000
lsof -i :8000
# Kill the process
kill -9 <PID>
```

**Memory Issues:**
```bash
# Check system memory
free -h
# Reduce worker processes in gunicorn.conf.py
workers = 2
```

**Container Issues:**
```bash
# Check container logs
docker-compose logs healvana-api

# Restart containers
docker-compose restart

# Rebuild containers
docker-compose up --build
```

### Debug Mode

Enable debug mode for development:

```bash
# Set environment variable
export DEBUG=True

# Or in .env file
DEBUG=True
```

**Debug Features:**
- Detailed error traces
- Auto-reload on code changes
- Enhanced logging
- Request debugging

### Log Analysis

**Find Errors:**
```bash
# Check recent errors
tail -f logs/app.log | grep ERROR

# Find specific request
grep "123e4567" logs/app.log
```

**Monitor Performance:**
```bash
# Response times
grep "completed in" logs/app.log | tail -20

# Health check status
curl -s http://localhost:8000/health | jq .
```

## FAQ

### General Questions

**Q: What types of sentiment can be detected?**
A: The API detects various mental health-related sentiments including positive, negative, neutral, anxiety, depression, and other psychological states depending on the model.

**Q: How accurate is the sentiment analysis?**
A: The model is specifically trained for mental health contexts and provides confidence scores. Accuracy varies based on text quality and context.

**Q: Can I use this for clinical purposes?**
A: This tool is for informational purposes only and should not be used as a substitute for professional mental health advice, diagnosis, or treatment.

### Technical Questions

**Q: What's the maximum text length?**
A: 10,000 characters by default, configurable via `MAX_TEXT_LENGTH` environment variable.

**Q: Does it support multiple languages?**
A: The current model is optimized for English text. Multi-language support may vary.

**Q: Can I run this without GPU?**
A: Yes, the API automatically detects available hardware and runs on CPU if GPU is not available.

**Q: How do I scale for high traffic?**
A: Use Docker containers with load balancers, increase worker processes, or deploy multiple instances.

### Deployment Questions

**Q: What are the minimum system requirements?**
A: 2GB RAM, 1 CPU core, 5GB disk space. GPU recommended for better performance.

**Q: How do I backup the model data?**
A: The models are cached in the `./models` directory. Back up this directory to preserve downloaded models.

**Q: Can I use a different sentiment analysis model?**
A: Yes, set the `MODEL_NAME` environment variable to any compatible HuggingFace model.