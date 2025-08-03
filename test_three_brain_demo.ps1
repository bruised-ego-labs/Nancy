# Comprehensive Three-Brain Demonstration Script
# Shows how Nancy intelligently uses Vector, Analytical, and Relational databases

param(
    [string]$ApiUrl = "http://localhost:8000/api"
)

Write-Host "🧠🧠🧠 NANCY THREE-BRAIN INTELLIGENCE DEMONSTRATION 🧠🧠🧠" -ForegroundColor Magenta
Write-Host "=========================================================" -ForegroundColor Magenta
Write-Host ""

# Function to make API calls and display results nicely
function Test-NancyQuery {
    param(
        [string]$TestName,
        [string]$Query,
        [string]$ExpectedStrategy,
        [string]$Description,
        [int]$ResultCount = 5
    )
    
    Write-Host "🔍 $TestName" -ForegroundColor Cyan
    Write-Host "Query: '$Query'" -ForegroundColor White
    Write-Host "Expected Strategy: $ExpectedStrategy" -ForegroundColor Yellow
    Write-Host "Description: $Description" -ForegroundColor Gray
    Write-Host ""
    
    $queryBody = @{
        "query" = $Query
        "n_results" = $ResultCount
        "use_enhanced" = $true
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$ApiUrl/query" -Method Post -Body $queryBody -ContentType "application/json"
        
        Write-Host "✅ RESULTS:" -ForegroundColor Green
        Write-Host "   Strategy Used: $($response.strategy_used)" -ForegroundColor Yellow
        Write-Host "   Primary Brain: $($response.intent.primary_brain)" -ForegroundColor Yellow
        Write-Host "   Query Type: $($response.intent.type)" -ForegroundColor Yellow
        Write-Host "   Focus: $($response.intent.focus)" -ForegroundColor Yellow
        Write-Host "   Results Found: $($response.results.Count)" -ForegroundColor Yellow
        
        if ($response.results.Count -gt 0) {
            Write-Host "   Top Result:" -ForegroundColor White
            Write-Host "     - Document: $($response.results[0].document_metadata.filename)" -ForegroundColor White
            Write-Host "     - Author: $($response.results[0].author)" -ForegroundColor White
            Write-Host "     - Distance: $([math]::Round($response.results[0].distance, 4))" -ForegroundColor White
            Write-Host "     - Text Preview: $($response.results[0].text.Substring(0, [Math]::Min(100, $response.results[0].text.Length)))..." -ForegroundColor Gray
        }
        
        if ($response.related_authors) {
            Write-Host "   Related Authors: $($response.related_authors -join ', ')" -ForegroundColor Cyan
        }
        
        if ($response.explored_connections) {
            Write-Host "   Connections Explored: $($response.explored_connections)" -ForegroundColor Cyan
        }
        
        # Count unique documents and authors
        $uniqueDocs = $response.results | Select-Object -ExpandProperty document_metadata | Select-Object -ExpandProperty filename | Sort-Object -Unique
        $uniqueAuthors = $response.results | Select-Object -ExpandProperty author | Sort-Object -Unique
        Write-Host "   Unique Documents: $($uniqueDocs.Count)" -ForegroundColor White
        Write-Host "   Unique Authors: $($uniqueAuthors.Count)" -ForegroundColor White
        
    } catch {
        Write-Host "❌ ERROR: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "─────────────────────────────────────────────────────────" -ForegroundColor DarkGray
    Write-Host ""
}

# Test 1: Vector Brain Primary - Semantic Content Search
Test-NancyQuery -TestName "TEST 1: VECTOR BRAIN PRIMARY" `
    -Query "the hidden tax of context-switching" `
    -ExpectedStrategy "Hybrid/Vector-First" `
    -Description "Semantic search for conceptual content. Should find README.md content about context-switching costs."

# Test 2: Relational Brain Primary - Author-Focused Query  
Test-NancyQuery -TestName "TEST 2: RELATIONAL BRAIN PRIMARY" `
    -Query "documents written by Scott" `
    -ExpectedStrategy "Relationship-First" `
    -Description "Author-focused query. Should start with Neo4j to find Scott's documents, then search within them."

# Test 3: Analytical Brain Primary - Temporal Query
Test-NancyQuery -TestName "TEST 3: ANALYTICAL BRAIN PRIMARY" `
    -Query "recent documents about performance" `
    -ExpectedStrategy "Analytical-First" `
    -Description "Time-based query. Should use DuckDB to filter recent documents, then vector search within them."

# Test 4: Graph Exploration - Relationship Discovery
Test-NancyQuery -TestName "TEST 4: GRAPH EXPLORATION" `
    -Query "show me documents related to Sarah Johnson's work" `
    -ExpectedStrategy "Graph-Exploration" `
    -Description "Relationship exploration. Should find Sarah's docs, then explore connected authors and related documents."

# Test 5: Analytical Focus - Statistics and Counting
Test-NancyQuery -TestName "TEST 5: ANALYTICAL FOCUS" `
    -Query "how many documents mention architecture" `
    -ExpectedStrategy "Analytical-Primary" `
    -Description "Statistical query. Should use analytical brain for counting and metadata analysis."

# Test 6: Complex Hybrid Query
Test-NancyQuery -TestName "TEST 6: COMPLEX HYBRID QUERY" `
    -Query "who participated in architecture discussions and what were the key decisions" `
    -ExpectedStrategy "Graph-Exploration or Hybrid" `
    -Description "Complex query requiring all three brains: vector for 'architecture decisions', graph for 'who participated', analytical for organizing results."

# Test 7: People and Relationship Focus
Test-NancyQuery -TestName "TEST 7: PEOPLE & RELATIONSHIPS" `
    -Query "what other documents has the author of the performance report written" `
    -ExpectedStrategy "Relationship-First" `
    -Description "Should identify Sarah Johnson from performance report, then find her other documents via Neo4j relationships."

Write-Host "🎯 THREE-BRAIN INTELLIGENCE SUMMARY" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Nancy's Enhanced Query Orchestrator demonstrates:" -ForegroundColor White
Write-Host ""
Write-Host "🧠 VECTOR BRAIN (ChromaDB):" -ForegroundColor Green
Write-Host "   ✓ Semantic similarity search" -ForegroundColor White
Write-Host "   ✓ Conceptual content discovery" -ForegroundColor White
Write-Host "   ✓ Finds relevant text even without exact keyword matches" -ForegroundColor White
Write-Host ""
Write-Host "🧠 ANALYTICAL BRAIN (DuckDB):" -ForegroundColor Green  
Write-Host "   ✓ Time-based filtering and queries" -ForegroundColor White
Write-Host "   ✓ Document metadata analysis" -ForegroundColor White
Write-Host "   ✓ Statistical operations and counting" -ForegroundColor White
Write-Host ""
Write-Host "🧠 RELATIONAL BRAIN (Neo4j):" -ForegroundColor Green
Write-Host "   ✓ Author-document relationships" -ForegroundColor White
Write-Host "   ✓ Social network discovery" -ForegroundColor White
Write-Host "   ✓ Multi-hop relationship traversal" -ForegroundColor White
Write-Host ""
Write-Host "🎯 INTELLIGENT ORCHESTRATION:" -ForegroundColor Cyan
Write-Host "   ✓ Query intent analysis and routing" -ForegroundColor White
Write-Host "   ✓ Strategy selection based on query type" -ForegroundColor White
Write-Host "   ✓ Multi-database result synthesis" -ForegroundColor White
Write-Host "   ✓ Emergent intelligence from brain combination" -ForegroundColor White
Write-Host ""
Write-Host "The three-brain architecture creates capabilities that exceed" -ForegroundColor Yellow
Write-Host "what any single database system could achieve alone!" -ForegroundColor Yellow
