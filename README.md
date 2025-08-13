# Project Nancy: Collaborative AI Librarian

## 1. Vision & Objective

**The Vision:** To eliminate the hidden tax of context-switching in the modern workplace. Knowledge workers spend countless hours searching for documents and rebuilding context. Our vision is a future where every team member, human and AI, has immediate, intelligent access to the full context of their work.

**The Objective:** To build "Nancy," a collaborative AI agent that creates and manages a persistent, project-specific knowledge base. Nancy acts as an autonomous teammate, building a rich "organizational memory" for a project, making its collective knowledge instantly accessible.

## 2. Current Architecture (LangChain Router + Enhanced Relationships)

Project Nancy uses a **"Four-Brain" architecture** enhanced with **multi-step query processing** and **foundational relationship schema** to provide intelligent, context-aware responses.

### 🧠 The Four Brains

*   **Vector Brain (ChromaDB & FastEmbed):** Handles semantic search using ONNX-based embeddings. Finds conceptually similar content even when keywords don't match exactly.
*   **Analytical Brain (DuckDB):** Handles structured metadata queries. Stores and retrieves concrete facts about files, sizes, types, and ingestion timestamps.
*   **Graph Brain (Neo4j):** Handles the comprehensive project knowledge graph with **foundational relationship schema**:
    - **People & Organization:** Expertise, roles, team membership, decision-making
    - **Technical Subsystems:** Component relationships, interfaces, constraints, dependencies  
    - **Project Management:** Decision provenance, validation chains, risk mitigation
*   **Linguistic Brain (Gemma 3n-e4b-it):** Handles intelligent query analysis, routing decisions, and response synthesis using Google AI API.

### 🎯 Multi-Step Query Processing

The system now intelligently detects complex queries requiring both semantic content and relationship analysis:

1. **Query Analysis:** Determines if multi-step processing is needed
2. **Content Discovery:** Vector brain finds relevant documents 
3. **Relationship Exploration:** Graph brain explores contextual relationships
4. **Intelligent Synthesis:** Combines findings into comprehensive responses

**Example Multi-Step Query Flow:**
```
Query: "What are the thermal constraints and who are the experts on this topic?"

Step 1: Vector search finds thermal analysis documents
Step 2: Graph brain explores thermal expertise relationships
Step 3: Synthesis combines technical content with expert identification
Result: "The thermal constraints include... The thermal experts are Sarah Chen (lead thermal engineer) and Mike Rodriguez (thermal validation)..."
```

## 3. Project Structure

```
/
├── 📂 nancy-services/          # Core Python services
│   ├── 📂 api/                # FastAPI endpoints
│   │   ├── main.py           # Application entry point
│   │   └── endpoints/        # API route handlers
│   ├── 📂 core/              # Core intelligence modules
│   │   ├── langchain_orchestrator.py    # LangChain router + multi-step processing
│   │   ├── knowledge_graph.py           # Enhanced graph brain with foundational schema
│   │   ├── nlp.py                      # Vector brain (FastEmbed + ChromaDB)
│   │   ├── search.py                   # Analytical brain (DuckDB)
│   │   ├── llm_client.py               # Gemma 3n-e4b-it integration
│   │   └── ingestion.py               # Multi-brain document processing
│   └── 📂 data/              # Container mount point
│
├── 📂 baseline-rag/           # Standard RAG comparison system
│   ├── main.py               # LangChain + ChromaDB baseline
│   └── Dockerfile           # Baseline container
│
├── 📂 benchmark_data/         # Comprehensive test datasets
│   └── benchmark_test_data/  # 14 queries across 7 engineering disciplines
│
├── 📂 data/                  # (Git-ignored) Persistent storage
│   └── 📂 project_phoenix/   # Example Nancy instance data
│
├── 📂 archive/               # Archived old files and scripts
│
└── 🐳 docker-compose.yml     # Complete service orchestration
```

## 4. Current Status: Production-Ready LangChain Router Architecture

### ✅ Completed Systems

**Core Architecture:**
*   **LangChain Router Integration:** Deterministic routing with multi-step processing for complex queries
*   **Enhanced Graph Brain:** Foundational relationship schema supporting expertise, technical systems, and project management queries
*   **Gemma 3n-e4b-it Integration:** Lightweight, fast LLM via Google AI API for all routing and synthesis operations
*   **Multi-Step Query Processing:** Intelligent detection and handling of complex queries requiring both content and relationship analysis
*   **Comprehensive Baseline System:** Standard LangChain + ChromaDB RAG for performance comparison

**Key Features:**
*   **Beyond "Who" Questions:** Graph brain now handles expertise ("Who are the thermal experts?"), technical relationships ("What systems interface with electrical?"), decision analysis ("Why was this decided?"), and collaboration networks
*   **Intelligent Routing:** Enhanced router descriptions guide queries to appropriate brains based on intent
*   **Synthesis Integration:** All responses properly synthesized through Gemma 3n-e4b-it for natural language output
*   **Deterministic Performance:** More predictable than ReAct agents while maintaining intelligence

### 🔧 Technical Implementation

**LangChain Router Architecture:**
```python
# Multi-step processing detection
def _needs_multi_step_processing(self, query: str) -> bool:
    patterns = [
        ("what" in query_lower and "who" in query_lower),
        ("how" in query_lower and "relate" in query_lower),
        (len([word for word in ["electrical", "mechanical", "thermal"] if word in query_lower]) > 1)
    ]
    return any(patterns)

# Enhanced relationship exploration  
def _explore_contextual_relationships(self, query: str, context: str) -> str:
    # Intelligently routes to expertise, technical, decision, or collaboration analysis
    # Based on query patterns and context
```

**Foundational Relationship Schema:**
```cypher
// People & Organization
(Person)-[:HAS_EXPERTISE]->(Domain)
(Person)-[:HAS_ROLE]->(Role)
(Person)-[:MEMBER_OF]->(Team)

// Technical Subsystems  
(Component)-[:PART_OF]->(System)
(System)-[:INTERFACES_WITH]->(System)
(Component)-[:CONSTRAINED_BY]->(Constraint)

// Project Management
(Decision)-[:VALIDATED_BY]->(Process)
(Document)-[:PRODUCED]->(Deliverable)
(Risk)-[:MITIGATED_BY]->(Action)
```

### 📊 Performance Characteristics

**Benchmark Results (vs Standard RAG):**
*   **Author Attribution:** 100% vs 0% (standard RAG has no author capability)
*   **Cross-Disciplinary Queries:** 50-80% F1 score improvement
*   **Relationship Discovery:** 60-90% precision improvement
*   **Response Time:** ~2-3 seconds for complex multi-step queries

**Current Active Scripts:**
*   `comprehensive_benchmark_with_metrics.py` - Current benchmark system
*   `test_benchmark_docker.ps1` - Docker-based testing
*   `reset_development_data.ps1` - Environment reset
*   `test_query_2.ps1` - Active query testing

## 5. How to Run the Project

**Prerequisites:**
*   Docker Desktop (4GB+ RAM available)
*   `GEMINI_API_KEY` environment variable set

**Quick Start:**
1.  **Start All Services:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Test the System:**
    ```powershell
    # Test document ingestion
    .\test_upload_2.ps1
    
    # Test intelligent querying
    .\test_query_2.ps1
    
    # Run comprehensive benchmark
    .\test_benchmark_docker.ps1
    ```

**Service URLs:**
- Nancy API: http://localhost:8000
- ChromaDB: http://localhost:8001  
- Neo4j Browser: http://localhost:7474 (neo4j/password)
- Nancy API Documentation: http://localhost:8000/docs

## 6. Enhanced Use Cases & Benefits

### 🎯 Advanced Query Types Now Supported

**Expertise Discovery:**
```
Query: "Who are the thermal analysis experts?"
Result: "Sarah Chen (lead thermal engineer, 5 decisions, 3 documents) and Mike Rodriguez (thermal validation specialist, 2 documents)..."
```

**Technical Relationship Analysis:**
```
Query: "How do electrical and mechanical systems interface?" 
Result: "The electrical design constrains mechanical housing requirements through EMC shielding needs. The power distribution interfaces with the cooling system via thermal management requirements..."
```

**Decision Provenance:**
```
Query: "Why did we choose this thermal solution?"
Result: "The thermal solution was decided by Sarah Chen based on constraints from the March design review meeting. This decision influenced the mechanical integration approach and validated the power analysis requirements..."
```

**Cross-Team Collaboration:**
```
Query: "What thermal decisions and who collaborated on electrical integration?"
Result: "Thermal constraints from Sarah Chen's analysis influenced Mike Rodriguez's electrical design. Their collaboration included EMC compliance decisions and power distribution validation..."
```

### 💡 Business Benefits

**For Engineering Teams:**
*   **Faster Onboarding:** New engineers quickly understand project context and expertise networks
*   **Better Decision Making:** Full context of why previous decisions were made
*   **Risk Mitigation:** Identify knowledge silos and single points of failure
*   **Compliance:** Complete audit trails for regulatory requirements

**For Project Management:**
*   **Impact Analysis:** Understand change consequences before implementation  
*   **Resource Planning:** Identify expertise gaps and collaboration patterns
*   **Knowledge Transfer:** Preserve institutional knowledge when team members leave

## 7. Next Steps & Extension Opportunities

### 🚀 Immediate Enhancements
*   **Enhanced Document Ingestion:** Support for PDF, DOCX, CAD file metadata
*   **Additional Brain Types:** Specialized brains for specific domains
*   **Relationship Auto-Extraction:** Automated relationship discovery during ingestion
*   **Query Templates:** Pre-built queries for common engineering workflows

### 🔮 Future Integrations  
*   **GitHub Integration:** Automatic ingestion of commits, PRs, and issues
*   **Slack/Teams Connectors:** Capture team communications and decisions
*   **CAD File Analysis:** Extract technical relationships from design files
*   **Advanced Analytics:** Team collaboration insights and knowledge gap analysis

## 8. Development Commands

```bash
# Environment management
docker-compose up -d --build    # Start all services
docker-compose down -v          # Stop and remove all data
.\reset_development_data.ps1    # Reset development environment

# Testing and benchmarking  
.\test_upload_2.ps1             # Test file ingestion
.\test_query_2.ps1              # Test querying capabilities
.\test_benchmark_docker.ps1     # Run comprehensive benchmarks

# Advanced testing
.\test_enhanced_three_brain_demo.ps1  # Demo all brain capabilities
.\test_four_brain_demo.ps1            # Test four-brain integration
```

## 9. Architecture Documentation

For detailed technical documentation, see:
- `CLAUDE.md` - Development guidelines and architectural details
- `API_DOCUMENTATION.md` - API endpoint specifications  
- `gemini.log` - Technical analysis and team recommendations
- `comprehensive_benchmark_*.json` - Latest benchmark results

---

*Project Nancy represents a next-generation approach to organizational knowledge management, combining the power of multiple specialized AI systems with intelligent query processing to create a truly collaborative AI teammate.*