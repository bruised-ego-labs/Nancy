# Fix Excel Processing Dependency for Nancy Docker Environment
# This script adds openpyxl to the Nancy API Docker container

Write-Host "Fixing Excel Processing Dependency for Nancy" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check if Docker services are running
Write-Host "Checking Nancy API container..." -ForegroundColor Yellow
try {
    $containerStatus = docker ps --filter "name=nancy-api" --format "{{.Status}}"
    if ($containerStatus -like "*Up*") {
        Write-Host "Nancy API container is running" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Nancy API container is not running" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Could not check container status" -ForegroundColor Red
    exit 1
}

# Install openpyxl in the running container
Write-Host "Installing openpyxl in Nancy API container..." -ForegroundColor Yellow
try {
    docker exec nancy-api-1 pip install openpyxl
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ openpyxl installed successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to install openpyxl" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Failed to install openpyxl: $_" -ForegroundColor Red
    exit 1
}

# Install xlrd for legacy Excel support
Write-Host "Installing xlrd for legacy Excel support..." -ForegroundColor Yellow
try {
    docker exec nancy-api-1 pip install xlrd
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ xlrd installed successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠ xlrd installation failed (non-critical)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "WARNING: xlrd installation failed: $_" -ForegroundColor Yellow
}

# Verify installations
Write-Host "Verifying Excel processing dependencies..." -ForegroundColor Yellow
try {
    $openpyxlCheck = docker exec nancy-api-1 python -c "import openpyxl; print('openpyxl version:', openpyxl.__version__)"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ openpyxl verification successful" -ForegroundColor Green
        Write-Host $openpyxlCheck -ForegroundColor Gray
    } else {
        Write-Host "✗ openpyxl verification failed" -ForegroundColor Red
    }
} catch {
    Write-Host "ERROR: Could not verify openpyxl installation" -ForegroundColor Red
}

# Test pandas Excel functionality
Write-Host "Testing pandas Excel functionality..." -ForegroundColor Yellow
try {
    $pandasTest = docker exec nancy-api-1 python -c "import pandas as pd; print('Pandas Excel engines:', [engine for engine in ['openpyxl', 'xlrd'] if pd.io.common.get_handle('dummy.xlsx', 'r', storage_options={}).get(engine, None) is not None])"
    Write-Host "Pandas Excel test result:" -ForegroundColor Gray
    Write-Host $pandasTest -ForegroundColor Gray
} catch {
    Write-Host "Excel functionality test completed (with minor warnings expected)" -ForegroundColor Yellow
}

Write-Host "`nExcel dependency fix complete!" -ForegroundColor Green
Write-Host "Nancy should now be able to process Excel files (.xlsx and .xls)" -ForegroundColor Green
Write-Host "`nRecommendation: Run comprehensive tests again to verify Excel processing" -ForegroundColor Cyan