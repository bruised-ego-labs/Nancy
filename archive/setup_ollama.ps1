# Nancy Ollama Setup Script
# Sets up the fourth brain: LinguisticBrain (Local LLM)

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Nancy Four-Brain Architecture: Ollama Setup" -ForegroundColor Cyan
Write-Host "Adding LinguisticBrain (Local Gemma) to Nancy" -ForegroundColor Cyan  
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`nStarting Nancy services with Ollama..." -ForegroundColor Yellow
docker-compose up -d

Write-Host "`nWaiting for Ollama service to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Test Ollama connectivity
Write-Host "`nTesting Ollama connectivity..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get -TimeoutSec 10
    Write-Host "Ollama service is running!" -ForegroundColor Green
} catch {
    Write-Host "Ollama not ready yet, waiting longer..." -ForegroundColor Yellow
    Start-Sleep -Seconds 20
}

Write-Host "`nPulling Gemma 2B model (this may take a few minutes)..." -ForegroundColor Yellow
Write-Host "Model size: ~1.6GB" -ForegroundColor Gray

$pullCommand = @{
    name = "gemma2:2b"
}

try {
    $response = Invoke-RestMethod -Uri "http://localhost:11434/api/pull" -Method Post -Body ($pullCommand | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 600
    Write-Host "Gemma 2B model downloaded successfully!" -ForegroundColor Green
} catch {
    Write-Host "Model pull failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Trying alternative approach..." -ForegroundColor Yellow
    
    # Alternative: Use docker exec
    docker-compose exec ollama ollama pull gemma2:2b
}

Write-Host "`nTesting Gemma model..." -ForegroundColor Yellow
$testPrompt = @{
    model = "gemma2:2b"
    prompt = "What is the purpose of a three-brain architecture in AI systems?"
    options = @{
        temperature = 0.1
    }
}

try {
    $testResponse = Invoke-RestMethod -Uri "http://localhost:11434/api/generate" -Method Post -Body ($testPrompt | ConvertTo-Json) -ContentType "application/json" -TimeoutSec 30
    Write-Host "Gemma model test successful!" -ForegroundColor Green
    Write-Host "Response preview: $($testResponse.response.Substring(0, [Math]::Min(100, $testResponse.response.Length)))..." -ForegroundColor White
} catch {
    Write-Host "Model test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nRestarting Nancy API to connect to Ollama..." -ForegroundColor Yellow
docker-compose restart api

Start-Sleep -Seconds 15

Write-Host "`nTesting Nancy integration with local LLM..." -ForegroundColor Yellow
try {
    $testIngestion = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "Nancy API is ready!" -ForegroundColor Green
    
    # Test document ingestion with local LLM
    Write-Host "`nTesting document ingestion with local Gemma..." -ForegroundColor Yellow
    
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $testContent = "This is a test document for Nancy's four-brain architecture. The thermal analysis shows significant improvements in heat dissipation. The electrical design requires careful consideration of power management."
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"test_local_llm.txt`"",
        "Content-Type: text/plain$LF",
        $testContent,
        "--$boundary",
        "Content-Disposition: form-data; name=`"author`"$LF",
        "Local LLM Test",
        "--$boundary--"
    )
    $body = $bodyLines -join $LF
    
    $ingestResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/ingest" -Method Post -Body $body -ContentType "multipart/form-data; boundary=`"$boundary`"" -TimeoutSec 60
    Write-Host "Document ingestion with local LLM successful!" -ForegroundColor Green
    Write-Host "Document ID: $($ingestResponse.doc_id)" -ForegroundColor White
    
} catch {
    Write-Host "Nancy integration test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "Nancy Four-Brain Architecture Setup Complete!" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`nActive Brains:" -ForegroundColor Yellow
Write-Host "1. VectorBrain (ChromaDB) - Semantic search" -ForegroundColor White
Write-Host "2. AnalyticalBrain (DuckDB) - Metadata queries" -ForegroundColor White  
Write-Host "3. RelationalBrain (Neo4j) - Knowledge graphs" -ForegroundColor White
Write-Host "4. LinguisticBrain (Ollama/Gemma) - Natural language processing" -ForegroundColor Green

Write-Host "`nService URLs:" -ForegroundColor Yellow
Write-Host "Nancy API: http://localhost:8000" -ForegroundColor White
Write-Host "ChromaDB: http://localhost:8001" -ForegroundColor White
Write-Host "Neo4j: http://localhost:7474" -ForegroundColor White
Write-Host "Ollama: http://localhost:11434" -ForegroundColor Green

Write-Host "`nTo test the system:" -ForegroundColor Yellow
Write-Host ".\test_enhanced_three_brain_demo.ps1" -ForegroundColor White

Write-Host "`nLocal LLM Benefits:" -ForegroundColor Green
Write-Host "✓ Zero token costs" -ForegroundColor White
Write-Host "✓ Complete privacy" -ForegroundColor White
Write-Host "✓ No rate limits" -ForegroundColor White
Write-Host "✓ Consistent performance" -ForegroundColor White