# Define the API endpoint
$uri = "http://localhost:8000/api/query"

# Define the query
$query = "What documents mention Claude?"

# Create the request body
$body = @{
    query = $query
} | ConvertTo-Json

# Print the request details
Write-Host "Attempting to query '$uri' with body:"
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
