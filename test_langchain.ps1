#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Test Nancy's LangChain integration
.DESCRIPTION
    This script tests the new LangChain orchestrator integration to ensure
    it maintains Nancy's Four-Brain functionality while adding LangChain benefits.
.EXAMPLE
    .\test_langchain.ps1
#>

Write-Host "🔍 Nancy LangChain Integration Test" -ForegroundColor Cyan
Write-Host "=" * 45 -ForegroundColor Cyan

# Check if Nancy is running
Write-Host "`n1. Checking Nancy system status..." -ForegroundColor Yellow

try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "   ✓ Nancy API: " -NoNewline -ForegroundColor Green
    Write-Host "RESPONDING" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Nancy API: " -NoNewline -ForegroundColor Red
    Write-Host "NOT RESPONDING" -ForegroundColor Red
    Write-Host "   Please start Nancy: docker-compose up -d" -ForegroundColor Gray
    exit 1
}

# Check if LangChain dependencies are installed
Write-Host "`n2. Checking LangChain dependencies..." -ForegroundColor Yellow

# We'll detect this by trying a LangChain query
try {
    $testQuery = @{
        query = "test"
        orchestrator = "langchain"
        n_results = 1
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $testQuery -ContentType "application/json" -TimeoutSec 30
    Write-Host "   ✓ LangChain orchestrator: " -NoNewline -ForegroundColor Green
    Write-Host "READY" -ForegroundColor Green
    $langchainReady = $true
} catch {
    Write-Host "   ❌ LangChain orchestrator: " -NoNewline -ForegroundColor Red
    Write-Host "NOT READY" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    $langchainReady = $false
}

# Run the comprehensive test
Write-Host "`n3. Running comprehensive integration test..." -ForegroundColor Yellow

if ($langchainReady) {
    Write-Host "   Running Python test suite..." -ForegroundColor Gray
    Write-Host "   (This may take several minutes)" -ForegroundColor Gray
    
    try {
        & python test_langchain_integration.py
        $testExitCode = $LASTEXITCODE
        
        if ($testExitCode -eq 0) {
            Write-Host "`n🎉 LangChain integration test completed!" -ForegroundColor Green
        } else {
            Write-Host "`n⚠️  Test completed with warnings or errors (exit code: $testExitCode)" -ForegroundColor Yellow
        }
        
        # Show recent test files
        $recentTests = Get-ChildItem -Path . -Filter "langchain_integration_test_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($recentTests) {
            Write-Host "   📄 Test results saved to: $($recentTests.Name)" -ForegroundColor Gray
        }
        
    } catch {
        Write-Host "`n❌ Test execution failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "   Skipping comprehensive test - LangChain orchestrator not ready" -ForegroundColor Yellow
    
    # Try to provide helpful information
    Write-Host "`n4. Troubleshooting suggestions:" -ForegroundColor Yellow
    Write-Host "   • Rebuild Nancy container: docker-compose up --build nancy-api" -ForegroundColor Gray
    Write-Host "   • Check container logs: docker logs nancy-api-1" -ForegroundColor Gray
    Write-Host "   • Verify requirements.txt includes LangChain dependencies" -ForegroundColor Gray
}

# Quick single test as fallback
Write-Host "`n4. Quick functionality test..." -ForegroundColor Yellow

$quickTests = @(
    @{
        orchestrator = "intelligent"
        description = "Intelligent Orchestrator"
    },
    @{
        orchestrator = "enhanced" 
        description = "Enhanced Orchestrator"
    }
)

foreach ($test in $quickTests) {
    try {
        $quickQuery = @{
            query = "What is the operating temperature?"
            orchestrator = $test.orchestrator
            n_results = 3
        } | ConvertTo-Json
        
        $start = Get-Date
        $result = Invoke-RestMethod -Uri "http://localhost:8000/api/query" -Method Post -Body $quickQuery -ContentType "application/json" -TimeoutSec 60
        $duration = (Get-Date) - $start
        
        Write-Host "   ✓ $($test.description): " -NoNewline -ForegroundColor Green
        Write-Host "$($duration.TotalSeconds.ToString('F1'))s" -ForegroundColor Green
        
    } catch {
        Write-Host "   ❌ $($test.description): " -NoNewline -ForegroundColor Red
        Write-Host "FAILED" -ForegroundColor Red
    }
}

Write-Host "`nTest completed." -ForegroundColor Cyan