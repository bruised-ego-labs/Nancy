# This script provides a reliable way to reset the development environment to a clean state.
# It stops all services, removes persistent Docker volumes, and clears local database files.

Write-Host "--- Starting Development Data Reset ---" -ForegroundColor Yellow

# Step 1: Stop all running containers and remove their volumes
Write-Host "Stopping containers and removing persistent volumes (ChromaDB, Neo4j)..."
docker-compose down -v
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to run 'docker-compose down -v'. Please check your Docker installation and try again." -ForegroundColor Red
    exit 1
}
Write-Host "Containers and volumes removed successfully." -ForegroundColor Green

# Step 2: Delete local DuckDB files
Write-Host "Deleting local DuckDB files (project_nancy.duckdb and project_nancy.duckdb.wal)..."
Remove-Item -Path "./data/project_nancy.duckdb*" -Force -ErrorAction SilentlyContinue
Write-Host "Local DuckDB files cleared." -ForegroundColor Green

Write-Host "--- Development Data Reset Complete ---" -ForegroundColor Yellow
Write-Host "You can now start the services with 'docker-compose up -d --build'"
