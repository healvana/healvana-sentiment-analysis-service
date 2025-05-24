#!/bin/bash

echo "🚀 Deploying Sentiment Analysis API..."

# Build and run with Docker
if command -v docker &> /dev/null; then
    echo "Using Docker..."
    docker-compose down 2>/dev/null || true
    docker-compose up --build -d
    
    echo "Waiting for service..."
    sleep 10
    
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo "✅ API is running at http://localhost:8000"
        echo "📋 Test with:"
        echo "curl -X POST http://localhost:8000/analyze -H 'Content-Type: application/json' -d '{\"type\":\"text\",\"input\":\"I feel great today!\"}'"
    else
        echo "❌ Deployment failed"
        docker-compose logs
    fi
else
    echo "Docker not found. Running locally..."
    pip install -r requirements.txt
    python app.py
fi
