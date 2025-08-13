# Upload benchmark file to Nancy
$uri = "http://localhost:8000/api/ingest"
$filePath = "C:\Users\scott\Documents\Nancy\benchmark_data\electrical_design_review.txt"
$author = "Mike Rodriguez"

# Create boundary and body
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"
$bodyLines = @(
    "--$boundary",
    "Content-Disposition: form-data; name=`"file`"; filename=`"$(Split-Path $filePath -Leaf)`"",
    "Content-Type: application/octet-stream$LF",
    ([System.IO.File]::ReadAllText($filePath)),
    "--$boundary",
    "Content-Disposition: form-data; name=`"author`"$LF",
    $author,
    "--$boundary--"
)
$body = $bodyLines -join $LF

Write-Host "Uploading $(Split-Path $filePath -Leaf) to Nancy..."
$response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "multipart/form-data; boundary=`"$boundary`""
Write-Host ($response | ConvertTo-Json)