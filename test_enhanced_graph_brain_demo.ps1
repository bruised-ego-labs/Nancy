# Enhanced GraphBrain Demo - Project Story Capture
# Demonstrates the enhanced GraphBrain capabilities for project knowledge

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Nancy Enhanced GraphBrain Demo" -ForegroundColor Cyan  
Write-Host "Project Story & Decision Archaeology" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Check services
Write-Host "`nChecking Nancy services..." -ForegroundColor Yellow
try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "Nancy API is ready!" -ForegroundColor Green
}
catch {
    Write-Host "Starting Nancy services..." -ForegroundColor Yellow
    docker-compose up -d
    Start-Sleep -Seconds 30
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "DEMO: Enhanced Project Story Ingestion" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Enhanced test document with rich project story elements
$projectStoryDoc = @"
Project Meeting Notes - Q4 2024 Nancy Architecture Review

Meeting Attendees:
- Scott Johnson (Project Lead)
- Sarah Chen (Thermal Engineer) 
- Mike Rodriguez (Electrical Engineer)
- Lisa Park (Mechanical Engineer)

Key Decisions Made:
1. DECISION: Adopt Four-Brain Architecture with Local LLM
   - DECISION MAKER: Scott Johnson
   - CONTEXT: Need zero-cost AI operations with complete privacy
   - INFLUENCED BY: Budget constraints and data security requirements
   - ERA: Q4 2024 Architecture Phase

2. DECISION: Use Gemma 2B for Local Processing
   - DECISION MAKER: Scott Johnson  
   - CONTEXT: Memory constraints on 16GB development machine
   - INFLUENCED BY: Docker memory limitations and performance testing
   - ERA: Q4 2024 Implementation Phase

Cross-Team Collaboration:
- Sarah Chen COLLABORATED WITH Mike Rodriguez on thermal-electrical integration
- Mike Rodriguez WORKED WITH Lisa Park on mechanical cooling requirements
- Scott Johnson COORDINATED WITH entire team on architecture decisions

Features Developed:
1. FEATURE: GraphBrain Enhanced Relationship Extraction
   - OWNER: Scott Johnson
   - INFLUENCED BY: "Adopt Four-Brain Architecture" decision
   - DEPENDS ON: Local LLM processing capabilities

2. FEATURE: Project Story Capture System
   - OWNER: Scott Johnson
   - INFLUENCED BY: Need for decision archaeology and project context
   - COLLABORATES WITH: Enhanced LLM prompts

Technical Constraints:
- Memory usage CONSTRAINS model selection (Gemma 2B vs larger models)
- Docker container limits AFFECT Ollama configuration
- Privacy requirements INFLUENCE local-only processing design

Project Phases:
- PHASE: "Q4 2024 Architecture Phase" - Initial four-brain design
- PHASE: "Q4 2024 Implementation Phase" - Local LLM integration and testing
- PHASE: "Q4 2024 Demonstration Phase" - System validation and demo preparation

Meeting Outcomes:
- This meeting RESULTED IN "Adopt Four-Brain Architecture" decision
- Architecture review RESULTED IN "Use Gemma 2B" decision
- Team alignment achieved on privacy-first approach

Document References:
- This document REFERENCES "Nancy System Requirements"
- Architecture decisions INFLUENCED BY "Budget Analysis Q4 2024"
- Implementation plan DEPENDS ON "Technical Feasibility Study"
"@

Write-Host "Ingesting enhanced project story document..." -ForegroundColor Yellow

# Create temp file and ingest
$tempFile = [System.IO.Path]::GetTempFileName()
$projectStoryDoc | Out-File -FilePath $tempFile -Encoding UTF8

try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"project_story_demo.txt`"",
        "Content-Type: text/plain$LF",
        $projectStoryDoc,
        "--$boundary",
        "Content-Disposition: form-data; name=`"author`"$LF",
        "Scott Johnson",
        "--$boundary--"
    )
    $body = $bodyLines -join $LF
    
    $ingestResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/ingest" -Method Post -Body $body -ContentType "multipart/form-data; boundary=`"$boundary`"" -TimeoutSec 120
    
    Write-Host "Document ingested successfully!" -ForegroundColor Green
    Write-Host "Document ID: $($ingestResponse.doc_id)" -ForegroundColor White
    Write-Host "Enhanced GraphBrain processing:" -ForegroundColor Gray
    Write-Host "  - Decisions extracted and linked to makers" -ForegroundColor Gray
    Write-Host "  - Meetings and attendees captured" -ForegroundColor Gray
    Write-Host "  - Features linked to decisions" -ForegroundColor Gray
    Write-Host "  - Project phases and eras identified" -ForegroundColor Gray
    Write-Host "  - Cross-team collaborations mapped" -ForegroundColor Gray
}
catch {
    Write-Host "Failed to ingest: $($_.Exception.Message)" -ForegroundColor Red
}
finally {
    Remove-Item $tempFile -ErrorAction SilentlyContinue
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "DEMO: Enhanced Query Capabilities" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

# Test the new project story query capabilities
$enhancedQueries = @(
    @{
        "query" = "Why did we choose the Four-Brain Architecture?"
        "type" = "Decision Provenance Analysis"
        "expected" = "Should trace back to Scott Johnson's decision and context"
    },
    @{
        "query" = "Who are the experts on thermal design?"
        "type" = "Knowledge Expert Identification"
        "expected" = "Should identify Sarah Chen and her expertise"
    },
    @{
        "query" = "What decisions led to using Gemma 2B?"
        "type" = "Decision Chain Analysis"
        "expected" = "Should show memory constraints and technical decisions"
    },
    @{
        "query" = "How do thermal and electrical teams collaborate?"
        "type" = "Cross-Team Collaboration Discovery"
        "expected" = "Should find Sarah-Mike collaboration patterns"
    },
    @{
        "query" = "What happened in Q4 2024 Architecture Phase?"
        "type" = "Project Timeline Analysis"
        "expected" = "Should show era-specific decisions and activities"
    }
)

foreach ($query in $enhancedQueries) {
    Write-Host "`n" + "="*60 -ForegroundColor DarkCyan
    Write-Host "TESTING: $($query.type)" -ForegroundColor Yellow
    Write-Host "Query: '$($query.query)'" -ForegroundColor White
    Write-Host "Expected: $($query.expected)" -ForegroundColor Gray
    Write-Host "-"*60 -ForegroundColor DarkCyan
    
    try {
        $queryBody = @{
            query = $query.query
            n_results = 5
            use_enhanced = $true
        } | ConvertTo-Json
        
        $startTime = Get-Date
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $queryBody -ContentType "application/json" -TimeoutSec 60
        $endTime = Get-Date
        $processingTime = ($endTime - $startTime).TotalSeconds
        
        Write-Host "Processing time: $([math]::Round($processingTime, 1)) seconds" -ForegroundColor Green
        Write-Host "Strategy used: $($response.strategy_used)" -ForegroundColor Green
        Write-Host "Query intent: $($response.intent.type)" -ForegroundColor Green
        
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
                $preview = $topResult.text.Substring(0, [Math]::Min(150, $topResult.text.Length)) + "..."
                Write-Host "Content preview: $preview" -ForegroundColor Gray
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
Write-Host "LOCAL LLM PROJECT STORY PROCESSING" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "Checking local Gemma processing for project story extraction..." -ForegroundColor Yellow

try {
    $logOutput = docker-compose logs api --tail=10 | Select-String "Local Ollama\|project story\|story elements"
    
    if ($logOutput) {
        Write-Host "`nLocal LLM project story processing:" -ForegroundColor Green
        foreach ($line in $logOutput) {
            Write-Host "  $line" -ForegroundColor White
        }
    } else {
        Write-Host "No recent local LLM story processing found" -ForegroundColor Yellow
    }
    
    # Check for story element processing
    $storyLogs = docker-compose logs api --tail=20 | Select-String "Processed project story elements"
    if ($storyLogs) {
        Write-Host "`nProject story elements processed:" -ForegroundColor Green
        foreach ($line in $storyLogs) {
            Write-Host "  $line" -ForegroundColor White
        }
    }
}
catch {
    Write-Host "Could not analyze logs: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "ENHANCED GRAPHBRAIN CAPABILITIES SUMMARY" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan

Write-Host "`nGRAPHBRAIN ENHANCEMENTS:" -ForegroundColor Yellow

Write-Host "`n1. PROJECT STORY CAPTURE:" -ForegroundColor Green
Write-Host "   - Decisions and decision makers" -ForegroundColor White
Write-Host "   - Meetings and attendees" -ForegroundColor White
Write-Host "   - Features and owners" -ForegroundColor White
Write-Host "   - Project eras and phases" -ForegroundColor White
Write-Host "   - Cross-team collaborations" -ForegroundColor White

Write-Host "`n2. DECISION ARCHAEOLOGY:" -ForegroundColor Blue
Write-Host "   - Why decisions were made" -ForegroundColor White
Write-Host "   - Who influenced decisions" -ForegroundColor White
Write-Host "   - What decisions led to features" -ForegroundColor White
Write-Host "   - Timeline of decision evolution" -ForegroundColor White

Write-Host "`n3. KNOWLEDGE EXPERT IDENTIFICATION:" -ForegroundColor Magenta
Write-Host "   - Subject matter expertise scoring" -ForegroundColor White
Write-Host "   - Cross-domain collaboration networks" -ForegroundColor White
Write-Host "   - Knowledge silo detection" -ForegroundColor White
Write-Host "   - Expertise transfer planning" -ForegroundColor White

Write-Host "`n4. IMPACT ANALYSIS:" -ForegroundColor Cyan
Write-Host "   - Document change impact prediction" -ForegroundColor White
Write-Host "   - Stakeholder notification chains" -ForegroundColor White
Write-Host "   - Dependency risk assessment" -ForegroundColor White
Write-Host "   - Feature relationship mapping" -ForegroundColor White

Write-Host "`nBUSINESS VALUE FOR ENGINEERING TEAMS:" -ForegroundColor Yellow
Write-Host "   - Instant decision context recovery" -ForegroundColor Green
Write-Host "   - New team member onboarding acceleration" -ForegroundColor Green
Write-Host "   - Knowledge transfer risk mitigation" -ForegroundColor Green
Write-Host "   - Cross-team dependency visibility" -ForegroundColor Green
Write-Host "   - Project evolution understanding" -ForegroundColor Green
Write-Host "   - Zero-cost AI-powered insights" -ForegroundColor Green

Write-Host "`nGraphBrain vs Simple Author Attribution:" -ForegroundColor Cyan
Write-Host "   OLD: 'Who wrote this document?'" -ForegroundColor Red
Write-Host "   NEW: 'Why was this decision made, who influenced it, what resulted from it, and how does it affect our current work?'" -ForegroundColor Green

Write-Host "`nNancy Enhanced GraphBrain demonstration complete!" -ForegroundColor Green
Write-Host "The project story is now captured and queryable with zero-cost local AI." -ForegroundColor Cyan