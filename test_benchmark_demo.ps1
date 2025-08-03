# Three-Brain Architecture Benchmark Demo
# This script demonstrates the superiority of Nancy's three-brain approach
# over standard RAG for multidisciplinary engineering teams

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Nancy Three-Brain Architecture Benchmark" -ForegroundColor Cyan  
Write-Host "Multidisciplinary Team Demonstration" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if Docker services are running
Write-Host "`nChecking Docker services..." -ForegroundColor Yellow
$dockerStatus = docker-compose ps --services --filter "status=running"

if ($dockerStatus -notcontains "api" -or $dockerStatus -notcontains "chromadb" -or $dockerStatus -notcontains "neo4j") {
    Write-Host "Starting Nancy services..." -ForegroundColor Yellow
    docker-compose up -d --build
    
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
    
    # Health check
    try {
        $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
        Write-Host "API service is ready!" -ForegroundColor Green
    }
    catch {
        Write-Host "Warning: API service may not be fully ready. Continuing..." -ForegroundColor Red
        Start-Sleep -Seconds 10
    }
}
else {
    Write-Host "Docker services are already running." -ForegroundColor Green
}

# Run the benchmark
Write-Host "`nStarting benchmark execution..." -ForegroundColor Yellow
Write-Host "This will compare Three-Brain vs Standard RAG across:" -ForegroundColor White
Write-Host "- Systems Engineering queries" -ForegroundColor Gray
Write-Host "- Mechanical Engineering queries" -ForegroundColor Gray  
Write-Host "- Electrical Engineering queries" -ForegroundColor Gray
Write-Host "- Firmware Engineering queries" -ForegroundColor Gray
Write-Host "- Industrial Design queries" -ForegroundColor Gray
Write-Host "- Project Management queries" -ForegroundColor Gray
Write-Host "- Cross-disciplinary queries" -ForegroundColor Gray

Write-Host "`nExecuting benchmark..." -ForegroundColor Yellow

try {
    # Change to Nancy directory and run benchmark
    Push-Location $PSScriptRoot
    
    # Run the Python benchmark script
    python run_benchmark.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=========================================" -ForegroundColor Green
        Write-Host "Benchmark completed successfully!" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Green
        
        Write-Host "`nNext Steps:" -ForegroundColor Cyan
        Write-Host "1. Review the detailed results JSON file" -ForegroundColor White
        Write-Host "2. Analyze discipline-specific improvements" -ForegroundColor White  
        Write-Host "3. Share results with stakeholders" -ForegroundColor White
        Write-Host "4. Consider expanding test dataset for your specific use case" -ForegroundColor White
        
        # Show recent benchmark results files
        Write-Host "`nRecent benchmark results:" -ForegroundColor Yellow
        Get-ChildItem -Path "." -Filter "benchmark_results_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3 | ForEach-Object {
            Write-Host "  $($_.Name)" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "Benchmark failed with exit code: $LASTEXITCODE" -ForegroundColor Red
    }
}
catch {
    Write-Host "Error running benchmark: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Pop-Location
}

Write-Host "`nBenchmark demo completed." -ForegroundColor Cyan