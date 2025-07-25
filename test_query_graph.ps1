# Define the API endpoint
$uri = "http://localhost:8000/api/query/graph"

# Define the author to query for
$author = "Scott"

# Create the request body
$body = @{
    author_name = $author
} | ConvertTo-Json

# Print the request details
Write-Host "Attempting to query '$uri' for documents by '$author'..."
Write-Host $body

try {
    # Send the POST request
    $response = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType "application/json"
    
    # Print the successful response
    Write-Host "Query successful!"
    Write-Host "Response:"
    Write-Host ($response | ConvertTo-Json -Depth 5)
}
catch {
    # Print the error details
    Write-Host "An error occurred:"
    Write-Host $_.Exception.Message
}
