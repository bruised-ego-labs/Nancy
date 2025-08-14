# Comprehensive Nancy Spreadsheet Ingestion Test Runner
# This script runs comprehensive tests for Nancy's four-brain spreadsheet capabilities

Write-Host "Nancy Comprehensive Spreadsheet Ingestion Test Suite" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan

# Check if Docker services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
try {
    $dockerStatus = docker-compose ps 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker Compose not available. Starting services..." -ForegroundColor Yellow
        docker-compose up -d --build
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Failed to start Docker services" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "Docker services are running" -ForegroundColor Green
    }
} catch {
    Write-Host "WARNING: Could not check Docker status" -ForegroundColor Yellow
}

# Wait for services to be ready
Write-Host "Waiting for Nancy API to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$nancy_ready = $false

while ($attempt -lt $maxAttempts -and -not $nancy_ready) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5
        if ($response) {
            $nancy_ready = $true
            Write-Host "Nancy API is ready!" -ForegroundColor Green
        }
    } catch {
        $attempt++
        Write-Host "Attempt $attempt/$maxAttempts - Waiting for Nancy API..." -ForegroundColor Yellow
        Start-Sleep -Seconds 2
    }
}

if (-not $nancy_ready) {
    Write-Host "ERROR: Nancy API failed to start within timeout" -ForegroundColor Red
    exit 1
}

# Run the comprehensive test suite
Write-Host "Starting comprehensive spreadsheet ingestion tests..." -ForegroundColor Cyan
try {
    python comprehensive_spreadsheet_test.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Tests completed successfully!" -ForegroundColor Green
    } else {
        Write-Host "Tests completed with errors. Check the output above." -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: Failed to run test suite: $_" -ForegroundColor Red
    exit 1
}

# Show recent test results
Write-Host "`nRecent test result files:" -ForegroundColor Cyan
Get-ChildItem -Filter "nancy_spreadsheet_test_results_*.json" | 
    Sort-Object LastWriteTime -Descending | 
    Select-Object -First 3 | 
    ForEach-Object { Write-Host "  $($_.Name)" -ForegroundColor Yellow }

Write-Host "`nTest suite execution complete!" -ForegroundColor Green