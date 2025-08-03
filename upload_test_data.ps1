# Upload test data for enhanced demo
$testFiles = @(
    @{file="benchmark_test_data\system_requirements_v2.txt"; author="Sarah Chen"},
    @{file="benchmark_test_data\thermal_constraints_doc.txt"; author="Sarah Chen"},
    @{file="benchmark_test_data\electrical_review_meeting.txt"; author="Mike Rodriguez"},
    @{file="benchmark_test_data\emc_test_results.txt"; author="Mike Rodriguez"},
    @{file="benchmark_test_data\voice_of_customer.txt"; author="Lisa Park"},
    @{file="benchmark_test_data\ergonomic_analysis.txt"; author="Lisa Park"},
    @{file="benchmark_test_data\march_design_review_transcript.txt"; author="Jennifer Adams"},
    @{file="benchmark_test_data\power_analysis_report.txt"; author="Tom Wilson"},
    @{file="benchmark_test_data\firmware_requirements.txt"; author="Tom Wilson"}
)

foreach ($test in $testFiles) {
    Write-Host "Uploading $($test.file) by $($test.author)..."
    
    try {
        $boundary = [System.Guid]::NewGuid().ToString()
        $LF = "`r`n"
        
        $fileContent = [System.IO.File]::ReadAllText($test.file)
        $fileName = Split-Path $test.file -Leaf
        
        $bodyLines = @(
            "--$boundary",
            "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
            "Content-Type: application/octet-stream$LF",
            $fileContent,
            "--$boundary",
            "Content-Disposition: form-data; name=`"author`"$LF",
            $test.author,
            "--$boundary--"
        )
        $body = $bodyLines -join $LF
        
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/ingest" -Method Post -Body $body -ContentType "multipart/form-data; boundary=`"$boundary`""
        Write-Host "Success: $($response.status)" -ForegroundColor Green
    }
    catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host "`nTest data upload completed!"