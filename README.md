# Project Nancy: Collaborative AI Librarian

## 1. Vision & Objective

**The Vision:** To eliminate the hidden tax of context-switching in the modern workplace. Knowledge workers spend countless hours searching for documents and rebuilding context. Our vision is a future where every team member, human and AI, has immediate, intelligent access to the full context of their work.

**The Objective:** To build "Nancy," a collaborative AI agent that creates and manages a persistent, project-specific knowledge base. Nancy acts as an autonomous teammate, building a rich "organizational memory" for a project, making its collective knowledge instantly accessible.

## 2. High-Level Architecture

Project Nancy uses a "Three-Brain" architecture to synthesize information from different kinds of data stores, providing answers with deep contextual awareness.

*   **🧠 Vector Brain (ChromaDB & FastEmbed):** Handles semantic search. It finds text snippets that are conceptually similar to a user's query, even if the keywords don't match exactly.
*   **🧠 Analytical Brain (DuckDB):** Handles structured metadata. It stores and retrieves concrete facts about data, such as filenames, file sizes, types, and creation dates.
*   **🧠 Relational Brain (Neo4j):** Handles the knowledge graph. It stores and queries the *relationships* between data, people, and concepts, such as who `AUTHORED` a specific document.

These three brains are orchestrated by a central **Query Orchestrator** that combines their strengths to produce a single, context-rich answer.

## 3. Project Structure

The project is a monorepo containing the core services and data.

```
/
├── 📂 nancy-services/    # Core Python services for Nancy
│   ├── 🐳 Dockerfile      # Defines the Ubuntu-based Python environment
│   ├── 📜 requirements.txt  # Python dependencies
│   │
│   ├── 📂 api/            # FastAPI application
│   │   ├── 📄 main.py       # API startup and routing
│   │   └── 📂 endpoints/  # API endpoint definitions (ingest, query)
│   │
│   └── 📂 core/           # Core business logic for the three "brains"
│       ├── 📄 ingestion.py
│       ├── 📄 knowledge_graph.py (Relational Brain)
│       ├── 📄 nlp.py (Vector Brain)
│       ├── 📄 query_orchestrator.py
│       └── 📄 search.py (Analytical Brain)
│
├── 📂 data/               # (Git-ignored) Local data stores for databases
│
└── 🐳 docker-compose.yml   # Defines and links all services for local development
```

## 4. Current Status (MVN Progress)

The project has achieved a stable, demonstrable proof-of-concept for the "Three-Brain" architecture.

**Completed:**
*   **Full Docker Environment:** All services (API, ChromaDB, Neo4j) are containerized and managed by `docker-compose`.
*   **Stable Embedding Service:** Replaced the unstable `sentence-transformers` library with `fastembed` and `ONNX`, resolving all low-level dependency crashes.
*   **File Ingestion Endpoint (`/api/ingest`):** Users can upload `.txt` files. The service automatically:
    1.  Stores file metadata in DuckDB.
    2.  Creates `Document` and `Person` nodes in Neo4j and links them with an `AUTHORED` relationship.
    3.  Chunks the text and stores its vector embeddings in ChromaDB.
*   **Hybrid Query Endpoint (`/api/query`):** Users can ask natural language questions. The service:
    1.  Finds relevant text chunks from ChromaDB.
    2.  Retrieves file metadata from DuckDB.
    3.  Finds the document's author from Neo4j.
    4.  Returns a single, synthesized response containing all three pieces of information.

## 5. How to Run the Project

**Prerequisites:**
*   Docker Desktop

**Steps:**
1.  **Start the Services:** From the project root, run the following command. This will build the API container and start all three services.
    ```bash
    docker-compose up -d --build
    ```
2.  **Test Ingestion:** Use the provided PowerShell script to upload a test file with an author.
    ```powershell
    .\test_upload_2.ps1
    ```
3.  **Test Querying:** Use the provided PowerShell script to ask a question about the ingested file.
    ```powershell
    .\test_query_2.ps1
    ```
    The response will be a JSON object containing the relevant text snippet, its metadata, and the author.

## 6. Development Next Steps

The current implementation provides a strong foundation for the Minimum Viable Nancy (MVN) demo. The next steps should focus on expanding the system's capabilities and demonstrating more complex, high-value queries.

*   **Expand File Type Support:** Add parsers for `.pdf` and `.docx` files in the `IngestionService` to broaden the types of knowledge Nancy can consume.
*   **Proactive Ingestion:** Implement webhook connectors for sources like GitHub to allow Nancy to autonomously observe project activity (e.g., ingest commit messages and link them to authors and code files).
*   **Advanced Graph Queries:** Enhance the `QueryOrchestrator` to answer more complex relational questions, such as:
    *   "What other documents has this author written?"
    *   "Show me all documents that are related to this one."
*   **LLM-Powered Synthesis:** Integrate a Large Language Model (LLM) to synthesize the final results into a natural, human-readable answer instead of a JSON object.

```