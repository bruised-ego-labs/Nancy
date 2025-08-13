# Enhanced Three-Brain Architecture Demo - Simple Version
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Nancy Enhanced Three-Brain Architecture Demo" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan

# Check if API is running
Write-Host "`nTesting API connectivity..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "API is ready!" -ForegroundColor Green
}
catch {
    Write-Host "API is not responding. Starting services..." -ForegroundColor Red
    docker-compose up -d --build
    Start-Sleep -Seconds 30
}

# Demo queries
$queries = @(
    "Who wrote the thermal analysis document?",
    "Show me documents from March about power consumption", 
    "What thermal issues affected electrical design?",
    "Find all documents that mention power management"
)

foreach ($query in $queries) {
    Write-Host "`n" + "="*60 -ForegroundColor DarkCyan
    Write-Host "Testing: $query" -ForegroundColor Yellow
    Write-Host "-"*60 -ForegroundColor DarkCyan
    
    try {
        # Test query strategy
        $strategyBody = @{
            query = $query
            n_results = 5
        } | ConvertTo-Json
        
        $strategy = Invoke-RestMethod -Uri "http://localhost:8000/api/query/test-strategy" -Method Post -Body $strategyBody -ContentType "application/json" -TimeoutSec 30
        Write-Host "Strategy: $($strategy.predicted_strategy.type)" -ForegroundColor Green
        Write-Host "Primary Brain: $($strategy.predicted_strategy.primary_brain)" -ForegroundColor Green
        
        # Execute enhanced query
        $queryBody = @{
            query = $query
            n_results = 5
            use_enhanced = $true
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $queryBody -ContentType "application/json" -TimeoutSec 30
        
        Write-Host "Processing: $($response.metadata.processing_method)" -ForegroundColor Green
        Write-Host "Brains Used: $($response.metadata.brains_used -join ', ')" -ForegroundColor Green
        Write-Host "Results: $($response.metadata.result_count)" -ForegroundColor Green
        
        if ($response.natural_response) {
            Write-Host "Response: $($response.natural_response)" -ForegroundColor White
        }
        
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nDemo completed!" -ForegroundColor Green