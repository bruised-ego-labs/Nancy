#!/usr/bin/env pwsh
# Test the Nancy vs Baseline RAG Comparison

Write-Host "🔍 Nancy vs Baseline RAG Performance Comparison" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green

# Check if both systems are running
Write-Host "Checking system availability..." -ForegroundColor Yellow

$nancyHealth = $null
$baselineHealth = $null

try {
    $nancyHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✅ Nancy (port 8000): Available" -ForegroundColor Green
} catch {
    Write-Host "❌ Nancy (port 8000): Not available" -ForegroundColor Red
    Write-Host "   Start Nancy with: docker-compose up -d" -ForegroundColor Yellow
}

try {
    $baselineHealth = Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 5  
    Write-Host "✅ Baseline (port 8001): Available" -ForegroundColor Green
} catch {
    Write-Host "❌ Baseline (port 8001): Not available" -ForegroundColor Red
    Write-Host "   Start Baseline with: .\run_baseline_rag.ps1" -ForegroundColor Yellow
}

if (-not $nancyHealth -or -not $baselineHealth) {
    Write-Host ""
    Write-Host "⚠️  Cannot run comparison - both systems must be available" -ForegroundColor Red
    Write-Host "Please start the missing system(s) and try again." -ForegroundColor Yellow
    exit 1
}

# Ensure both systems have data
Write-Host ""
Write-Host "Ensuring both systems have test data..." -ForegroundColor Yellow

# Ingest data into Nancy (if not already done)
try {
    Write-Host "Checking Nancy data status..." -ForegroundColor Cyan
    $nancyQuery = @{ query = "test" } | ConvertTo-Json
    $nancyResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $nancyQuery -ContentType "application/json"
    Write-Host "✅ Nancy has data" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Nancy may need data ingestion" -ForegroundColor Yellow
    Write-Host "   Consider running: .\test_upload_2.ps1" -ForegroundColor Cyan
}

# Ingest data into Baseline
try {
    Write-Host "Ingesting data into Baseline system..." -ForegroundColor Cyan
    $baselineIngest = Invoke-RestMethod -Uri "http://localhost:8001/api/ingest" -Method Post
    Write-Host "✅ Baseline data ingestion complete" -ForegroundColor Green
    Write-Host "   Files processed: $($baselineIngest.details.files_processed)" -ForegroundColor Cyan
    Write-Host "   Chunks created: $($baselineIngest.details.chunks_created)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Baseline data ingestion failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Run the comparison
Write-Host ""
Write-Host "🚀 Starting comprehensive comparison..." -ForegroundColor Green
Write-Host ""

python compare_nancy_vs_baseline.py

Write-Host ""
Write-Host "✅ Comparison complete!" -ForegroundColor Green
Write-Host "Check the generated JSON file for detailed results." -ForegroundColor Cyan