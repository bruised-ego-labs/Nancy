# Simple Nancy Benchmark Runner
Write-Host "Nancy Benchmark Starting..." -ForegroundColor Green

# Check if Nancy is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "Nancy API is ready" -ForegroundColor Green
} catch {
    Write-Host "Starting Nancy services..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep 30
}

# Run benchmark
Write-Host "Running benchmark..." -ForegroundColor Cyan
python automated_benchmark.py --run

Write-Host "Benchmark complete!" -ForegroundColor Green