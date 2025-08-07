# Nancy Benchmark Runner - PowerShell Script
# Automated execution of the complete benchmark suite

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Nancy Four-Brain Architecture Benchmark" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Check if Nancy services are running
Write-Host "Checking Nancy services..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
    Write-Host "Nancy services are running." -ForegroundColor Green
}
catch {
    Write-Host "Nancy services not running. Starting..." -ForegroundColor Yellow
    docker-compose up -d
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Verify all services are healthy
Write-Host "Verifying service health..." -ForegroundColor Yellow
$services = @(
    'http://localhost:8000/health',
    'http://localhost:8001',
    'http://localhost:11434'
)

foreach ($service in $services) {
    try {
        Invoke-RestMethod -Uri $service -Method Get -TimeoutSec 5 | Out-Null
        Write-Host "✓ $service is responding" -ForegroundColor Green
    }
    catch {
        Write-Host "✗ $service is not responding" -ForegroundColor Red
        exit 1
    }
}

# Check Python dependencies
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
try {
    python -c "import requests, chromadb, numpy" 2>$null
    Write-Host "✓ Python dependencies available" -ForegroundColor Green
}
catch {
    Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
    pip install requests chromadb numpy
}

# Run the benchmark
Write-Host "Starting benchmark execution..." -ForegroundColor Cyan
python automated_benchmark.py --run

Write-Host "Benchmark completed!" -ForegroundColor Green
Write-Host "Check the benchmark_results/ directory for detailed reports." -ForegroundColor White