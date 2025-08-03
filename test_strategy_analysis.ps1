# Strategy Analysis Tool - Test Nancy's Query Intelligence
# Shows what database strategy Nancy would choose for different query types

param(
    [string]$ApiUrl = "http://localhost:8000/api"
)

Write-Host "🧠 NANCY QUERY STRATEGY ANALYZER 🧠" -ForegroundColor Magenta
Write-Host "====================================" -ForegroundColor Magenta
Write-Host ""

function Test-QueryStrategy {
    param(
        [string]$Query,
        [string]$Category
    )
    
    $queryBody = @{
        "query" = $Query
        "n_results" = 5
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$ApiUrl/query/test-strategy" -Method Post -Body $queryBody -ContentType "application/json"
        
        Write-Host "Query: '$Query'" -ForegroundColor White
        Write-Host "Category: $Category" -ForegroundColor Gray
        Write-Host "Strategy: $($response.predicted_strategy.type)" -ForegroundColor Yellow
        Write-Host "Primary Brain: $($response.predicted_strategy.primary_brain)" -ForegroundColor Cyan
        Write-Host "Focus: $($response.predicted_strategy.focus)" -ForegroundColor Green
        Write-Host "Description: $($response.description)" -ForegroundColor Gray
        Write-Host ""
        
    } catch {
        Write-Host "❌ Error testing strategy for: $Query" -ForegroundColor Red
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "📝 CONTENT-FOCUSED QUERIES (Vector Brain Expected)" -ForegroundColor Green
Test-QueryStrategy "machine learning algorithms" "Content Search"
Test-QueryStrategy "database performance optimization" "Technical Content"
Test-QueryStrategy "the hidden tax of context-switching" "Conceptual Content"

Write-Host "👥 PEOPLE-FOCUSED QUERIES (Relational Brain Expected)" -ForegroundColor Green
Test-QueryStrategy "documents by Scott" "Author Query"
Test-QueryStrategy "who wrote the architecture report" "Author Discovery"
Test-QueryStrategy "Sarah Johnson's contributions" "Author Focus"

Write-Host "📊 ANALYTICAL QUERIES (Analytical Brain Expected)" -ForegroundColor Green
Test-QueryStrategy "recent documents" "Temporal Query"
Test-QueryStrategy "how many files were uploaded" "Statistical Query"
Test-QueryStrategy "largest documents in the system" "Metadata Analysis"

Write-Host "🕸️ RELATIONSHIP QUERIES (Graph Exploration Expected)" -ForegroundColor Green
Test-QueryStrategy "show me related documents" "Relationship Discovery"
Test-QueryStrategy "what other work is connected to this" "Connection Exploration"
Test-QueryStrategy "documents similar to the performance report" "Similarity + Relationships"

Write-Host "🔀 HYBRID QUERIES (Multiple Brains Expected)" -ForegroundColor Green
Test-QueryStrategy "architecture decisions made recently" "Temporal + Content"
Test-QueryStrategy "who worked on recent performance improvements" "People + Time + Content"
Test-QueryStrategy "find collaboration patterns in our team" "Complex Analysis"

Write-Host "✨ NANCY'S INTELLIGENCE IN ACTION ✨" -ForegroundColor Magenta
Write-Host ""
Write-Host "Nancy analyzes each query to determine:" -ForegroundColor White
Write-Host "• Which database brain should take the lead" -ForegroundColor Gray
Write-Host "• What type of orchestration strategy to use" -ForegroundColor Gray  
Write-Host "• How to combine results from multiple brains" -ForegroundColor Gray
Write-Host "• The optimal order of database operations" -ForegroundColor Gray
Write-Host ""
Write-Host "This intelligent routing ensures you get the best possible" -ForegroundColor Yellow
Write-Host "answers by leveraging the right database for each query type!" -ForegroundColor Yellow
