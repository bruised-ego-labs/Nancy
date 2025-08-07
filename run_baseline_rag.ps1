#!/usr/bin/env pwsh
# Start the LangChain + ChromaDB Baseline RAG System

Write-Host "🚀 Starting Baseline RAG System..." -ForegroundColor Green
Write-Host "Framework: LangChain + ChromaDB + Ollama/Gemma" -ForegroundColor Cyan

# Check if Docker services are running
Write-Host "Checking Docker services..." -ForegroundColor Yellow
$dockerServices = docker-compose ps --services --filter status=running
if ($dockerServices -notcontains "chromadb" -or $dockerServices -notcontains "ollama") {
    Write-Host "❌ Required Docker services not running. Starting them..." -ForegroundColor Red
    docker-compose up -d chromadb ollama
    Start-Sleep -Seconds 10
}

# Install baseline requirements
Write-Host "Installing baseline requirements..." -ForegroundColor Yellow
Set-Location baseline-rag
pip install -r requirements.txt

# Start the baseline system
Write-Host "Starting baseline RAG server on port 8001..." -ForegroundColor Green
python main.py

Set-Location ..