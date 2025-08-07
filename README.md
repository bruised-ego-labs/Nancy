# Project Nancy: Collaborative AI Librarian

## 1. Vision & Objective

**The Vision:** To eliminate the hidden tax of context-switching in the modern workplace. Knowledge workers spend countless hours searching for documents and rebuilding context. Our vision is a future where every team member, human and AI, has immediate, intelligent access to the full context of their work.

**The Objective:** To build "Nancy," a collaborative AI agent that creates and manages a persistent, project-specific knowledge base. Nancy acts as an autonomous teammate, building a rich "organizational memory" for a project, making its collective knowledge instantly accessible.

## 2. High-Level Architecture

Project Nancy uses a **"Four-Brain" architecture** to synthesize information from different kinds of data stores, providing answers with deep contextual awareness and intelligent natural language processing.

*   **🧠 Vector Brain (ChromaDB & FastEmbed):** Handles semantic search. It finds text snippets that are conceptually similar to a user's query, even if the keywords don't match exactly.
*   **🧠 Analytical Brain (DuckDB):** Handles structured metadata. It stores and retrieves concrete facts about data, such as filenames, file sizes, types, and creation dates.
*   **🧠 Graph Brain (Neo4j):** Handles the project knowledge graph. It captures the complete project story including decisions, meetings, features, team collaborations, and project evolution - far beyond simple author attribution.
*   **🧠 Linguistic Brain (Ollama/Gemma):** Handles intelligent query analysis and response synthesis using a local Gemma LLM for zero-cost, private AI operations.

These four brains are orchestrated by an enhanced **Query Orchestrator** that intelligently combines their strengths to produce natural language responses with comprehensive fallback support (local LLM → cloud APIs → mock responses).

## 3. Project Structure

The project is a monorepo containing the core services and data.

```
/
├── 📂 nancy-services/    # Core Python services for Nancy
│   ├── ...
│   └── 📂 data/         # (Git-tracked) Placeholder for Docker volume mount
│       └── 📄 .gitkeep
│
├── 📂 data/               # (Git-ignored) Persistent data storage for all databases
│   └── 📂 project_phoenix/ # Example data for a specific "Nancy instance"
│
└── 🐳 docker-compose.yml   # Defines and links all services for local development
```

### The Role of the `data` Directories

The separation of the two `data` directories is intentional and important for maintaining a clean architecture.

*   `./data/`: This directory is the **persistent storage** for the application. It is mounted into the `api` container at `/app/data` and is the source of truth for all database files (DuckDB, ChromaDB, Neo4j). It is ignored by Git to prevent large data files from being committed to the repository.
*   `./nancy-services/data/`: This directory is a **placeholder**. Its purpose is to ensure that the `/app/data` path exists inside the container during development. Because the entire `./nancy-services` directory is mounted for live code reloading, this placeholder is necessary. It contains a `.gitkeep` file to ensure it is tracked by source control, preserving the project structure for all developers.


## 4. Current Status (Four-Brain Achievement)

The project has achieved a fully operational **Four-Brain Architecture** with local LLM integration, providing zero-cost AI operations with complete privacy.

**Completed:**
*   **Complete Docker Environment:** All services (API, ChromaDB, Neo4j, Ollama) are containerized and managed by `docker-compose`.
*   **Local LLM Integration:** Ollama service running Gemma 2B model for intelligent query analysis and response synthesis.
*   **Stable Embedding Service:** Using `fastembed` with ONNX for reliable, CPU-based text embeddings.
*   **Enhanced File Ingestion (`/api/ingest`):** Users can upload `.txt` files. The service automatically:
    1.  Stores file metadata in DuckDB (AnalyticalBrain).
    2.  Creates semantic embeddings and stores in ChromaDB (VectorBrain).
    3.  Extracts comprehensive project story using local Gemma LLM and stores in Neo4j (GraphBrain):
        - Decisions and decision makers
        - Meetings and attendees 
        - Features and owners
        - Project eras and phases
        - Cross-team collaborations
        - Technical dependencies
    4.  All processing happens locally with zero API costs.
*   **Intelligent Query Processing (`/api/query`):** Users can ask natural language questions. The enhanced system:
    1.  Analyzes query intent using local Gemma LLM (LinguisticBrain).
    2.  Orchestrates searches across Vector, Analytical, and Graph brains.
    3.  Answers complex project questions like:
        - "Why was this decision made?"
        - "Who are the experts on thermal design?"  
        - "What decisions led to this feature?"
        - "How do teams collaborate on this project?"
        - "What happened during Q4 2024 Architecture Phase?"
    4.  Provides comprehensive fallback: Local LLM → Cloud APIs → Mock responses.

**Key Benefits Achieved:**
*   **Zero Token Costs:** All LLM operations run locally on Gemma 2B
*   **Complete Privacy:** No data sent to external APIs
*   **No Rate Limits:** Unlimited local processing
*   **Consistent Performance:** No dependency on external services
*   **Production Ready:** Robust fallback systems ensure reliability

## 5. How to Run the Project

**Prerequisites:**
*   Docker Desktop (with at least 4GB RAM available for containers)

**Quick Start:**
1.  **Setup Nancy Four-Brain Architecture:** Run the automated setup script that starts all services and configures the local LLM.
    ```powershell
    .\setup_ollama.ps1
    ```
    This script will:
    - Start all Docker services (API, ChromaDB, Neo4j, Ollama)
    - Pull the Gemma 2B model (~1.6GB download)
    - Test the complete Four-Brain integration
    - Verify local LLM processing is working

**Manual Steps (Alternative):**
1.  **Start the Services:** From the project root, run the following command. This will build the API container and start all four services.
    ```bash
    docker-compose up -d --build
    ```
2.  **Wait for Ollama:** The Gemma model needs to be pulled on first run:
    ```bash
    docker-compose exec ollama ollama pull gemma:2b
    ```
3.  **Test the Complete System:** Use the enhanced demo script to test all four brains:
    ```powershell
    .\test_enhanced_three_brain_demo.ps1
    ```

**Service URLs:**
- Nancy API: http://localhost:8000
- ChromaDB: http://localhost:8001
- Neo4j Browser: http://localhost:7474 (neo4j/password)
- Ollama API: http://localhost:11434

## 6. Architecture Benefits & Use Cases

The Four-Brain Architecture provides significant advantages for multidisciplinary engineering teams:

**Key Benefits:**
*   **Zero Operating Costs:** Local LLM eliminates token charges while providing intelligent query analysis
*   **Complete Data Privacy:** All processing happens on-premises with no external API calls
*   **Unlimited Scalability:** No rate limits or API quotas restrict usage
*   **Robust Reliability:** Multiple fallback layers ensure system availability
*   **Rich Context Understanding:** Four specialized brains provide comprehensive information synthesis

**Ideal Use Cases:**
*   **Decision Archaeology:** Instantly recover why decisions were made, who influenced them, and what resulted
*   **Knowledge Expert Identification:** Find subject matter experts based on decisions, documents, and features
*   **Project Onboarding:** New team members can quickly understand project evolution and current context
*   **Impact Analysis:** Predict what changes will affect before making them
*   **Cross-team Collaboration:** Map collaboration networks and identify knowledge silos
*   **Regulatory Compliance:** Maintain comprehensive audit trails of decisions and their influences
*   **Knowledge Transfer:** Mitigate risks when team members leave by understanding their expertise networks

## 7. Development & Extension Opportunities

The Four-Brain Architecture provides a robust foundation for advanced AI-powered knowledge management:

**Immediate Enhancements:**
*   **Expand File Type Support:** Add parsers for `.pdf`, `.docx`, and `.xlsx` files
*   **Advanced Relationship Extraction:** Enhance LLM prompts for more sophisticated concept relationships
*   **Multi-language Support:** Leverage Gemma's multilingual capabilities for international teams
*   **Query Templates:** Pre-built queries for common engineering workflows

**Future Integrations:**
*   **GitHub Integration:** Automatic ingestion of commit messages, pull requests, and issues
*   **CAD File Analysis:** Extract metadata and relationships from design files
*   **Slack/Teams Connectors:** Capture and index team communications
*   **Advanced Analytics:** Generate insights about team collaboration patterns and knowledge gaps

```