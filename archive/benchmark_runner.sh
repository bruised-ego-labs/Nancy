#!/bin/bash
# Nancy Benchmark Runner Script
# Automated execution of the complete benchmark suite

set -e

echo "=========================================="
echo "Nancy Four-Brain Architecture Benchmark"
echo "=========================================="

# Check if Nancy services are running
echo "Checking Nancy services..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Nancy services not running. Starting..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 30
else
    echo "Nancy services are running."
fi

# Verify all services are healthy
echo "Verifying service health..."
services=("http://localhost:8000/health" "http://localhost:8001" "http://localhost:11434")
for service in "${services[@]}"; do
    if curl -s "$service" > /dev/null; then
        echo "✓ $service is responding"
    else
        echo "✗ $service is not responding"
        exit 1
    fi
done

# Install Python dependencies if needed
if ! python3 -c "import requests, chromadb" 2>/dev/null; then
    echo "Installing Python dependencies..."
    pip3 install requests chromadb numpy
fi

# Run the benchmark
echo "Starting benchmark execution..."
python3 run_benchmark.py --config benchmark_config.json

echo "Benchmark completed!"
echo "Check the benchmark_results/ directory for detailed reports."