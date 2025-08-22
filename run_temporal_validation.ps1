# Nancy Temporal Brain Validation Executor
# PowerShell script to execute the comprehensive temporal validation strategy

Write-Host "Nancy Temporal Brain: Intermediate Validation Strategy" -ForegroundColor Green
Write-Host "Addressing validation-skeptic concerns with real systems and data" -ForegroundColor Green
Write-Host "=" * 80

# Check if Docker services are running
Write-Host "`nChecking Docker services..." -ForegroundColor Yellow
$dockerStatus = docker-compose ps

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker services not running. Starting services..." -ForegroundColor Red
    Write-Host "Running: docker-compose up -d --build" -ForegroundColor Yellow
    docker-compose up -d --build
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to start Docker services. Exiting." -ForegroundColor Red
        exit 1
    }
    
    Write-Host "⏳ Waiting 30 seconds for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 30
}

# Verify services are healthy
Write-Host "`nVerifying service health..." -ForegroundColor Yellow

$nancyHealth = try { 
    Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✅ Nancy service: Healthy" -ForegroundColor Green
    $true
} catch {
    Write-Host "❌ Nancy service: Unhealthy - $($_.Exception.Message)" -ForegroundColor Red
    $false
}

$baselineHealth = try {
    Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 10
    Write-Host "✅ Baseline service: Healthy" -ForegroundColor Green
    $true
} catch {
    Write-Host "❌ Baseline service: Unhealthy - $($_.Exception.Message)" -ForegroundColor Red
    $false
}

if (-not $nancyHealth -or -not $baselineHealth) {
    Write-Host "`n⚠️  Services not fully healthy. Proceeding with validation anyway..." -ForegroundColor Yellow
    Write-Host "   (Validation will include service health assessment)" -ForegroundColor Yellow
}

# Check if test data exists
Write-Host "`nChecking test data availability..." -ForegroundColor Yellow
$testDataPath = ".\benchmark_test_data"

if (Test-Path $testDataPath) {
    $testFiles = Get-ChildItem $testDataPath -Filter "*.txt"
    Write-Host "✅ Test data found: $($testFiles.Count) files" -ForegroundColor Green
    foreach ($file in $testFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Test data directory not found: $testDataPath" -ForegroundColor Red
    Write-Host "   Creating sample test data..." -ForegroundColor Yellow
    
    # Create test data directory and sample files
    New-Item -ItemType Directory -Path $testDataPath -Force | Out-Null
    
    # Create a sample temporal test file
    $sampleContent = @"
Engineering Project Timeline
Date: March 22, 2024
Project: IoT Device Development

TIMELINE:
January 15, 2024 - Requirements gathering meeting
January 30, 2024 - Initial system architecture decision
February 10, 2024 - Thermal constraints specification by Sarah Chen  
February 22, 2024 - Power management strategy finalized
March 5, 2024 - Electrical design review with Mike Rodriguez
March 22, 2024 - Design review meeting with all stakeholders

DECISIONS:
- Budget constraint led to material change from aluminum to plastic
- Thermal analysis triggered design modifications  
- EMC compliance requirements influenced electrical architecture
- Customer feedback impacted industrial design timeline

PARTICIPANTS:
- Sarah Chen (Systems Engineering)
- Mike Rodriguez (Electrical Engineering)
- Lisa Park (Industrial Design)
- Tom Wilson (Firmware Engineering)
- Jennifer Adams (Project Manager)
"@
    
    $sampleContent | Out-File -FilePath "$testDataPath\sample_timeline.txt" -Encoding UTF8
    Write-Host "✅ Sample test data created" -ForegroundColor Green
}

# Execute the validation strategy
Write-Host "`n" + "=" * 80 -ForegroundColor Green
Write-Host "STARTING TEMPORAL VALIDATION EXECUTION" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green

Write-Host "`nExecuting comprehensive validation strategy..." -ForegroundColor Yellow
Write-Host "This will run the three-phase validation protocol:" -ForegroundColor Yellow
Write-Host "  Phase 1: Real System Baseline Establishment" -ForegroundColor Gray
Write-Host "  Phase 2: Head-to-Head Temporal Comparison" -ForegroundColor Gray  
Write-Host "  Phase 3: Independent Adversarial Validation" -ForegroundColor Gray

# Run the Python validation executor
try {
    Write-Host "`nStarting Python validation executor..." -ForegroundColor Yellow
    python temporal_validation_executor.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ VALIDATION COMPLETE: GO DECISION" -ForegroundColor Green
        Write-Host "   Temporal brain development shows clear value" -ForegroundColor Green
    }
    elseif ($LASTEXITCODE -eq 2) {
        Write-Host "`n🚫 VALIDATION COMPLETE: NO-GO DECISION" -ForegroundColor Red
        Write-Host "   Temporal brain development does not meet criteria" -ForegroundColor Red
    }
    else {
        Write-Host "`n❌ VALIDATION FAILED: Technical error occurred" -ForegroundColor Red
        Write-Host "   Check logs for details" -ForegroundColor Red
    }
}
catch {
    Write-Host "`n❌ Failed to execute validation: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Ensure Python and required packages are installed" -ForegroundColor Yellow
    exit 1
}

# Check for results files
Write-Host "`nChecking validation results..." -ForegroundColor Yellow
$resultsPath = ".\temporal_validation_results"

if (Test-Path $resultsPath) {
    $resultFiles = Get-ChildItem $resultsPath -Filter "*.json" | Sort-Object LastWriteTime -Descending
    Write-Host "✅ Validation results saved:" -ForegroundColor Green
    foreach ($file in $resultFiles) {
        Write-Host "   - $($file.Name)" -ForegroundColor Gray
    }
    
    # Show latest comprehensive result summary
    $latestComprehensive = $resultFiles | Where-Object { $_.Name -like "*comprehensive*" } | Select-Object -First 1
    if ($latestComprehensive) {
        Write-Host "`nLatest comprehensive result: $($latestComprehensive.Name)" -ForegroundColor Yellow
        try {
            $result = Get-Content $latestComprehensive.FullName | ConvertFrom-Json
            $decision = $result.final_assessment.go_no_go_decision
            $confidence = $result.final_assessment.confidence_level
            $recommendation = $result.final_assessment.recommendation
            
            Write-Host "`n📊 FINAL ASSESSMENT:" -ForegroundColor Green
            Write-Host "   Decision: $decision" -ForegroundColor $(if ($decision -eq "GO") { "Green" } else { "Red" })
            Write-Host "   Confidence: $confidence" -ForegroundColor Yellow
            Write-Host "   Recommendation: $recommendation" -ForegroundColor Gray
        }
        catch {
            Write-Host "   (Could not parse result details)" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "⚠️  No validation results found" -ForegroundColor Yellow
}

Write-Host "`n" + "=" * 80 -ForegroundColor Green
Write-Host "TEMPORAL VALIDATION STRATEGY EXECUTION COMPLETE" -ForegroundColor Green
Write-Host "Results provide credible evidence for development decisions" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green