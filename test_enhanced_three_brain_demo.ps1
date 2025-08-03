# Enhanced Three-Brain Architecture Demo
# Demonstrates the advanced capabilities of Nancy's intelligent orchestration

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Nancy Enhanced Three-Brain Architecture Demo" -ForegroundColor Cyan  
Write-Host "Intelligent Query Orchestration & LLM Synthesis" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check if Docker services are running
Write-Host "`nChecking Docker services..." -ForegroundColor Yellow
$dockerStatus = docker-compose ps --services --filter "status=running"

if ($dockerStatus -notcontains "api" -or $dockerStatus -notcontains "chromadb" -or $dockerStatus -notcontains "neo4j") {
    Write-Host "Starting Nancy services..." -ForegroundColor Yellow
    docker-compose up -d --build
    
    Write-Host "Waiting for services to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}
else {
    Write-Host "Docker services are already running." -ForegroundColor Green
}

# Health check
Write-Host "Testing API connectivity..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "Nancy API is ready!" -ForegroundColor Green
}
catch {
    Write-Host "Nancy API is not responding. Please check Docker services." -ForegroundColor Red
    exit 1
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "DEMO: Enhanced Query Intelligence" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Demo queries that showcase three-brain advantages
$demoQueries = @(
    @{
        "query" = "Who wrote the thermal analysis document?"
        "type" = "Author Attribution"
        "expected" = "Should identify Sarah Chen and show knowledge graph advantage"
    },
    @{
        "query" = "Show me documents from March about power consumption"
        "type" = "Temporal + Semantic Filtering"
        "expected" = "Should filter by date AND content - demonstrates analytical brain filtering"
    },
    @{
        "query" = "What thermal issues affected Mike's electrical design?"
        "type" = "Cross-Team Relationship Discovery"
        "expected" = "Should find connections between Sarah's thermal work and Mike's electrical work"
    },
    @{
        "query" = "Find all documents that mention power management"
        "type" = "Concept-Based Search"
        "expected" = "Should find semantic matches plus relationship-based connections"
    },
    @{
        "query" = "What decisions did Sarah Chen make that affected the project?"
        "type" = "Decision Impact Analysis"
        "expected" = "Should trace decision chains through the knowledge graph"
    }
)

Write-Host "Testing Nancy's Enhanced Query Intelligence:" -ForegroundColor White
Write-Host "Each query will show:" -ForegroundColor Gray
Write-Host "• Query intent analysis (which brains to use)" -ForegroundColor Gray
Write-Host "• Intelligent routing strategy" -ForegroundColor Gray
Write-Host "• Multi-brain synthesis results" -ForegroundColor Gray
Write-Host "• Natural language response (when LLM configured)" -ForegroundColor Gray

foreach ($demo in $demoQueries) {
    Write-Host "`n" + "="*60 -ForegroundColor DarkCyan
    Write-Host "TESTING: $($demo.type)" -ForegroundColor Yellow
    Write-Host "Query: '$($demo.query)'" -ForegroundColor White
    Write-Host "Expected: $($demo.expected)" -ForegroundColor Gray
    Write-Host "-"*60 -ForegroundColor DarkCyan
    
    try {
        # First, show the query strategy analysis
        Write-Host "`n1. Query Intent Analysis:" -ForegroundColor Cyan
        $strategyBody = @{
            query = $demo.query
            n_results = 5
        } | ConvertTo-Json
        
        $strategyResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/query/test-strategy" -Method Post -Body $strategyBody -ContentType "application/json" -TimeoutSec 30
        
        Write-Host "   Strategy: $($strategyResponse.predicted_strategy.type)" -ForegroundColor Green
        Write-Host "   Primary Brain: $($strategyResponse.predicted_strategy.primary_brain)" -ForegroundColor Green
        Write-Host "   Focus: $($strategyResponse.predicted_strategy.focus)" -ForegroundColor Green
        
        # Now execute the actual query with enhanced orchestrator
        Write-Host "`n2. Enhanced Query Execution:" -ForegroundColor Cyan
        $queryBody = @{
            query = $demo.query
            n_results = 5
            use_enhanced = $true
        } | ConvertTo-Json
        
        $queryResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $queryBody -ContentType "application/json" -TimeoutSec 30
        
        Write-Host "   Processing Method: $($queryResponse.metadata.processing_method)" -ForegroundColor Green
        Write-Host "   Brains Used: $($queryResponse.metadata.brains_used -join ', ')" -ForegroundColor Green
        Write-Host "   Results Found: $($queryResponse.metadata.result_count)" -ForegroundColor Green
        
        if ($queryResponse.natural_response) {
            Write-Host "`n3. Natural Language Response:" -ForegroundColor Cyan
            Write-Host "   $($queryResponse.natural_response)" -ForegroundColor White
        } else {
            Write-Host "`n3. Raw Results Summary:" -ForegroundColor Cyan
            if ($queryResponse.raw_results.results.Count -gt 0) {
                $topResult = $queryResponse.raw_results.results[0]
                if ($topResult.author) {
                    Write-Host "   Top Result: $($topResult.document_metadata.filename) by $($topResult.author)" -ForegroundColor White
                }
                if ($topResult.text) {
                    $preview = $topResult.text.Substring(0, [Math]::Min(100, $topResult.text.Length)) + "..."
                    Write-Host "   Preview: $preview" -ForegroundColor Gray
                }
            } else {
                Write-Host "   No results found" -ForegroundColor Yellow
            }
        }
        
        # Show comparison with legacy orchestrator
        Write-Host "`n4. Legacy vs Enhanced Comparison:" -ForegroundColor Cyan
        $legacyBody = @{
            query = $demo.query
            n_results = 5
            use_enhanced = $false
        } | ConvertTo-Json
        
        $legacyResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $legacyBody -ContentType "application/json" -TimeoutSec 30
        
        $enhancedCount = $queryResponse.metadata.result_count
        $legacyCount = if ($legacyResponse.results) { $legacyResponse.results.Count } else { 0 }
        
        Write-Host "   Enhanced Results: $enhancedCount" -ForegroundColor Green
        Write-Host "   Legacy Results: $legacyCount" -ForegroundColor Yellow
        
        if ($enhancedCount -gt $legacyCount) {
            Write-Host "   Enhanced orchestrator found more relevant results!" -ForegroundColor Green
        } elseif ($enhancedCount -eq $legacyCount) {
            Write-Host "   Similar result count, but enhanced provides better context" -ForegroundColor Yellow
        }
        
    }
    catch {
        Write-Host "   Error testing query: $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Start-Sleep -Seconds 2
}

Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "DEMO: Three-Brain Architecture Benefits Summary" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan

Write-Host "`nKey Advantages Demonstrated:" -ForegroundColor Yellow

Write-Host "`nVECTOR BRAIN (ChromaDB + FastEmbed):" -ForegroundColor Green
Write-Host "   • Semantic search across document content" -ForegroundColor White
Write-Host "   • Finds conceptually similar text even without keyword matches" -ForegroundColor White
Write-Host "   • Handles natural language queries effectively" -ForegroundColor White

Write-Host "`nANALYTICAL BRAIN (DuckDB):" -ForegroundColor Blue  
Write-Host "   • Metadata filtering by date, author, file type, size" -ForegroundColor White
Write-Host "   • Statistical analysis and document analytics" -ForegroundColor White
Write-Host "   • Temporal queries and trend analysis" -ForegroundColor White

Write-Host "`nRELATIONAL BRAIN (Neo4j):" -ForegroundColor Magenta
Write-Host "   • Author attribution and accountability tracking" -ForegroundColor White
Write-Host "   • Cross-team influence and decision impact analysis" -ForegroundColor White
Write-Host "   • Document relationship discovery and graph traversal" -ForegroundColor White
Write-Host "   • Collaboration network analysis" -ForegroundColor White

Write-Host "`nINTELLIGENT ORCHESTRATION:" -ForegroundColor Cyan
Write-Host "   • Query intent analysis determines optimal brain usage" -ForegroundColor White
Write-Host "   • Dynamic routing based on query type and content" -ForegroundColor White
Write-Host "   • Multi-brain synthesis for comprehensive results" -ForegroundColor White
Write-Host "   • LLM-powered natural language responses (when configured)" -ForegroundColor White

Write-Host "`nBUSINESS VALUE FOR ENGINEERING TEAMS:" -ForegroundColor Yellow
Write-Host "   • Instant access to project knowledge across disciplines" -ForegroundColor White
Write-Host "   • Decision traceability and accountability" -ForegroundColor White
Write-Host "   • Cross-team collaboration insights" -ForegroundColor White
Write-Host "   • Reduced context-switching and knowledge loss" -ForegroundColor White
Write-Host "   • Intelligent information discovery beyond simple search" -ForegroundColor White

Write-Host "`nNext Steps:" -ForegroundColor Cyan
Write-Host "1. Configure LLM API keys (Claude/Gemini) for natural language synthesis" -ForegroundColor White
Write-Host "2. Ingest your team actual project documents" -ForegroundColor White
Write-Host "3. Train team members on query types for optimal results" -ForegroundColor White
Write-Host "4. Expand relationship extraction rules for your domain" -ForegroundColor White

Write-Host "`nNancy Enhanced Three-Brain Demo completed!" -ForegroundColor Green