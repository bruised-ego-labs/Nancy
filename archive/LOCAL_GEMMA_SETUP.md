# Local Gemma Setup for Nancy Four-Brain Architecture

Nancy now features a complete **Four-Brain Architecture** with local Gemma models for **zero-cost, private LLM operations**! This guide shows you how the local LLM integration works and how to customize it for your needs.

## Benefits of Local Gemma

✅ **Zero Token Costs** - No charges for LLM operations  
✅ **Complete Privacy** - Data never leaves your machine  
✅ **No Rate Limits** - Process as many documents as needed  
✅ **Consistent Performance** - No API downtime or throttling  
✅ **Specialized Models** - Optimize for your specific use case  

## ✅ Already Setup! (Current Implementation)

The Nancy Four-Brain Architecture comes **pre-configured** with local Gemma integration:

### Current Configuration
```bash
# .env file (already configured):
LOCAL_MODEL_NAME="gemma:2b"
OLLAMA_HOST="http://ollama:11434"  # Containerized Ollama service
```

### Ready-to-Use Setup
```bash
# Simply run the setup script:
.\setup_ollama.ps1

# Or manually start services:
docker-compose up -d
```

### What's Already Working
✅ **Ollama Service**: Containerized as the fourth brain  
✅ **Gemma 2B Model**: Pre-configured (~1.6GB, uses ~4GB RAM)  
✅ **LLM Client**: Full integration with fallback support  
✅ **Document Processing**: Relationship extraction with local LLM  
✅ **Query Analysis**: Intent analysis using local Gemma  
✅ **Response Synthesis**: Natural language responses (when enabled)

## Option 2: Direct Transformers (More Control)

### 1. Update Requirements
```bash
# Uncomment in requirements.txt:
torch
transformers

# Rebuild container:
docker-compose down  
docker-compose up -d --build
```

### 2. Configuration Options
```bash
# .env file options:
LOCAL_MODEL_NAME="google/gemma-2-2b-it"  # 2B model
# LOCAL_MODEL_NAME="google/gemma-2-9b-it"  # 9B model for better quality
```

## Option 3: Docker Ollama (Containerized)

Add to your `docker-compose.yml`:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_MODELS=/root/.ollama/models

volumes:
  ollama_data:
```

Then run:
```bash
docker-compose up -d ollama
docker-compose exec ollama ollama pull gemma2:2b
```

## Usage Examples

### Document Ingestion with Local LLM
```bash
# Upload document - will use local Gemma for relationship extraction
curl -X POST "http://localhost:8000/api/ingest" \
  -F "file=@technical_document.txt" \
  -F "author=Engineer Name"
```

### Query Analysis with Local LLM  
```bash
# Query strategy analysis using local Gemma
curl -X POST "http://localhost:8000/api/query/test-strategy" \
  -H "Content-Type: application/json" \
  -d '{"query": "thermal issues affecting electrical design"}'
```

## Performance Characteristics

| Model | Size | RAM Usage | Speed | Quality |
|-------|------|-----------|-------|---------|
| gemma2:2b | 1.6GB | ~4GB | Fast | Good |
| gemma2:9b | 5.4GB | ~12GB | Medium | Better |
| gemma:2b | 1.4GB | ~3GB | Fastest | Good |

## Expected Token Usage (Local = Free!)

### Current Nancy Operations:
- **Document Relationship Extraction**: ~1500-3000 tokens/document → **FREE**
- **Query Intent Analysis**: ~500-800 tokens/query → **FREE**  
- **Response Synthesis**: ~1000-2000 tokens/query → **FREE**

### Estimated Monthly Savings:
- Processing 1000 documents: ~$15-30 saved
- 10,000 queries: ~$5-15 saved
- **Total: $20-45+ monthly savings with zero compromise on functionality**

## Troubleshooting

### Ollama Not Found
```bash
# Check Ollama is running
ollama list

# Check Nancy can reach Ollama
curl http://localhost:11434/api/tags
```

### Memory Issues
```bash
# For low-memory systems, use smaller models:
LOCAL_MODEL_NAME="gemma:2b"  # Uses ~3GB RAM instead of 4GB
```

### Performance Optimization
```bash
# For GPU acceleration (if available):
# Ollama automatically uses GPU when available
# Transformers will use CUDA if torch detects GPU
```

## Integration Status

✅ **Four-Brain Architecture** - Complete with local LLM as fourth brain  
✅ **LLM Client Implemented** - Full local Gemma integration with fallbacks  
✅ **Containerized Ollama** - Runs as separate Docker service  
✅ **Token Logging** - Tracks all local inference usage  
✅ **Production Ready** - Robust error handling and fallback systems  
✅ **Zero-Cost Operations** - All LLM processing happens locally  

## Current Performance (Live System)

Based on actual usage:
- **Document Relationship Extraction**: ~1,112 tokens processed per document → **FREE**
- **Query Intent Analysis**: ~400-800 tokens per query → **FREE**  
- **Response Synthesis**: ~800-1,500 tokens per response → **FREE**
- **Processing Time**: ~2-3 minutes for complex document analysis
- **Memory Usage**: ~4GB RAM for Gemma 2B model

## Verification Commands

```bash
# Check all four brains are running:
docker-compose ps

# Verify Ollama models:
curl http://localhost:11434/api/tags

# Test Nancy API:
curl http://localhost:8000/health

# Monitor local LLM usage:
docker-compose logs api | grep "Local Ollama"
```

Your Nancy Four-Brain Architecture is **ready to use** with complete privacy and zero token costs!