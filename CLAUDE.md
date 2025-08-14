# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Project Nancy is a collaborative AI librarian using a **"Four-Brain" architecture** with **LangChain router orchestration** and **multi-step query processing** to create intelligent knowledge bases. It combines specialized data stores with intelligent routing:

- **Vector Brain (ChromaDB + FastEmbed)**: Semantic search using ONNX-based BAAI/bge-small-en-v1.5 embeddings
- **Analytical Brain (DuckDB)**: Structured metadata storage for files, statistics, and document properties
- **Graph Brain (Neo4j)**: Enhanced knowledge graph with **foundational relationship schema** supporting people & organization, technical subsystems, and project management relationships
- **Linguistic Brain (Gemma 3n-e4b-it)**: Intelligent query analysis, routing, and response synthesis via Google AI API

The system uses **LangChain MultiPromptChain routing** with **multi-step processing** for complex queries requiring both semantic content and relationship analysis.

## Development Commands

### Environment Setup
```bash
# Start all services (Nancy API, ChromaDB, Neo4j, Baseline RAG)
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
# Test file ingestion with author attribution
.\test_upload_2.ps1

# Test intelligent querying with multi-step processing
.\test_query_2.ps1

# Run comprehensive benchmark (Nancy vs Baseline RAG)
.\test_benchmark_docker.ps1

# Demo four-brain architecture capabilities
.\test_four_brain_demo.ps1

# Demo enhanced graph brain with relationship schema
.\test_enhanced_three_brain_demo.ps1
```

### Service Access
- Nancy API: http://localhost:8000
- Baseline RAG API: http://localhost:8002
- ChromaDB: http://localhost:8001
- Neo4j Browser: http://localhost:7474 (neo4j/password)
- Nancy API Documentation: http://localhost:8000/docs

## Current Architecture (LangChain Router + Enhanced Relationships)

### Core Components
- `nancy-services/api/main.py`: FastAPI application entry point with health checks
- `nancy-services/core/langchain_orchestrator.py`: **LangChain router with multi-step query processing**
- `nancy-services/core/knowledge_graph.py`: **Enhanced graph brain with foundational relationship schema**
- `nancy-services/core/ingestion.py`: Multi-brain file processing and storage
- `nancy-services/core/nlp.py`: Vector brain implementation using FastEmbed
- `nancy-services/core/search.py`: Analytical brain (DuckDB operations)
- `nancy-services/core/llm_client.py`: **Gemma 3n-e4b-it integration via Google AI API**

### Key Architecture Features
- **Multi-Step Query Processing**: Detects complex queries needing both content and relationship analysis
- **Enhanced Graph Relationships**: Beyond simple authorship - expertise, technical systems, decisions
- **LangChain Router Integration**: Deterministic brain selection with fallback support
- **Baseline Comparison**: Standard LangChain + ChromaDB RAG system for benchmarking

### API Endpoints
- `POST /api/ingest`: Upload files with author attribution and multi-brain processing
- `POST /api/query`: Intelligent natural language querying with multi-step processing
- `GET /health`: Service health check across all brains

### Data Storage
- `./data/`: Persistent storage mounted to containers (Git-ignored)
- `./nancy-services/data/`: Container placeholder (Git-tracked)
- `./archive/`: Old files and deprecated scripts (Git-tracked)
- DuckDB file: `./data/project_nancy.duckdb`

### Enhanced Query Processing Flow

**Single-Step Queries:**
1. LangChain router analyzes query intent
2. Routes to appropriate brain (vector/analytical/graph)
3. Brain executes specialized logic
4. Gemma 3n-e4b-it synthesizes natural language response

**Multi-Step Queries (Complex):**
1. System detects multi-step need (e.g., "What are thermal constraints and who are the experts?")
2. Vector brain finds relevant content
3. Graph brain explores contextual relationships
4. Gemma 3n-e4b-it synthesizes comprehensive response combining both

### Foundational Relationship Schema
```cypher
// People & Organization
(Person)-[:HAS_EXPERTISE]->(Domain)
(Person)-[:HAS_ROLE]->(Role)
(Person)-[:MEMBER_OF]->(Team)
(Person)-[:MADE]->(Decision)
(Person)-[:ATTENDED]->(Meeting)

// Technical Subsystems
(Component)-[:PART_OF]->(System)
(System)-[:INTERFACES_WITH]->(System)
(Component)-[:CONSTRAINED_BY]->(Constraint)
(Decision)-[:AFFECTS]->(Component)

// Project Management
(Decision)-[:VALIDATED_BY]->(Process)
(Document)-[:PRODUCED]->(Deliverable)
(Risk)-[:MITIGATED_BY]->(Action)
(Meeting)-[:RESULTED_IN]->(Decision)
```

## Development Workflow & Patterns

### Our Collaborative Development Approach

**Planning & Implementation:**
1. **Use TodoWrite tool extensively** for task planning and progress tracking
2. **Mark tasks as in_progress before starting** and completed immediately after finishing
3. **Implement incrementally** - complete one feature before moving to the next
4. **Test each component** after implementation before moving on

**Code Organization:**
- **Archive old/unused files** regularly to keep repository clean
- **Preserve recently used scripts** like `comprehensive_benchmark_with_metrics.py`
- **Update documentation** (README.md, CLAUDE.md) after major changes
- **Keep active development files** easily accessible

**Testing Strategy:**
- **Always test individual brains** before integration
- **Use benchmark system** to validate improvements
- **Compare Nancy vs Baseline RAG** for performance measurement
- **Document benchmark results** in JSON files with timestamps

### LLM and API Integration

**Current Model: Gemma 3n-e4b-it via Google AI API**
- Lightweight, fast model for routing and synthesis
- Requires `GEMINI_API_KEY` environment variable
- Used across Nancy system and baseline for fair comparison
- Integrated via custom LangChain LLM wrapper classes

**Fallback Strategy:**
- Cloud API (Google AI) → Local model → Mock responses
- Robust error handling and graceful degradation

## File Processing

### Supported File Types
**Text-based files** (.txt, .md, .log, .py, .js, .html, .css, .json) get full processing:
- Vector embedding and chunking via FastEmbed
- Metadata storage in DuckDB
- Author attribution and relationship extraction for Neo4j
- Named entity recognition using spaCy (when available)

**Spreadsheet files** (.xlsx, .csv) with **foundational architecture** implemented:
- Document metadata and author attribution in Graph Brain
- Basic file storage in Analytical Brain
- **Full structured data processing** (requires completion of implementation plan in `SPREADSHEET_IMPLEMENTATION_PLAN.md`)

Binary files receive metadata-only storage.

### Ingestion Flow
1. Generate unique doc_id from filename and content hash
2. Store file metadata in DuckDB (Analytical Brain)
3. Create document and author nodes in Neo4j (Graph Brain)
4. For text files: chunk, embed, and store in ChromaDB (Vector Brain)
5. Extract relationships for foundational schema (enhanced Graph Brain)
6. **For spreadsheets**: Process structured data through enhanced four-brain integration

## Spreadsheet Ingestion Capabilities

### Current Architecture Status
Nancy includes **foundational spreadsheet ingestion architecture** designed for engineering teams where legacy and current data is stored in spreadsheets (financial data, project management, test data, training data, etc.).

### Four-Brain Spreadsheet Integration
**Analytical Brain (DuckDB)**: Direct tabular data storage using pandas for SQL querying
- Spreadsheet registry for tracking all tables and sheets
- Advanced query capabilities with `query_spreadsheet_data()` and `search_spreadsheet_content()`
- Enhanced document metadata with spreadsheet-specific information

**Graph Brain (Neo4j)**: Column relationships and formula dependencies
- Document → Sheet → Column relationship hierarchy
- Calculated field dependency detection and categorical value concept nodes
- Mathematical relationship discovery between columns

**Vector Brain (ChromaDB)**: Searchable spreadsheet summaries
- Comprehensive sheet summaries for semantic search with column statistics
- Sample data context for natural language queries and multi-sheet context handling

**Linguistic Brain (Gemma)**: Natural language to structured data queries
- Intelligent routing for spreadsheet-specific queries and cross-brain synthesis for complex analyses

### Implementation Status
✅ **Completed**: Architecture design, enhanced ingestion service, comprehensive analytical brain methods
✅ **Tested**: Basic CSV upload, metadata storage, author attribution through Docker testing
❌ **Pending**: Full structured data processing (see `SPREADSHEET_IMPLEMENTATION_PLAN.md` for completion steps)

### Engineering Team Value
- **Requirements Management**: Track compliance across multiple spreadsheets
- **Test Data Analysis**: Query results across test campaigns with correlation analysis  
- **Component Management**: Analyze supply chain data and specifications
- **Cross-Disciplinary Insights**: Connect data across mechanical, electrical, thermal, and software domains

## Benchmark System

### Running Benchmarks
```powershell
# Primary benchmark command
.\test_benchmark_docker.ps1

# Using active benchmark script
python comprehensive_benchmark_with_metrics.py

# Manual Docker approach
docker cp benchmark_test_data/ nancy-api-1:/app/data/
docker exec nancy-api-1 python /app/run_comprehensive_comparison.py
```

### Benchmark Categories
14 queries across 7 engineering disciplines:
- **Systems Engineering**: Requirements, constraints, author attribution
- **Mechanical Engineering**: CAD integration, materials, stress analysis
- **Electrical Engineering**: Circuit design, EMC compliance, power relationships
- **Firmware Engineering**: Memory requirements, protocols, architecture
- **Industrial Design**: User feedback, ergonomics, interface design
- **Project Management**: Decision tracking, meetings, budget constraints
- **Cross-Disciplinary**: Multi-team dependencies and collaboration analysis

### Performance Improvements (Nancy vs Standard RAG)
Based on comprehensive benchmarking:
- **Author Attribution**: 100% vs 0% (standard RAG has no author capability)
- **Cross-Disciplinary Queries**: 50-80% F1 score improvement
- **Metadata Filtering**: 40-60% recall improvement
- **Relationship Discovery**: 60-90% precision improvement
- **Multi-Step Processing**: Handles complex queries standard RAG cannot

### Evaluation Metrics
- Precision@10, Recall@10, F1 Score
- Mean Reciprocal Rank (MRR)
- Author Attribution Accuracy
- Response Time Analysis
- Discipline-specific Performance Breakdown

## Development Guidelines

### Code Quality
- **Follow existing patterns** in the codebase
- **Use type hints** where appropriate
- **Add docstrings** for new methods and classes
- **Handle errors gracefully** with try/catch blocks
- **Log important operations** for debugging

### Architecture Principles
- **Separation of concerns** - each brain handles specific data types
- **Fail gracefully** - provide fallback responses when components fail
- **Maintain compatibility** - ensure changes don't break existing functionality
- **Document decisions** - update CLAUDE.md and README.md for significant changes

### When Making Changes
1. **Read existing code** to understand current patterns
2. **Use TodoWrite** to plan multi-step changes
3. **Test incrementally** as you implement
4. **Update documentation** after completing features
5. **Run benchmarks** to validate improvements
6. **Archive old files** when they become obsolete

### Environment Variables Required
```bash
# Required for Gemma 3n-e4b-it integration
GEMINI_API_KEY=your_google_ai_api_key

# Optional service configuration
CHROMA_HOST=chromadb
CHROMA_PORT=8001
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Active Files & Scripts

### Current Development Scripts
- `comprehensive_benchmark_with_metrics.py` - Active benchmark system
- `test_benchmark_docker.ps1` - Docker-based benchmarking
- `test_query_2.ps1` - Current query testing
- `test_upload_2.ps1` - Current ingestion testing
- `reset_development_data.ps1` - Environment reset
- `test_spreadsheet_ingestion.py` - Comprehensive spreadsheet testing
- `SPREADSHEET_IMPLEMENTATION_PLAN.md` - Detailed implementation roadmap

### Recent Results
- `comprehensive_benchmark_20250812_142248.json` - Latest benchmark results
- `comprehensive_benchmark_20250812_084013.json` - Previous benchmark

### Archived Items
- Old test scripts, outdated documentation, and deprecated benchmark results have been moved to `./archive/` folder

## Project Status

**Current State**: Production-ready LangChain router architecture with enhanced foundational relationship schema

**Completed Features**:
- ✅ LangChain MultiPromptChain routing with deterministic brain selection
- ✅ Multi-step query processing for complex queries
- ✅ Enhanced graph brain with foundational relationship schema
- ✅ Gemma 3n-e4b-it integration via Google AI API
- ✅ Comprehensive benchmark system vs standard RAG
- ✅ Complete Docker containerization
- ✅ Repository cleanup and documentation updates
- ✅ **Spreadsheet ingestion architecture** (Excel/CSV support for four-brain integration)

**Next Development Areas**:
- **Complete spreadsheet ingestion implementation** (pandas dependency, structured data processing)
- Enhanced document ingestion capabilities (PDF, DOCX support)
- Advanced spreadsheet intelligence (cross-brain queries, data lineage)
- Automated relationship extraction during ingestion