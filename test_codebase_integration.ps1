# PowerShell script to test Nancy's Codebase Analysis capabilities
# Tests AST parsing, Git integration, and Four-Brain Architecture integration
# Follows Nancy's existing test script patterns

param(
    [string]$RepoPath = "",
    [string]$TestDirectory = "nancy-services",
    [switch]$Verbose,
    [switch]$SaveResults
)

Write-Host "🚀 Nancy Codebase Analysis Integration Test" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python available: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python and ensure it's in your PATH." -ForegroundColor Red
    exit 1
}

# Check if we're in the correct directory
if (-not (Test-Path "nancy-services")) {
    Write-Host "❌ nancy-services directory not found. Please run this script from the Nancy project root." -ForegroundColor Red
    exit 1
}

Write-Host "📂 Working directory: $(Get-Location)" -ForegroundColor Yellow

# Build the Python command
$pythonArgs = @()
$pythonArgs += "test_codebase_analysis.py"

if ($RepoPath -ne "") {
    $pythonArgs += "--repo-path", $RepoPath
}

if ($TestDirectory -ne "") {
    $pythonArgs += "--test-directory", $TestDirectory
}

if ($SaveResults) {
    $pythonArgs += "--save-results"
}

# Set verbosity
if ($Verbose) {
    $env:PYTHONVERBOSE = "1"
}

Write-Host ""
Write-Host "🔧 Test Configuration:" -ForegroundColor Yellow
Write-Host "  Repository Path: $(if ($RepoPath -eq '') { '(current directory)' } else { $RepoPath })" -ForegroundColor Gray
Write-Host "  Test Directory: $TestDirectory" -ForegroundColor Gray
Write-Host "  Save Results: $SaveResults" -ForegroundColor Gray
Write-Host "  Verbose Mode: $Verbose" -ForegroundColor Gray
Write-Host ""

# Run the test
Write-Host "🎯 Starting Codebase Analysis Tests..." -ForegroundColor Cyan
Write-Host ""

try {
    $startTime = Get-Date
    
    # Execute the Python test script
    & python @pythonArgs
    $exitCode = $LASTEXITCODE
    
    $endTime = Get-Date
    $duration = $endTime - $startTime
    
    Write-Host ""
    Write-Host "⏱️  Test Duration: $($duration.TotalSeconds.ToString('F2')) seconds" -ForegroundColor Gray
    
    if ($exitCode -eq 0) {
        Write-Host "🎉 All codebase analysis tests PASSED!" -ForegroundColor Green
        Write-Host ""
        Write-Host "✨ Nancy's codebase ingestion capabilities are working correctly:" -ForegroundColor Green
        Write-Host "   • AST parsing for multiple programming languages" -ForegroundColor White
        Write-Host "   • Git repository analysis and authorship tracking" -ForegroundColor White
        Write-Host "   • Four-Brain Architecture integration" -ForegroundColor White
        Write-Host "   • Code relationship extraction and storage" -ForegroundColor White
        Write-Host "   • Advanced codebase queries and statistics" -ForegroundColor White
        Write-Host ""
        Write-Host "🔍 You can now use Nancy to analyze entire source code repositories!" -ForegroundColor Cyan
        Write-Host "   Example queries Nancy can now answer:" -ForegroundColor Cyan
        Write-Host "   • 'Who wrote the authentication module?'" -ForegroundColor White
        Write-Host "   • 'What functions handle error logging?'" -ForegroundColor White
        Write-Host "   • 'Which components depend on the database layer?'" -ForegroundColor White
        Write-Host "   • 'Show me the class hierarchy for the API components'" -ForegroundColor White
        
    } elseif ($exitCode -eq 1) {
        Write-Host "⚠️  Some codebase analysis tests FAILED" -ForegroundColor Yellow
        Write-Host "Check the detailed output above for specific issues." -ForegroundColor Yellow
        
    } elseif ($exitCode -eq 130) {
        Write-Host "⏹️  Tests were interrupted by user" -ForegroundColor Blue
        
    } else {
        Write-Host "💥 Test execution failed with exit code: $exitCode" -ForegroundColor Red
    }
    
    # Show log files if they exist
    $logFiles = Get-ChildItem -Name "codebase_analysis_test_results_*.json" -ErrorAction SilentlyContinue | Sort-Object CreationTime -Descending | Select-Object -First 1
    if ($logFiles) {
        Write-Host ""
        Write-Host "📋 Detailed test results saved to: $logFiles" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "💥 Failed to execute test script: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "📚 For more information about Nancy's codebase analysis capabilities:" -ForegroundColor Cyan
Write-Host "   • Check the enhanced ingestion.py for implementation details" -ForegroundColor White
Write-Host "   • Review knowledge_graph.py for code-specific relationship types" -ForegroundColor White
Write-Host "   • See requirements.txt for the tree-sitter and GitPython dependencies" -ForegroundColor White

exit $exitCode