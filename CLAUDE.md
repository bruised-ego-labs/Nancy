# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Project Nancy is a collaborative AI librarian using a "Three-Brain" architecture to create intelligent knowledge bases. It combines three data stores:

- **Vector Brain (ChromaDB + FastEmbed)**: Semantic search using ONNX-based text embeddings
- **Analytical Brain (DuckDB)**: Structured metadata storage for files and documents
- **Relational Brain (Neo4j)**: Knowledge graph storing relationships between documents, people, and concepts

The system is fully containerized with Docker and provides REST API endpoints for file ingestion and intelligent querying.

## Development Commands

### Environment Setup
```bash
# Start all services (API, ChromaDB, Neo4j)
docker-compose up -d --build

# Reset development environment (stops containers, clears all data)
.\reset_development_data.ps1

# Stop services
docker-compose down

# Stop services and remove volumes
docker-compose down -v
```

### Testing Commands
```powershell
# Test file ingestion
.\test_upload_2.ps1

# Test querying
.\test_query_2.ps1

# Advanced query tests
.\test_advanced_queries.ps1

# Three-brain architecture demo
.\test_three_brain_demo.ps1
```

### Service Access
- API Server: http://localhost:8000
- ChromaDB: http://localhost:8001
- Neo4j Browser: http://localhost:7474 (neo4j/password)
- API Documentation: http://localhost:8000/docs

## Architecture Details

### Core Components
- `nancy-services/api/main.py`: FastAPI application entry point
- `nancy-services/core/query_orchestrator.py`: Central intelligence combining all three brains
- `nancy-services/core/ingestion.py`: File processing and multi-brain storage
- `nancy-services/core/nlp.py`: VectorBrain implementation using FastEmbed
- `nancy-services/core/search.py`: AnalyticalBrain (DuckDB operations)
- `nancy-services/core/knowledge_graph.py`: RelationalBrain (Neo4j operations)

### API Endpoints
- `POST /api/ingest`: Upload files with author attribution
- `POST /api/query`: Natural language querying across all brains
- `GET /health`: Service health check

### Data Storage
- `./data/`: Persistent storage mounted to containers (Git-ignored)
- `./nancy-services/data/`: Container placeholder (Git-tracked)
- DuckDB file: `./data/project_nancy.duckdb`

### File Processing
The system supports text-based files (.txt, .md, .log, .py, .js, .html, .css, .json) for full processing including:
- Vector embedding and chunking
- Named entity recognition using spaCy
- Relationship extraction for knowledge graph

Binary files are stored with metadata only (no vector embeddings).

## Development Notes

### Dependencies
- Python 3.9 with FastAPI, uvicorn
- FastEmbed + ONNX for stable CPU-based embeddings (replaces sentence-transformers)
- spaCy with en_core_web_sm model for NLP
- Multi-database stack: ChromaDB, DuckDB, Neo4j

### Container Architecture
The API service depends on ChromaDB and Neo4j services. Environment variables configure service discovery:
- `CHROMA_HOST=chromadb`
- `NEO4J_URI=bolt://neo4j:7687`

### Query Processing Flow
1. Vector search finds semantically similar text chunks
2. DuckDB retrieves document metadata by doc_id
3. Neo4j provides author attribution and relationships
4. Results are synthesized into unified response with text, metadata, and authorship

### Ingestion Flow
1. Generate unique doc_id from filename and content hash
2. Store metadata in DuckDB
3. Create document and author nodes in Neo4j with AUTHORED relationship
4. For text files: chunk, embed, and store in ChromaDB; extract entities for knowledge graph

## Benchmark System

### Running Benchmarks
```powershell
# Run comprehensive three-brain vs standard RAG benchmark
.\test_benchmark_docker.ps1

# Alternative manual approach
docker cp benchmark_test_data/ nancy-api-1:/app/data/
docker cp run_benchmark_docker.py nancy-api-1:/app/
docker exec nancy-api-1 python /app/run_benchmark_docker.py
```

### Benchmark Test Categories
The benchmark includes 14 queries across 7 disciplines:
- **Systems Engineering**: Requirements, constraints, author attribution
- **Mechanical Engineering**: CAD files, materials, stress analysis
- **Electrical Engineering**: Circuits, EMC compliance, design relationships
- **Firmware Engineering**: Memory requirements, protocols, architecture
- **Industrial Design**: User feedback, ergonomics, interface design
- **Project Management**: Decisions, meetings, budget constraints
- **Cross-Disciplinary**: Complex multi-team dependency tracking

### Expected Performance Gains
Three-brain architecture typically shows:
- **Author Attribution**: 100% vs 0% (standard RAG has no author info)
- **Cross-Disciplinary Queries**: 50-80% F1 score improvement
- **Metadata Filtering**: 40-60% recall improvement
- **Relationship Discovery**: 60-90% precision improvement

### Benchmark Evaluation Metrics
- Precision@10, Recall@10, F1 Score, Mean Reciprocal Rank
- Author Attribution Accuracy
- Response Time Analysis
- Discipline-specific Performance Breakdown