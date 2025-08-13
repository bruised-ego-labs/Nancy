#!/usr/bin/env pwsh

<#
.SYNOPSIS
    Run comprehensive Nancy vs Baseline RAG comparison
.DESCRIPTION
    This script runs the Python comparison tool that systematically tests
    Nancy's Four-Brain architecture against the baseline LangChain RAG system.
.EXAMPLE
    .\run_comparison.ps1
#>

Write-Host "🔍 Nancy vs Baseline RAG Comprehensive Comparison" -ForegroundColor Cyan
Write-Host "=" * 55 -ForegroundColor Cyan

# Check if both systems are running
Write-Host "`n1. Checking system status..." -ForegroundColor Yellow

$nancyHealth = $null
$baselineHealth = $null

try {
    $nancyHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "   ✓ Nancy Four-Brain: " -NoNewline -ForegroundColor Green
    Write-Host "HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Nancy Four-Brain: " -NoNewline -ForegroundColor Red
    Write-Host "NOT RESPONDING" -ForegroundColor Red
    Write-Host "      Make sure Nancy is running: docker-compose up -d" -ForegroundColor Gray
}

try {
    $baselineHealth = Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 5
    Write-Host "   ✓ Baseline RAG: " -NoNewline -ForegroundColor Green
    Write-Host "HEALTHY" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Baseline RAG: " -NoNewline -ForegroundColor Red
    Write-Host "NOT RESPONDING" -ForegroundColor Red
    Write-Host "      Make sure Baseline is running: docker-compose up baseline-rag -d" -ForegroundColor Gray
}

if (-not $nancyHealth -or -not $baselineHealth) {
    Write-Host "`n⚠️  Warning: Not all systems are healthy. Comparison may fail." -ForegroundColor Yellow
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne 'y' -and $continue -ne 'Y') {
        Write-Host "Comparison cancelled." -ForegroundColor Red
        exit 1
    }
}

Write-Host "`n2. Starting comprehensive comparison..." -ForegroundColor Yellow
Write-Host "   This will test 7 different query types across both systems" -ForegroundColor Gray
Write-Host "   Expected time: 3-8 minutes (depending on system performance)" -ForegroundColor Gray
Write-Host "   Results will be saved to timestamped JSON file" -ForegroundColor Gray

Write-Host "`n   Press Ctrl+C to cancel..." -ForegroundColor Gray
Start-Sleep -Seconds 2

# Run the Python comparison script
try {
    Write-Host "`n" + "="*55 -ForegroundColor Cyan
    python run_comprehensive_comparison.py
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -eq 0) {
        Write-Host "`n🎉 Comparison completed successfully!" -ForegroundColor Green
        Write-Host "   Check the generated JSON file for detailed results" -ForegroundColor Gray
        
        # List generated files
        $recentFiles = Get-ChildItem -Path . -Filter "nancy_vs_baseline_comparison_*.json" | Sort-Object LastWriteTime -Descending | Select-Object -First 3
        if ($recentFiles) {
            Write-Host "`n📁 Recent comparison files:" -ForegroundColor Cyan
            foreach ($file in $recentFiles) {
                Write-Host "   - $($file.Name) ($($file.LastWriteTime.ToString('yyyy-MM-dd HH:mm')))" -ForegroundColor Gray
            }
        }
        
    } else {
        Write-Host "`n❌ Comparison failed with exit code: $exitCode" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`n❌ Error running comparison: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nComparison script finished." -ForegroundColor Cyan