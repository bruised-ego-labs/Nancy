# Upload script for additional test documents
# This demonstrates ingesting different types of content with different authors

param(
    [string]$ApiUrl = "http://localhost:8000/api/ingest"
)

Write-Host "Uploading additional test documents to demonstrate three-brain system..." -ForegroundColor Green

# Document 1: Database Performance Report by Sarah Johnson
$file1 = "database_performance_report.md"
$author1 = "Sarah Johnson"

if (Test-Path $file1) {
    Write-Host "Uploading $file1 by $author1..." -ForegroundColor Yellow
    try {
        $form1 = @{
            file = Get-Item $file1
            author = $author1
        }
        Invoke-RestMethod -Uri $ApiUrl -Method Post -Form $form1
        Write-Host "✅ Successfully uploaded $file1" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error uploading $file1`: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️ File $file1 not found" -ForegroundColor Yellow
}

Start-Sleep -Seconds 2

# Document 2: Meeting Notes by Scott
$file2 = "meeting_notes_architecture_review.md"
$author2 = "Scott"

if (Test-Path $file2) {
    Write-Host "Uploading $file2 by $author2..." -ForegroundColor Yellow
    try {
        $form2 = @{
            file = Get-Item $file2
            author = $author2
        }
        Invoke-RestMethod -Uri $ApiUrl -Method Post -Form $form2
        Write-Host "✅ Successfully uploaded $file2" -ForegroundColor Green
    } catch {
        Write-Host "❌ Error uploading $file2`: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "⚠️ File $file2 not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📊 Test Data Summary:" -ForegroundColor Cyan
Write-Host "- README.md (Scott): Project overview and vision"
Write-Host "- database_performance_report.md (Sarah Johnson): Technical analysis" 
Write-Host "- meeting_notes_architecture_review.md (Scott): Team collaboration record"
Write-Host "- test2.txt (Scott): Development session logs"
Write-Host ""
Write-Host "This diverse dataset allows testing of:" -ForegroundColor White
Write-Host "✓ Multi-author queries (Scott vs Sarah Johnson)" -ForegroundColor White
Write-Host "✓ Different document types (.md vs .txt)" -ForegroundColor White
Write-Host "✓ Various content themes (vision, technical, collaboration)" -ForegroundColor White
Write-Host "✓ Time-based queries (recent uploads)" -ForegroundColor White
Write-Host "✓ Relationship exploration (author connections)" -ForegroundColor White
