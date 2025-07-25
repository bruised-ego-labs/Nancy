# Define the API endpoint
$uri = "http://localhost:8000/api/query"

# Define the query
#$query = "what is chromadb used for?"
$query = "the hidden tax of context-switching"
$n_results = 10

# Create the request body
$body = @{
    query = $query
    n_results = $n_results
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
