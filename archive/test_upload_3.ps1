# Define the API endpoint
$uri = "http://localhost:8000/api/ingest"

# Define the file to upload and the author
$filePath = "C:\Users\scott\Documents\Nancy\test3.txt"
$author = "Scott"

# Create a unique boundary string
$boundary = [System.Guid]::NewGuid().ToString()

# Create the multipart content
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

# Print the request details
Write-Host "Attempting to upload '$filePath' to '$uri' by author '$author'..."

try {
    # Send the POST request
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "multipart/form-data; boundary=`"$boundary`""
    
    # Print the successful response
    Write-Host "Upload successful!"
    Write-Host "Response:"
    Write-Host ($response | ConvertTo-Json -Depth 5)
}
catch {
    # Print the error details
    Write-Host "An error occurred:"
    Write-Host $_.Exception.Message
}
