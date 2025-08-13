# This script sends a test file to the Nancy API's ingest endpoint.

$ErrorActionPreference = "Stop"

try {
    $file = 'C:\Users\scott\Documents\Nancy\test.txt'
    $uri = 'http://localhost:8000/api/ingest'
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"

    # Construct the multipart form data body
    $body = (
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$(Split-Path $file -Leaf)`"",
        "Content-Type: application/octet-stream$LF",
        [System.IO.File]::ReadAllText($file),
        "--$boundary--"
    ) -join $LF

    Write-Host "Attempting to upload '$file' to '$uri'..."

    # Send the request
    $response = Invoke-RestMethod -Uri $uri -Method Post -ContentType "multipart/form-data; boundary=`"$boundary`"" -Body $body

    Write-Host "Upload successful!"
    Write-Host "Response:"
    $response | ConvertTo-Json
}
catch {
    Write-Host "An error occurred:"
    Write-Host $_.Exception.Message
}
