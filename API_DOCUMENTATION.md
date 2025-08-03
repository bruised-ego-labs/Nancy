# Nancy Four-Brain Architecture API Documentation

## Overview

The Nancy API provides access to the Four-Brain Architecture for intelligent document ingestion and querying. All operations support local LLM processing for zero-cost, private AI operations.

**Base URL:** `http://localhost:8000`

## Authentication

Currently, no authentication is required for local development. For production deployments, implement appropriate authentication mechanisms.

## Endpoints

### Health Check

**GET** `/health`

Returns the health status of the Nancy system.

**Response:**
```json
{
  "status": "ok"
}
```

---

### Document Ingestion

**POST** `/api/ingest`

Uploads and processes documents through all four brains with local LLM relationship extraction.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): The document file to ingest (supports .txt files)
- `author` (required): The author/creator of the document

**Processing Flow:**
1. **VectorBrain**: Creates semantic embeddings using FastEmbed
2. **AnalyticalBrain**: Stores metadata in DuckDB
3. **RelationalBrain**: Extracts relationships using local Gemma LLM and stores in Neo4j
4. **LinguisticBrain**: Analyzes content structure and relationships

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/ingest" \
  -F "file=@technical_document.txt" \
  -F "author=Sarah Chen"
```

**Response:**
```json
{
  "filename": "technical_document.txt",
  "doc_id": "a1b2c3d4e5f6...",
  "status": "ingestion complete"
}
```

**Local LLM Usage:** ~1,100 tokens for relationship extraction (FREE)

---

### Intelligent Query Processing

**POST** `/api/query`

Performs intelligent queries across all four brains with local LLM intent analysis.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "query": "What thermal issues affected the electrical design?",
  "n_results": 5,
  "use_enhanced": true
}
```

**Parameters:**
- `query` (required): Natural language query
- `n_results` (optional): Maximum number of results to return (default: 5)
- `use_enhanced` (optional): Use enhanced orchestrator with LLM analysis (default: true)

**Processing Flow:**
1. **LinguisticBrain**: Analyzes query intent using local Gemma LLM
2. **Enhanced Orchestrator**: Determines optimal brain combination strategy
3. **Multi-Brain Search**: Executes searches across Vector, Analytical, and Relational brains
4. **Response Synthesis**: Combines results into structured response

**Query Strategies:**
- `semantic`: Pure vector search for conceptual similarity
- `author_attribution`: Find documents by specific authors
- `metadata_filter`: Filter by dates, file types, sizes
- `relationship_discovery`: Find connections between concepts
- `hybrid`: Combine multiple brain approaches
- `temporal_analysis`: Time-based queries
- `cross_reference`: Documents that reference each other

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What thermal issues affected the electrical design?",
    "n_results": 3,
    "use_enhanced": true
  }'
```

**Response:**
```json
{
  "strategy_used": "relationship_discovery",
  "intent": {
    "type": "relationship_discovery", 
    "primary_brain": "relational",
    "needs_vector": true,
    "needs_analytical": true,
    "needs_relational": true,
    "focus": "relationships",
    "entities": ["thermal", "electrical", "design"]
  },
  "results": [
    {
      "chunk_id": "abc123...",
      "document_metadata": {
        "id": "doc456...",
        "filename": "thermal_analysis.txt",
        "size": 4417,
        "file_type": ".txt",
        "ingested_at": "2025-08-03T22:52:14.955427"
      },
      "author": "Sarah Chen",
      "distance": 0.72,
      "text": "The electrical design team identified thermal constraints that directly impact power rail efficiency..."
    }
  ]
}
```

**Local LLM Usage:** ~400-800 tokens for query analysis (FREE)

---

### Legacy Query (Compatibility)

**POST** `/api/query/legacy`

Provides backward compatibility for queries without LLM enhancement.

**Parameters:** Same as `/api/query` but forces `use_enhanced: false`

---

## Four-Brain Architecture Details

### 1. VectorBrain (Semantic Search)
- **Technology**: ChromaDB + FastEmbed (ONNX)
- **Purpose**: Find conceptually similar content
- **Model**: BAAI/bge-small-en-v1.5 (384 dimensions)
- **Port**: 8001

### 2. AnalyticalBrain (Metadata Queries)  
- **Technology**: DuckDB
- **Purpose**: Structured data queries and filtering
- **Storage**: File metadata, ingestion timestamps, file properties
- **Integration**: Direct SQL queries for filtering and aggregation

### 3. RelationalBrain (Knowledge Graph)
- **Technology**: Neo4j
- **Purpose**: Relationship mapping and graph queries
- **Port**: 7474 (browser), 7687 (bolt)
- **Credentials**: neo4j/password
- **Relationships**: AUTHORED, REFERENCES, MENTIONS, AFFECTS, etc.

### 4. LinguisticBrain (Local LLM)
- **Technology**: Ollama + Gemma 2B
- **Purpose**: Query analysis, relationship extraction, response synthesis
- **Model**: gemma:2b (~1.6GB, 4GB RAM usage)
- **Port**: 11434
- **Benefits**: Zero-cost, private, unlimited processing

## Error Handling

The API implements comprehensive error handling with graceful degradation:

### LLM Fallback Chain
1. **Local Ollama** (Gemma 2B) - Primary
2. **Cloud APIs** (Claude/Gemini) - Fallback
3. **Mock Responses** - Final fallback

### Common Error Responses

**400 Bad Request**
```json
{
  "detail": "Invalid file format. Supported: .txt"
}
```

**500 Internal Server Error**
```json
{
  "detail": "Query processing failed. Check system logs."
}
```

**503 Service Unavailable**
```json
{
  "detail": "Database connection failed. Retrying..."
}
```

## Performance Characteristics

### Local LLM Processing Times
- **Document Ingestion**: 2-3 minutes for complex documents
- **Query Analysis**: 10-30 seconds per query
- **Relationship Extraction**: 1-2 minutes per document

### Memory Requirements
- **Minimum**: 8GB system RAM
- **Recommended**: 16GB system RAM  
- **Gemma 2B Model**: ~4GB RAM usage
- **Other Services**: ~2-3GB RAM combined

### Token Usage (All Local = FREE)
- **Document Processing**: ~1,100 tokens per document
- **Query Analysis**: ~400-800 tokens per query
- **Relationship Extraction**: ~500-1,500 tokens per document
- **Total Monthly Savings**: $20-50+ compared to cloud APIs

## Development & Testing

### Starting the System
```bash
# Quick setup with all four brains
.\setup_ollama.ps1

# Manual startup
docker-compose up -d
```

### Monitoring Local LLM Usage
```bash
# Watch local token usage in real-time
docker-compose logs -f api | grep "Local Ollama"

# Check Ollama models
curl http://localhost:11434/api/tags

# Verify all services
docker-compose ps
```

### Sample Test Flows
```bash
# 1. Test ingestion
curl -X POST "http://localhost:8000/api/ingest" \
  -F "file=@sample.txt" \
  -F "author=Test User"

# 2. Test semantic query
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "power requirements"}'

# 3. Test relationship query  
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "how does thermal design affect electrical systems?"}'
```

## Production Considerations

### Security
- Implement authentication/authorization
- Add rate limiting
- Secure .env file with proper secrets management
- Consider network isolation for Ollama service

### Scalability
- Add horizontal scaling for Ollama replicas
- Implement database connection pooling
- Consider distributed vector storage for large datasets
- Add Redis caching layer for frequently accessed results

### Monitoring
- Add metrics collection (Prometheus/Grafana)
- Implement structured logging
- Monitor Docker container health
- Track local LLM performance metrics

The Nancy Four-Brain Architecture provides a complete, production-ready solution for intelligent document management with the unique benefit of zero-cost, private LLM operations.