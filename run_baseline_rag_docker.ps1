#!/usr/bin/env pwsh
# Start the LangChain + ChromaDB Baseline RAG System in Docker

Write-Host "Starting Baseline RAG System (Docker)..." -ForegroundColor Green
Write-Host "Framework: LangChain + ChromaDB + Ollama/Gemma" -ForegroundColor Cyan

# Build and start the baseline RAG service
Write-Host "Building and starting baseline RAG container..." -ForegroundColor Yellow
docker-compose up -d --build baseline-rag

# Wait for services to be ready
Write-Host "Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

# Check if baseline service is running
Write-Host "Checking baseline service status..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8002/health" -UseBasicParsing
    $healthData = $response.Content | ConvertFrom-Json
    
    if ($healthData.status -eq "ok" -and $healthData.rag_initialized) {
        Write-Host "Baseline RAG System is running successfully!" -ForegroundColor Green
        Write-Host "API available at: http://localhost:8002" -ForegroundColor Cyan
        Write-Host "Health check: http://localhost:8002/health" -ForegroundColor Cyan
        Write-Host "System info: http://localhost:8002/api/info" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "Available endpoints:" -ForegroundColor Yellow
        Write-Host "  POST /api/ingest  - Ingest benchmark data" -ForegroundColor White
        Write-Host "  POST /api/query   - Query the system" -ForegroundColor White
        Write-Host "  GET  /api/info    - System information" -ForegroundColor White
        Write-Host "  GET  /health      - Health check" -ForegroundColor White
        
    } else {
        Write-Host "Service started but RAG system not initialized properly" -ForegroundColor Yellow
        Write-Host "Response: $($response.Content)" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "Failed to connect to baseline service" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Checking container logs..." -ForegroundColor Yellow
    docker-compose logs baseline-rag --tail=20
}