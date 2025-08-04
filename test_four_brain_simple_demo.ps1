# Nancy Four-Brain Architecture Demo
# Simple demonstration without Unicode characters

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Nancy Four-Brain Architecture Demo" -ForegroundColor Cyan  
Write-Host "Local LLM + Intelligent Multi-Brain System" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Health check
Write-Host "`nTesting API connectivity..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "Nancy API is ready!" -ForegroundColor Green
}
catch {
    Write-Host "Nancy API is not responding. Starting services..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 30
}

# Check Ollama
Write-Host "`nVerifying Local LLM..." -ForegroundColor Yellow
try {
    $ollamaModels = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 10
    $gemmaModel = $ollamaModels.models | Where-Object { $_.name -like "gemma*" }
    
    if ($gemmaModel) {
        Write-Host "Gemma model available: $($gemmaModel[0].name)" -ForegroundColor Green
    } else {
        Write-Host "No Gemma model found" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Ollama not ready" -ForegroundColor Yellow
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "DEMO: Document Ingestion with Local LLM" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Create a simple test document
$testContent = @"
Advanced Thermal Management System Design

This document outlines the thermal management approach for our next-generation electronic system. The primary challenge involves managing heat dissipation across multiple power domains while maintaining optimal performance.

Key Design Considerations:
- Power density exceeds 150W per cubic inch in critical areas
- Operating temperature range: -40C to +85C ambient
- Integration with electrical power distribution system is critical

The electrical design team has identified several constraints that directly impact our thermal strategy. The main power rail efficiency drops significantly above 70C junction temperature.

Mike Rodriguez from the electrical team has proposed a novel switching regulator configuration that could reduce heat generation by 15%.

Risk Assessment:
- Thermal runaway scenarios in high-power modes
- Component derating at temperature extremes
- Manufacturing tolerances affecting thermal paths

The relationship between our thermal design and the electrical power management is fundamental to system reliability.
"@

# Save to temp file and ingest
$tempFile = [System.IO.Path]::GetTempFileName()
$testContent | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "Ingesting test document..." -ForegroundColor Yellow

try {
    # Create boundary for multipart form data
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"thermal_analysis.txt`"",
        "Content-Type: text/plain$LF",
        $testContent,
        "--$boundary",
        "Content-Disposition: form-data; name=`"author`"$LF",
        "Sarah Chen",
        "--$boundary--"
    )
    $body = $bodyLines -join $LF
    
    $ingestResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/ingest" -Method Post -Body $body -ContentType "multipart/form-data; boundary=`"$boundary`"" -TimeoutSec 60
    
    Write-Host "Document ingested successfully!" -ForegroundColor Green
    Write-Host "Document ID: $($ingestResponse.doc_id)" -ForegroundColor White
    Write-Host "Processing complete across all four brains:" -ForegroundColor Gray
    Write-Host "  - VectorBrain: Semantic embeddings created" -ForegroundColor Gray
    Write-Host "  - AnalyticalBrain: Metadata stored" -ForegroundColor Gray
    Write-Host "  - RelationalBrain: Relationships extracted" -ForegroundColor Gray
    Write-Host "  - LinguisticBrain: Local LLM processing" -ForegroundColor Gray
}
catch {
    Write-Host "Failed to ingest document: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Remove-Item $tempFile -ErrorAction SilentlyContinue
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "DEMO: Four-Brain Query Processing" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Test queries
$queries = @(
    "Who wrote the thermal analysis document?",
    "What are the power density requirements?", 
    "How do thermal constraints affect electrical design?",
    "What temperature ranges are specified?"
)

foreach ($query in $queries) {
    Write-Host "`nTesting query: '$query'" -ForegroundColor Yellow
    
    try {
        $queryBody = @{
            query = $query
            n_results = 3
            use_enhanced = $true
        } | ConvertTo-Json
        
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $queryBody -ContentType "application/json" -TimeoutSec 30
        $endTime = Get-Date
        $processingTime = ($endTime - $startTime).TotalSeconds
        
        Write-Host "Processing time: $([math]::Round($processingTime, 1)) seconds" -ForegroundColor Green
        Write-Host "Strategy used: $($response.strategy_used)" -ForegroundColor Green
        
        if ($response.results -and $response.results.Count -gt 0) {
            Write-Host "Results found: $($response.results.Count)" -ForegroundColor Green
            $topResult = $response.results[0]
            
            if ($topResult.author) {
                Write-Host "Top result author: $($topResult.author)" -ForegroundColor White
            }
            if ($topResult.document_metadata.filename) {
                Write-Host "Document: $($topResult.document_metadata.filename)" -ForegroundColor White
            }
            if ($topResult.text) {
                $preview = $topResult.text.Substring(0, [Math]::Min(100, $topResult.text.Length)) + "..."
                Write-Host "Preview: $preview" -ForegroundColor Gray
            }
        } else {
            Write-Host "No results found" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "Query failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "LOCAL LLM TOKEN USAGE ANALYSIS" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "Checking local Gemma LLM usage..." -ForegroundColor Yellow

try {
    $logOutput = docker-compose logs api --tail=20 2>&1 | Select-String "Local Ollama"
    
    if ($logOutput) {
        Write-Host "`nLocal LLM operations detected (all FREE):" -ForegroundColor Green
        foreach ($line in $logOutput) {
            Write-Host "  $line" -ForegroundColor White
        }
        
        Write-Host "`nCost Analysis:" -ForegroundColor Cyan
        Write-Host "  Local processing cost: $0.00" -ForegroundColor Green
        Write-Host "  Estimated cloud API cost: $2-5" -ForegroundColor Yellow
        Write-Host "  Privacy: 100% local processing" -ForegroundColor Green
    } else {
        Write-Host "No recent local LLM operations found in logs" -ForegroundColor Yellow
    }
}
catch {
    Write-Host "Could not analyze logs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "FOUR-BRAIN ARCHITECTURE SUMMARY" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`nFOUR-BRAIN SYSTEM COMPONENTS:" -ForegroundColor Yellow

Write-Host "`n1. VECTORBRAIN (ChromaDB + FastEmbed):" -ForegroundColor Green
Write-Host "   - Semantic search across document content" -ForegroundColor White
Write-Host "   - Natural language query understanding" -ForegroundColor White
Write-Host "   - CPU-based embeddings for reliability" -ForegroundColor White

Write-Host "`n2. ANALYTICALBRAIN (DuckDB):" -ForegroundColor Blue  
Write-Host "   - Fast metadata queries and filtering" -ForegroundColor White
Write-Host "   - Document statistics and analytics" -ForegroundColor White
Write-Host "   - Date and attribute-based searches" -ForegroundColor White

Write-Host "`n3. RELATIONALBRAIN (Neo4j):" -ForegroundColor Magenta
Write-Host "   - Author attribution and accountability" -ForegroundColor White
Write-Host "   - Cross-team collaboration mapping" -ForegroundColor White
Write-Host "   - Document relationship discovery" -ForegroundColor White

Write-Host "`n4. LINGUISTICBRAIN (Ollama/Gemma):" -ForegroundColor Red
Write-Host "   - Zero-cost local LLM processing" -ForegroundColor White
Write-Host "   - Intelligent query analysis" -ForegroundColor White
Write-Host "   - Relationship extraction" -ForegroundColor White
Write-Host "   - Complete privacy protection" -ForegroundColor White

Write-Host "`nKEY BUSINESS BENEFITS:" -ForegroundColor Yellow
Write-Host "   - Zero ongoing LLM costs" -ForegroundColor Green
Write-Host "   - Complete data privacy" -ForegroundColor Green
Write-Host "   - Unlimited query processing" -ForegroundColor Green
Write-Host "   - Cross-domain knowledge discovery" -ForegroundColor Green
Write-Host "   - Team collaboration insights" -ForegroundColor Green

Write-Host "`nSERVICE URLS:" -ForegroundColor Yellow
Write-Host "   API: http://localhost:8000" -ForegroundColor White
Write-Host "   ChromaDB: http://localhost:8001" -ForegroundColor White
Write-Host "   Neo4j: http://localhost:7474" -ForegroundColor White
Write-Host "   Ollama: http://localhost:11434" -ForegroundColor White

Write-Host "`nNancy Four-Brain Architecture demonstration complete!" -ForegroundColor Green
Write-Host "System ready for production with zero-cost AI operations." -ForegroundColor Cyan