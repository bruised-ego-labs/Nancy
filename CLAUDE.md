# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Project Nancy is a **configurable AI orchestration platform** using a **"Four-Brain" architecture** with **MCP (Model Context Protocol) orchestration** and **Knowledge Packet processing** to create intelligent knowledge bases. Nancy has evolved from a monolithic system to a flexible chassis that integrates specialized MCP servers.

**Current Status (August 2025):** Nancy has proven technical superiority (60% query advantage vs standard RAG) but requires enterprise transformation to achieve market adoption. Strategic analysis has identified critical barriers and development priorities for the next 90 days.

### Core Four-Brain Architecture
- **Vector Brain (ChromaDB + FastEmbed)**: Semantic search using ONNX-based BAAI/bge-small-en-v1.5 embeddings
- **Analytical Brain (DuckDB)**: Structured metadata storage for files, statistics, and document properties  
- **Graph Brain (Neo4j)**: Enhanced knowledge graph with **foundational relationship schema** supporting people & organization, technical subsystems, and project management relationships
- **Linguistic Brain (Configurable LLM)**: Intelligent query analysis, routing, and response synthesis via configurable API

### MCP Architecture Benefits
- **Modular Capabilities**: Specialized MCP servers for different data types (spreadsheets, codebase, documents)
- **Configurable Components**: Database and LLM selection through YAML configuration  
- **Horizontal Scaling**: Independent MCP server deployment and scaling
- **Standardized Integration**: Knowledge Packet protocol for seamless Four-Brain routing

The system uses **MCP Host orchestration** with **Knowledge Packet routing** for complex queries requiring both semantic content and relationship analysis across multiple specialized servers.

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

# Test MCP server integrations
python integrate_codebase_mcp.py
python test_codebase_mcp_simple.py

# Benchmark MCP server performance
python benchmark_codebase_mcp.py
```

### Service Access
- Nancy API: http://localhost:8000
- Baseline RAG API: http://localhost:8002
- ChromaDB: http://localhost:8001
- Neo4j Browser: http://localhost:7474 (neo4j/password)
- Nancy API Documentation: http://localhost:8000/docs

## Current Architecture (MCP Orchestration Platform)

### Nancy Core Components
- `nancy-services/api/main.py`: FastAPI application entry point with health checks
- `nancy-services/core/mcp_host.py`: **MCP Host orchestration for external servers**
- `nancy-services/core/knowledge_packet_processor.py`: **Knowledge Packet routing to Four-Brain architecture**
- `nancy-services/core/config_manager.py`: **Configurable database and LLM selection**
- `nancy-services/core/knowledge_graph.py`: Enhanced graph brain with foundational relationship schema
- `nancy-services/core/nlp.py`: Vector brain implementation using FastEmbed
- `nancy-services/core/search.py`: Analytical brain (DuckDB operations)
- `nancy-services/core/llm_client.py`: Configurable LLM integration

### MCP Servers
- `mcp-servers/spreadsheet/server.py`: **Standalone spreadsheet processing MCP server**
- `mcp-servers/codebase/server.py`: **Standalone codebase analysis MCP server with multi-language AST parsing**

### Key Architecture Features
- **MCP Host Orchestration**: Intelligent routing to appropriate MCP servers based on query analysis
- **Knowledge Packet Protocol**: Standardized data structures for Four-Brain integration
- **Configurable Components**: Database and LLM selection through YAML configuration files
- **Enhanced Graph Relationships**: Foundational schema supporting people, organizations, technical systems, and decisions
- **Horizontal Scaling**: Independent MCP server deployment and scaling
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

**MCP Orchestration Process:**
1. **Query Analysis**: Nancy Core analyzes incoming natural language query
2. **Server Routing**: MCP Host routes query to appropriate MCP server(s) based on content type
3. **Knowledge Packet Generation**: MCP servers generate standardized Knowledge Packets
4. **Four-Brain Integration**: Knowledge Packet Processor routes packets to appropriate brains
5. **Response Synthesis**: Configurable LLM synthesizes comprehensive response

**Multi-Step Queries (Complex):**
1. System detects multi-step need (e.g., "What are thermal constraints and who wrote the code?")
2. Multiple MCP servers invoked (codebase analysis + document processing)
3. Vector brain finds relevant content across all sources
4. Graph brain explores relationships across datasets
5. Analytical brain provides structured query capabilities
6. Linguistic brain synthesizes comprehensive response combining all sources

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

**Configurable LLM Architecture:**
- **Default Model**: Gemma 3n-e4b-it via Google AI API for lightweight, fast routing and synthesis
- **Configurable Selection**: YAML-based configuration allows switching between different LLM providers
- **Environment Variables**: Requires appropriate API keys (e.g., `GEMINI_API_KEY` for Google AI)
- **MCP Server Compatibility**: Used across Nancy Core and MCP servers for consistent responses

**Configuration Management:**
- Database selection (ChromaDB, Neo4j, DuckDB alternatives)
- LLM provider configuration (Google AI, OpenAI, local models)
- MCP server registration and capability discovery
- Fallback strategies with graceful degradation

## File Processing

### Supported File Types via MCP Servers

**Text-based files** (.txt, .md, .log) - **Nancy Core**:
- Vector embedding and chunking via FastEmbed
- Metadata storage in DuckDB
- Author attribution and relationship extraction for Neo4j
- Named entity recognition using spaCy (when available)

**Code files** (.py, .js, .java, .go, .rust, .cpp, etc.) - **Codebase MCP Server**:
- Multi-language AST parsing with tree-sitter
- Git authorship analysis and collaboration patterns
- Developer expertise profiling and code ownership tracking
- Function/class extraction with complexity analysis
- Knowledge Packet generation for Four-Brain integration

**Spreadsheet files** (.xlsx, .csv) - **Spreadsheet MCP Server**:
- Structured data processing with pandas integration
- Row-by-row Knowledge Packet generation
- Column metadata analysis and relationship extraction
- Author attribution and document tracking
- Performance: 1,038 rows/sec processing rate

Binary files receive metadata-only storage through Nancy Core.

### MCP-Based Ingestion Flow
1. **Nancy Core Analysis**: Determine appropriate MCP server(s) based on file type
2. **MCP Server Invocation**: Route file to specialized server for processing
3. **Knowledge Packet Generation**: MCP server generates standardized packets
4. **Four-Brain Routing**: Knowledge Packet Processor routes to appropriate brains:
   - Vector Brain: Semantic content (code, text, documentation)
   - Analytical Brain: Structured metadata (metrics, authorship, complexity)
   - Graph Brain: Relationships (functions, classes, authorship, dependencies)
5. **Integration Completion**: All brains updated with coordinated data

## MCP Server Capabilities

### Spreadsheet MCP Server
**Performance Characteristics:**
- **Processing Speed**: 1,038 rows per second
- **Knowledge Packet Generation**: 1,560 packets per second
- **Success Rate**: 100% on structured data processing
- **Multi-format Support**: Excel (.xlsx), CSV (.csv), Google Sheets integration ready

**Four-Brain Integration:**
- **Analytical Brain**: Direct tabular data storage with SQL querying capabilities
- **Graph Brain**: Column relationships, formula dependencies, and data lineage
- **Vector Brain**: Searchable spreadsheet summaries with comprehensive metadata
- **Linguistic Brain**: Natural language to structured data query translation

### Codebase MCP Server  
**Performance Characteristics:**
- **Processing Speed**: 114.52 files per second
- **Knowledge Packet Generation**: 1,061 packets per second
- **Success Rate**: 96.7% across diverse codebases
- **Language Support**: 15+ programming languages with AST parsing

**Advanced Features:**
- **Multi-language AST parsing** with tree-sitter support
- **Git repository analysis** with authorship tracking and collaboration patterns
- **Developer expertise profiling** and code ownership analysis
- **Complexity calculation** and code quality metrics
- **Modern language feature detection** (ES6+, TypeScript, Python asyncio)

### Engineering Team Value
- **Requirements Management**: Track compliance across multiple data sources
- **Code Intelligence**: Understand authorship, complexity, and relationships in codebases
- **Cross-Disciplinary Analysis**: Connect data across mechanical, electrical, thermal, software, and project management domains
- **Developer Collaboration**: Analyze expertise patterns and contribution relationships

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

## Enterprise Development Priorities (Next 30 Days)

### 🔴 Critical Path - Multi-User Foundation
**Priority 1:** Implement basic authentication system using FastAPI-Users
- User registration/login endpoints
- Password hashing and session management
- Basic user model in database

**Priority 2:** Add data isolation across all four brains
- User-scoped data access in ChromaDB collections
- User-specific Neo4j graph namespaces  
- DuckDB table-level access control
- MCP server user context passing

**Priority 3:** Simple permission system
- Admin/User role definitions
- Access control decorators for API endpoints
- User management interface basics

### 🟡 High Priority - Deployment Simplification
**Priority 4:** Single-container deployment option
- Embedded SQLite + FAISS alternative to full database stack
- Dockerfile optimization for <2GB RAM usage
- Environment variable configuration consolidation

**Priority 5:** 5-minute setup experience
- Single `docker run` command deployment
- Auto-configuration for development mode
- Health check endpoints for deployment validation

### 🟢 Medium Priority - Enterprise Basics
**Priority 6:** Audit logging system
- User action tracking (ingestion, queries, access)
- Structured logging with timestamps and user context
- Log rotation and retention policies

## Development Guidelines

### Code Quality (Updated for Enterprise Focus)
- **Security first** - validate all user inputs, implement proper authentication
- **Follow existing patterns** but prioritize enterprise requirements over research features
- **Use type hints** and comprehensive error handling for production readiness
- **Add comprehensive logging** for audit trails and debugging
- **Test multi-user scenarios** alongside existing single-user tests

### Architecture Principles (Enterprise-Focused)
- **Multi-tenancy by design** - all new features must support multiple users
- **Graceful degradation** - system remains functional with partial component failures
- **Configuration over hardcoding** - externalize settings for different deployment environments
- **Security boundaries** - assume malicious users, validate everything
- **Operational visibility** - metrics, health checks, and monitoring integration

### When Making Changes (Enterprise Development)
1. **Security review first** - consider authentication, authorization, and data isolation
2. **Use TodoWrite** extensively for multi-step enterprise features
3. **Test with multiple users** - validate data isolation and permission boundaries
4. **Document deployment changes** - update Docker configurations and environment guides
5. **Customer perspective** - will this reduce or increase adoption friction?

### Environment Variables Required
```bash
# Required for default LLM integration
GEMINI_API_KEY=your_google_ai_api_key

# Optional service configuration
CHROMA_HOST=chromadb
CHROMA_PORT=8001
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# MCP server configuration
MCP_SERVER_CONFIG_PATH=./config/mcp_servers.yaml
```

## Active Files & Scripts

### Current Development Scripts
- `comprehensive_benchmark_with_metrics.py` - Active benchmark system
- `test_benchmark_docker.ps1` - Docker-based benchmarking
- `test_query_2.ps1` - Current query testing
- `test_upload_2.ps1` - Current ingestion testing
- `reset_development_data.ps1` - Environment reset

### MCP Server Testing Scripts  
- `integrate_codebase_mcp.py` - Nancy Core + Codebase MCP integration demonstration
- `test_codebase_mcp_simple.py` - Simplified codebase analysis testing
- `benchmark_codebase_mcp.py` - Performance benchmarking for MCP servers

### Recent Results
- `comprehensive_benchmark_20250812_142248.json` - Latest Nancy vs Baseline RAG results
- `CODEBASE_MCP_EXTRACTION_SUMMARY.md` - Complete codebase MCP server extraction report
- `codebase_mcp_benchmark_*.json` - MCP server performance benchmark results

### Archived Items
- Old test scripts, outdated documentation, and deprecated benchmark results have been moved to `./archive/` folder
- Previous monolithic implementations archived during MCP migration

## Project Status

**Current State**: Production-ready MCP orchestration platform with configurable Four-Brain architecture

**Completed Features**:
- ✅ **MCP Host orchestration** with intelligent server routing and capability discovery
- ✅ **Knowledge Packet protocol** for standardized Four-Brain integration
- ✅ **Configurable components** via YAML-based database and LLM selection
- ✅ **Spreadsheet MCP Server** with 1,038 rows/sec processing performance
- ✅ **Codebase MCP Server** with multi-language AST parsing and Git analysis
- ✅ **Enhanced graph brain** with foundational relationship schema
- ✅ **Comprehensive benchmark system** vs standard RAG with MCP performance metrics
- ✅ **Complete Docker containerization** with MCP server support
- ✅ **Horizontal scaling architecture** through independent MCP server deployment

**Strategic Achievement:**
Nancy has successfully evolved from a **monolithic super-RAG** to a **configurable orchestration platform**. The core value proposition is now the expertly designed chassis that makes specialized components work together seamlessly, while allowing users to configure databases, LLMs, and data processing capabilities through MCP servers.

**Recent Implementation (2025-08-20):**
- ✅ **MCP-First Architecture**: Nancy now defaults to MCP mode (`NANCY_MIGRATION_MODE=mcp`) demonstrating MCP orchestration in production
- ✅ **Core-Only Mode Support**: Fixed MCP host to allow Nancy to run with zero external MCP servers
- ✅ **Knowledge Packet Ingestion Enabled**: Full MCP architecture operational with proper schema validation
- ✅ **Adaptive MCP Memory Server**: Updated nancy-memory MCP server to handle both legacy and MCP modes automatically
- ✅ **Strategic Positioning**: Nancy positioned as "MCP orchestration platform" rather than "MCP-compatible system"

**Claude Code MCP Integration Status:**
- Nancy Memory MCP server configured via `claude mcp add` command
- Adaptive ingestion detects Nancy's mode and routes appropriately
- Requires Claude Code restart to load updated MCP server code
- Enables Claude Code to leverage Nancy's four-brain architecture for persistent memory

**Next Development Areas**:
- **Additional MCP servers** (PDF processing, real-time data sources, specialized domain servers)
- **Enhanced configuration management** with UI-based server registration
- **Performance optimization** for MCP communication protocols
- **Advanced analytics** and cross-server insight generation