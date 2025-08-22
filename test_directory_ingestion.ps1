# Test Directory Ingestion System for Nancy
# This script validates the directory-based ingestion with hash-based change detection

Write-Host "=== Nancy Directory Ingestion Test Suite ===" -ForegroundColor Green
Write-Host "Testing directory-based ingestion with four-brain architecture" -ForegroundColor Yellow

# Configuration
$NANCY_API_URL = "http://localhost:8000"
$TEST_DIRECTORY = ".\test_project_directory"

# Create test directory structure if it doesn't exist
if (-not (Test-Path $TEST_DIRECTORY)) {
    Write-Host "Creating test project directory structure..." -ForegroundColor Blue
    
    New-Item -ItemType Directory -Path $TEST_DIRECTORY -Force | Out-Null
    New-Item -ItemType Directory -Path "$TEST_DIRECTORY\docs" -Force | Out-Null
    New-Item -ItemType Directory -Path "$TEST_DIRECTORY\specs" -Force | Out-Null
    New-Item -ItemType Directory -Path "$TEST_DIRECTORY\test_results" -Force | Out-Null
    New-Item -ItemType Directory -Path "$TEST_DIRECTORY\archive" -Force | Out-Null
    
    # Create test files
    @"
# Project Documentation
This is the main project documentation file.

## Overview
Nancy Project is a four-brain AI librarian system.

## Key Features
- Vector Brain: Semantic search capabilities
- Analytical Brain: Structured data storage
- Graph Brain: Relationship mapping
- Linguistic Brain: Query processing

## Team
- Alice Johnson: Lead Engineer
- Bob Smith: Systems Architect
- Carol Davis: Data Scientist
"@ | Out-File -FilePath "$TEST_DIRECTORY\README.md" -Encoding UTF8
    
    @"
# System Requirements Specification
Document: SRS-001
Author: Alice Johnson
Date: 2025-01-15

## Functional Requirements
1. The system shall support semantic search across multiple document types
2. The system shall maintain relationship graphs between documents
3. The system shall provide real-time query processing

## Non-Functional Requirements
- Performance: Query response time < 2 seconds
- Scalability: Support for 10,000+ documents
- Reliability: 99.9% uptime requirement

## Technical Constraints
- Memory: Maximum 8GB RAM usage
- Storage: Supports both local and cloud deployment
- Integration: Must work with existing document management systems
"@ | Out-File -FilePath "$TEST_DIRECTORY\docs\system_requirements.md" -Encoding UTF8
    
    @"
# Power Analysis Report
Document: PWR-001
Author: Bob Smith
Date: 2025-01-10

## Power Consumption Analysis
The thermal constraints require careful power management.

### CPU Power Requirements
- Peak consumption: 95W
- Idle consumption: 15W
- Average operational: 45W

### Memory Power Requirements
- DDR4 modules: 3.2W each
- Total memory power: 12.8W

### Storage Power Requirements
- NVMe SSD: 8.5W active, 1.2W idle
- HDD backup: 12W active, 2.5W idle

## Thermal Analysis
The mechanical stress analysis shows that heat dissipation is critical.
Maximum junction temperature must not exceed 85C.

## Recommendations
1. Implement dynamic frequency scaling
2. Use thermal monitoring with automatic throttling
3. Consider liquid cooling for high-performance scenarios
"@ | Out-File -FilePath "$TEST_DIRECTORY\docs\power_analysis.txt" -Encoding UTF8
    
    @"
Component,Status,Test_Result,Temperature_C,Voltage_V,Current_A,Power_W,Pass_Fail
CPU_Core_1,Active,Stress_Test_1,72.5,1.2,4.2,5.04,Pass
CPU_Core_2,Active,Stress_Test_1,71.8,1.2,4.1,4.92,Pass
Memory_Module_1,Active,Memory_Test,45.2,1.35,2.4,3.24,Pass
Memory_Module_2,Active,Memory_Test,46.1,1.35,2.3,3.105,Pass
GPU_Core,Active,Graphics_Test,68.9,1.1,8.5,9.35,Pass
Power_Supply,Active,Load_Test,42.3,12.0,8.2,98.4,Pass
Storage_SSD,Active,IO_Test,38.7,3.3,2.1,6.93,Pass
Cooling_Fan_1,Active,RPM_Test,35.1,12.0,0.3,3.6,Pass
Cooling_Fan_2,Active,RPM_Test,36.2,12.0,0.29,3.48,Pass
Thermal_Sensor_1,Active,Calibration,25.1,3.3,0.001,0.0033,Pass
"@ | Out-File -FilePath "$TEST_DIRECTORY\test_results\component_testing.csv" -Encoding UTF8
    
    @"
{
    "project_config": {
        "name": "Nancy AI System",
        "version": "1.0.0",
        "build_target": "production",
        "dependencies": {
            "chromadb": "0.4.0",
            "neo4j": "4.4.0",
            "fastapi": "0.68.0",
            "pandas": "1.5.0"
        },
        "deployment": {
            "environment": "docker",
            "scaling": "horizontal",
            "monitoring": true
        },
        "team_contacts": {
            "lead": "alice.johnson@company.com",
            "architect": "bob.smith@company.com",
            "data_scientist": "carol.davis@company.com"
        }
    }
}
"@ | Out-File -FilePath "$TEST_DIRECTORY\specs\project_config.json" -Encoding UTF8
    
    @"
"""
Nancy System Integration Test
Author: Carol Davis
Purpose: Validate four-brain architecture integration

This module tests the integration between:
- Vector Brain (ChromaDB)  
- Analytical Brain (DuckDB)
- Graph Brain (Neo4j)
- Linguistic Brain (Gemma)
"""

import asyncio
import pytest
from nancy.core import IngestionService, QueryService

class TestNancyIntegration:
    def __init__(self):
        self.ingestion = IngestionService()
        self.query = QueryService()
    
    async def test_document_ingestion(self):
        """Test document ingestion through four brains"""
        test_doc = "System architecture decision by Alice Johnson"
        result = await self.ingestion.ingest_text(test_doc)
        assert result.success == True
        return result
    
    async def test_semantic_search(self):
        """Test vector brain semantic search"""
        query = "What are the thermal constraints?"
        results = await self.query.semantic_search(query)
        assert len(results) > 0
        return results
    
    async def test_relationship_queries(self):
        """Test graph brain relationship queries"""
        query = "Who are the experts in power management?"
        results = await self.query.relationship_search(query)
        assert len(results) > 0
        return results
    
    async def test_analytical_queries(self):
        """Test analytical brain structured queries"""
        query = "SELECT * FROM documents WHERE author='Alice Johnson'"
        results = await self.query.analytical_search(query)
        assert len(results) > 0
        return results

if __name__ == "__main__":
    test_suite = TestNancyIntegration()
    print("Nancy Integration Test Suite")
    print("Testing four-brain architecture...")
"@ | Out-File -FilePath "$TEST_DIRECTORY\archive\integration_test.py" -Encoding UTF8
    
    Write-Host "Test directory structure created successfully!" -ForegroundColor Green
}

# Function to make HTTP requests
function Invoke-NancyAPI {
    param(
        [string]$Endpoint,
        [string]$Method = "GET",
        [hashtable]$Body = @{},
        [string]$ContentType = "application/x-www-form-urlencoded"
    )
    
    try {
        $uri = "$NANCY_API_URL$Endpoint"
        
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -ErrorAction Stop
        } else {
            $response = Invoke-RestMethod -Uri $uri -Method $Method -Body $Body -ContentType $ContentType -ErrorAction Stop
        }
        
        return $response
    }
    catch {
        Write-Host "API Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# Function to display test results
function Show-TestResult {
    param(
        [string]$TestName,
        [object]$Result,
        [string]$ExpectedKey = ""
    )
    
    Write-Host "`n--- $TestName ---" -ForegroundColor Cyan
    
    if ($Result -eq $null) {
        Write-Host "FAILED: No response received" -ForegroundColor Red
        return $false
    }
    
    if ($Result.error) {
        Write-Host "FAILED: $($Result.error)" -ForegroundColor Red
        return $false
    }
    
    Write-Host "SUCCESS: Test completed" -ForegroundColor Green
    
    if ($ExpectedKey -ne "" -and $Result.$ExpectedKey) {
        Write-Host "Key metric - $ExpectedKey : $($Result.$ExpectedKey)" -ForegroundColor Yellow
    }
    
    # Show key results
    if ($Result.total_files_discovered) {
        Write-Host "Files discovered: $($Result.total_files_discovered)" -ForegroundColor White
    }
    if ($Result.files_to_process) {
        Write-Host "Files to process: $($Result.files_to_process)" -ForegroundColor White
    }
    if ($Result.files_successful) {
        Write-Host "Files successfully processed: $($Result.files_successful)" -ForegroundColor White
    }
    if ($Result.configured_directories) {
        Write-Host "Configured directories: $($Result.configured_directories)" -ForegroundColor White
    }
    
    return $true
}

# Test 1: Health Check
Write-Host "`n=== Test 1: Health Checks ===" -ForegroundColor Magenta

$healthCheck = Invoke-NancyAPI -Endpoint "/health"
Show-TestResult -TestName "Main API Health Check" -Result $healthCheck

$directoryHealth = Invoke-NancyAPI -Endpoint "/api/directory/health"
Show-TestResult -TestName "Directory Service Health Check" -Result $directoryHealth

# Test 2: Directory Configuration
Write-Host "`n=== Test 2: Directory Configuration ===" -ForegroundColor Magenta

$absolutePath = (Resolve-Path $TEST_DIRECTORY).Path
$configBody = @{
    'directory_path' = $absolutePath
    'recursive' = 'true'
    'file_patterns' = '*.txt,*.md,*.py,*.js,*.json,*.csv'
    'ignore_patterns' = '.git/*,__pycache__/*,*.pyc'
}

$configResult = Invoke-NancyAPI -Endpoint "/api/directory/config" -Method "POST" -Body $configBody
Show-TestResult -TestName "Add Directory Configuration" -Result $configResult -ExpectedKey "config_id"

# Test 3: Directory Scanning
Write-Host "`n=== Test 3: Directory Scanning ===" -ForegroundColor Magenta

$scanBody = @{
    'directory_path' = $absolutePath
    'recursive' = 'true'
    'file_patterns' = '*.txt,*.md,*.py,*.js,*.json,*.csv'
    'ignore_patterns' = '.git/*,__pycache__/*,*.pyc'
    'author' = 'Test Suite'
}

$scanResult = Invoke-NancyAPI -Endpoint "/api/directory/scan" -Method "POST" -Body $scanBody
$scanSuccess = Show-TestResult -TestName "Directory Scan" -Result $scanResult -ExpectedKey "total_files_discovered"

# Test 4: File Processing
Write-Host "`n=== Test 4: File Processing ===" -ForegroundColor Magenta

if ($scanResult -and $scanResult.files_to_process -gt 0) {
    $processBody = @{
        'limit' = '20'
        'author' = 'Test Suite Processing'
    }
    
    $processResult = Invoke-NancyAPI -Endpoint "/api/directory/process" -Method "POST" -Body $processBody
    Show-TestResult -TestName "Process Pending Files" -Result $processResult -ExpectedKey "processed_files"
} else {
    Write-Host "SKIPPED: No files to process" -ForegroundColor Yellow
}

# Test 5: Combined Scan and Process
Write-Host "`n=== Test 5: Combined Scan and Process ===" -ForegroundColor Magenta

# Modify a file to trigger change detection
$readmeContent = Get-Content "$TEST_DIRECTORY\README.md" -Raw
$modifiedContent = $readmeContent + "`n`n## Test Modification`nThis line was added during testing at $(Get-Date)"
$modifiedContent | Out-File -FilePath "$TEST_DIRECTORY\README.md" -Encoding UTF8

Start-Sleep -Seconds 2  # Ensure timestamp difference

$combinedBody = @{
    'directory_path' = $absolutePath
    'recursive' = 'true'
    'file_patterns' = '*.txt,*.md,*.py,*.js,*.json,*.csv'
    'ignore_patterns' = '.git/*,__pycache__/*,*.pyc'
    'author' = 'Test Suite Combined'
    'process_limit' = '15'
}

$combinedResult = Invoke-NancyAPI -Endpoint "/api/directory/scan-and-process" -Method "POST" -Body $combinedBody
Show-TestResult -TestName "Combined Scan and Process" -Result $combinedResult -ExpectedKey "files_processed"

# Test 6: Directory Status
Write-Host "`n=== Test 6: Directory Status ===" -ForegroundColor Magenta

$statusResult = Invoke-NancyAPI -Endpoint "/api/directory/status"
Show-TestResult -TestName "Directory Status" -Result $statusResult -ExpectedKey "configured_directories"

# Test 7: Change Detection Validation
Write-Host "`n=== Test 7: Change Detection Validation ===" -ForegroundColor Magenta

# First scan - should detect no new changes
$changeDetectionScan1 = Invoke-NancyAPI -Endpoint "/api/directory/scan" -Method "POST" -Body $scanBody
if ($changeDetectionScan1 -and $changeDetectionScan1.files_to_process -eq 0) {
    Write-Host "SUCCESS: Change detection working - no new files to process" -ForegroundColor Green
} else {
    Write-Host "WARNING: Unexpected files to process: $($changeDetectionScan1.files_to_process)" -ForegroundColor Yellow
}

# Add a new file
$newFileName = "$TEST_DIRECTORY\docs\new_test_document.md"
@"
# New Test Document
This document was created during testing.

## Purpose
Testing change detection capabilities of Nancy directory ingestion system.

## Content
This file contains information about:
- Hash-based change detection
- File state management
- Four-brain architecture integration

Author: Test Suite
Created: $(Get-Date)
"@ | Out-File -FilePath $newFileName -Encoding UTF8

# Second scan - should detect new file
Start-Sleep -Seconds 1
$changeDetectionScan2 = Invoke-NancyAPI -Endpoint "/api/directory/scan" -Method "POST" -Body $scanBody
if ($changeDetectionScan2 -and $changeDetectionScan2.new_files -gt 0) {
    Write-Host "SUCCESS: Change detection working - detected new file" -ForegroundColor Green
} else {
    Write-Host "FAILED: Change detection not working properly" -ForegroundColor Red
}

# Summary
Write-Host "`n=== Test Summary ===" -ForegroundColor Green
Write-Host "Directory Ingestion Test Suite Completed" -ForegroundColor Yellow

if ($statusResult -and $statusResult.configured_directories -gt 0) {
    Write-Host "✓ Directory configuration: WORKING" -ForegroundColor Green
} else {
    Write-Host "✗ Directory configuration: FAILED" -ForegroundColor Red
}

if ($scanSuccess) {
    Write-Host "✓ Directory scanning: WORKING" -ForegroundColor Green
} else {
    Write-Host "✗ Directory scanning: FAILED" -ForegroundColor Red
}

if ($combinedResult -and $combinedResult.files_processed -gt 0) {
    Write-Host "✓ File processing: WORKING" -ForegroundColor Green
} else {
    Write-Host "✗ File processing: FAILED" -ForegroundColor Red
}

if ($changeDetectionScan2 -and $changeDetectionScan2.new_files -gt 0) {
    Write-Host "✓ Change detection: WORKING" -ForegroundColor Green
} else {
    Write-Host "✗ Change detection: FAILED" -ForegroundColor Red
}

Write-Host "`nTest directory preserved at: $TEST_DIRECTORY" -ForegroundColor Blue
Write-Host "You can inspect the files and run additional tests as needed." -ForegroundColor Blue
Write-Host "`nFor cleanup, you can remove the test directory:" -ForegroundColor Gray
Write-Host "Remove-Item -Path '$TEST_DIRECTORY' -Recurse -Force" -ForegroundColor Gray