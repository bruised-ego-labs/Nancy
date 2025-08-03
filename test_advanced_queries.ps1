# Advanced Query Tests for Nancy Project
# Demonstrates intelligent use of all three databases

# Query Type 1: Content-Focused (Vector Brain Primary)
$query1 = @{
    "query" = "the hidden tax of context-switching"
    "n_results" = 5
} | ConvertTo-Json

Write-Host "=== TEST 1: Content-Focused Query (Vector Brain Primary) ===" -ForegroundColor Green
Write-Host "Query: 'the hidden tax of context-switching'"
Write-Host "Expected: Should find semantic matches in README.md, use vector search first"

try {
    $response1 = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $query1 -ContentType "application/json"
    Write-Host "Strategy Used: $($response1.strategy_used)" -ForegroundColor Yellow
    Write-Host "Results Count: $($response1.results.Count)" -ForegroundColor Yellow
    Write-Host "Top Result Author: $($response1.results[0].author)" -ForegroundColor Yellow
    Write-Host "Top Result Distance: $($response1.results[0].distance)" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host "Error in Test 1: $($_.Exception.Message)" -ForegroundColor Red
}

# Query Type 2: Author-Focused (Relational Brain Primary)
$query2 = @{
    "query" = "documents by Scott"
    "n_results" = 10
} | ConvertTo-Json

Write-Host "=== TEST 2: Author-Focused Query (Relational Brain Primary) ===" -ForegroundColor Green
Write-Host "Query: 'documents by Scott'"
Write-Host "Expected: Should start with Neo4j, find Scott's documents, then search within them"

try {
    $response2 = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $query2 -ContentType "application/json"
    Write-Host "Strategy Used: $($response2.strategy_used)" -ForegroundColor Yellow
    Write-Host "Results Count: $($response2.results.Count)" -ForegroundColor Yellow
    if ($response2.results.Count -gt 0) {
        Write-Host "All results by Scott: $(($response2.results | ForEach-Object { $_.author -eq 'Scott' } | Measure-Object).Count)" -ForegroundColor Yellow
    }
    Write-Host ""
} catch {
    Write-Host "Error in Test 2: $($_.Exception.Message)" -ForegroundColor Red
}

# Query Type 3: Temporal-Focused (Analytical Brain Primary)
$query3 = @{
    "query" = "recent documents about architecture"
    "n_results" = 8
} | ConvertTo-Json

Write-Host "=== TEST 3: Temporal-Focused Query (Analytical Brain Primary) ===" -ForegroundColor Green
Write-Host "Query: 'recent documents about architecture'"
Write-Host "Expected: Should start with DuckDB time filtering, then vector search within recent docs"

try {
    $response3 = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $query3 -ContentType "application/json"
    Write-Host "Strategy Used: $($response3.strategy_used)" -ForegroundColor Yellow
    Write-Host "Results Count: $($response3.results.Count)" -ForegroundColor Yellow
    if ($response3.results.Count -gt 0) {
        Write-Host "Recent Documents Found: $(($response3.results | Select-Object -Property @{Name='filename'; Expression={$_.document_metadata.filename}} | Sort-Object filename -Unique).Count)" -ForegroundColor Yellow
    }
    Write-Host ""
} catch {
    Write-Host "Error in Test 3: $($_.Exception.Message)" -ForegroundColor Red
}

# Query Type 4: Relationship Exploration (Graph Brain Primary)
$query4 = @{
    "query" = "show me related documents to the three-brain architecture"
    "n_results" = 10
} | ConvertTo-Json

Write-Host "=== TEST 4: Relationship Exploration Query (Graph Brain Primary) ===" -ForegroundColor Green
Write-Host "Query: 'show me related documents to the three-brain architecture'"
Write-Host "Expected: Should find relevant docs, then explore author connections and related works"

try {
    $response4 = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $query4 -ContentType "application/json"
    Write-Host "Strategy Used: $($response4.strategy_used)" -ForegroundColor Yellow
    Write-Host "Results Count: $($response4.results.Count)" -ForegroundColor Yellow
    if ($response4.related_authors) {
        Write-Host "Related Authors Found: $($response4.related_authors -join ', ')" -ForegroundColor Yellow
    }
    if ($response4.explored_connections) {
        Write-Host "Connections Explored: $($response4.explored_connections)" -ForegroundColor Yellow
    }
    Write-Host ""
} catch {
    Write-Host "Error in Test 4: $($_.Exception.Message)" -ForegroundColor Red
}

# Query Type 5: Analytical Query (Counting and Statistics)
$query5 = @{
    "query" = "how many documents has Scott written"
    "n_results" = 5
} | ConvertTo-Json

Write-Host "=== TEST 5: Analytical Query (Statistics Focus) ===" -ForegroundColor Green
Write-Host "Query: 'how many documents has Scott written'"
Write-Host "Expected: Should use analytical brain to count and provide statistics"

try {
    $response5 = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $query5 -ContentType "application/json"
    Write-Host "Strategy Used: $($response5.strategy_used)" -ForegroundColor Yellow
    Write-Host "Results Count: $($response5.results.Count)" -ForegroundColor Yellow
    
    # Count unique documents by Scott
    $scottDocs = $response5.results | Where-Object { $_.author -eq "Scott" } | Select-Object -ExpandProperty document_metadata | Select-Object -ExpandProperty filename | Sort-Object -Unique
    Write-Host "Unique Documents by Scott: $($scottDocs.Count)" -ForegroundColor Yellow
    Write-Host "Scott's Documents: $($scottDocs -join ', ')" -ForegroundColor Yellow
    Write-Host ""
} catch {
    Write-Host "Error in Test 5: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "=== SUMMARY OF THREE-BRAIN DEMONSTRATION ===" -ForegroundColor Cyan
Write-Host "The tests above demonstrate how Nancy intelligently routes queries to different database strategies:"
Write-Host "1. Vector Brain: For semantic content search" -ForegroundColor White
Write-Host "2. Analytical Brain: For time-based queries and statistics" -ForegroundColor White  
Write-Host "3. Relational Brain: For author/relationship queries" -ForegroundColor White
Write-Host "4. Graph Exploration: For discovering connections between documents and people" -ForegroundColor White
Write-Host "5. Hybrid Approach: When multiple strategies are needed" -ForegroundColor White
