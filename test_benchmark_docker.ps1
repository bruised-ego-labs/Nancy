# Three-Brain Architecture Benchmark Demo (Docker Version)
# This script runs the benchmark inside the Docker container with all dependencies

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Nancy Three-Brain Architecture Benchmark" -ForegroundColor Cyan  
Write-Host "Multidisciplinary Team Demonstration" -ForegroundColor Cyan
Write-Host "(Docker Container Execution)" -ForegroundColor Cyan
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

# Copy benchmark test data into the container
Write-Host "`nCopying benchmark test data to container..." -ForegroundColor Yellow

# Create the benchmark_test_data directory in the container
docker exec nancy-api-1 mkdir -p /app/data/benchmark_test_data

# Copy each test data file to the container
$testFiles = Get-ChildItem -Path "benchmark_test_data" -Filter "*.txt"
foreach ($file in $testFiles) {
    Write-Host "Copying $($file.Name)..." -ForegroundColor Gray
    docker cp "benchmark_test_data\$($file.Name)" nancy-api-1:/app/data/benchmark_test_data/
}

# Copy the benchmark script to the container
Write-Host "Copying benchmark script to container..." -ForegroundColor Yellow
docker cp "run_benchmark_docker.py" nancy-api-1:/app/run_benchmark.py

Write-Host "`nStarting benchmark execution..." -ForegroundColor Yellow
Write-Host "This will compare Three-Brain vs Standard RAG across:" -ForegroundColor White
Write-Host "- Systems Engineering queries" -ForegroundColor Gray
Write-Host "- Mechanical Engineering queries" -ForegroundColor Gray  
Write-Host "- Electrical Engineering queries" -ForegroundColor Gray
Write-Host "- Firmware Engineering queries" -ForegroundColor Gray
Write-Host "- Industrial Design queries" -ForegroundColor Gray
Write-Host "- Project Management queries" -ForegroundColor Gray
Write-Host "- Cross-disciplinary queries" -ForegroundColor Gray

Write-Host "`nExecuting benchmark inside Docker container..." -ForegroundColor Yellow

try {
    # Run the benchmark inside the Docker container
    $benchmarkResult = docker exec nancy-api-1 python3 /app/run_benchmark.py
    
    # Display the results
    Write-Host $benchmarkResult -ForegroundColor White
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n=========================================" -ForegroundColor Green
        Write-Host "Benchmark completed successfully!" -ForegroundColor Green
        Write-Host "=========================================" -ForegroundColor Green
        
        # Copy results back to host
        Write-Host "`nCopying results back to host..." -ForegroundColor Yellow
        $resultsFiles = docker exec nancy-api-1 find /app/data -name "benchmark_results_*.json" -type f
        
        foreach ($resultFile in $resultsFiles) {
            if ($resultFile.Trim()) {
                $fileName = Split-Path $resultFile.Trim() -Leaf
                docker cp "nancy-api-1:$($resultFile.Trim())" "./$fileName"
                Write-Host "Copied $fileName to current directory" -ForegroundColor Green
            }
        }
        
        Write-Host "`nNext Steps:" -ForegroundColor Cyan
        Write-Host "1. Review the detailed results JSON file" -ForegroundColor White
        Write-Host "2. Analyze discipline-specific improvements" -ForegroundColor White  
        Write-Host "3. Share results with stakeholders" -ForegroundColor White
        Write-Host "4. Consider expanding test dataset for your specific use case" -ForegroundColor White
        
        # Show copied results files
        Write-Host "`nBenchmark results files:" -ForegroundColor Yellow
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
    Write-Host "Docker container logs:" -ForegroundColor Yellow
    docker logs nancy-api-1 --tail 50
}

Write-Host "`nBenchmark demo completed." -ForegroundColor Cyan