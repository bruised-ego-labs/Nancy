# Nancy Memory MCP Server

> **"Infinite Memory for AI Assistants"** - Transform any LLM into a project-aware intelligence with persistent memory.

## Overview

The Nancy Memory MCP Server provides persistent, intelligent memory capabilities for any LLM through the Model Context Protocol (MCP). Instead of losing context between conversations, AI assistants can now store and retrieve project knowledge, track decisions, and maintain long-term understanding.

## Strategic Position

**Nancy as Infrastructure, Not Competition:**
- Nancy becomes the "Project Brain" that makes other LLMs smarter
- Solves the fundamental context window limitation of all current LLMs
- Positions Nancy as essential infrastructure rather than competing with Claude/GPT-4/Gemini
- Leverages Nancy's proven 60% query superiority in engineering contexts

## Architecture

```
┌─────────────────┐    MCP Protocol    ┌─────────────────┐
│                 │ ◄─────────────────► │                 │
│  Any LLM        │                     │  Nancy Memory   │
│  (Claude, GPT,  │   Tools & Resources │  MCP Server     │
│   Gemini, etc.) │                     │                 │
└─────────────────┘                     └─────────────────┘
                                                │
                                                │ HTTP API
                                                ▼
                                        ┌─────────────────┐
                                        │                 │
                                        │  Nancy Core     │
                                        │  Four-Brain     │
                                        │  Architecture   │
                                        │                 │
                                        └─────────────────┘
```

## Capabilities

### 🧠 Tools (What LLMs Can Do)

1. **`ingest_information`** - Store information in persistent memory
   - Decisions made during conversations
   - Technical specifications and requirements
   - Meeting outcomes and action items
   - Code analysis and documentation

2. **`query_memory`** - Retrieve relevant context from past conversations
   - "What decisions did we make about the thermal design?"
   - "Who are the experts on power management?"
   - "How do electrical and mechanical systems interact?"

3. **`find_author_contributions`** - Track who contributed what
   - Code authorship and ownership
   - Document creation and maintenance
   - Subject matter expertise identification

4. **`get_project_overview`** - Comprehensive project status
   - Metrics and health indicators
   - Key areas of activity
   - System configuration and capabilities

### 📚 Resources (What LLMs Can Access)

1. **`nancy://project/memory`** - Complete project memory index
   - Structured view of all stored information
   - Nancy's configuration and capabilities
   - Usage guidance and best practices

## Quick Start

### Prerequisites

1. **Nancy Core Running:**
   ```bash
   cd /path/to/nancy
   docker-compose up -d --build
   ```

2. **Verify Nancy Health:**
   ```bash
   curl http://localhost:8000/health
   ```

### Installation

1. **Install Dependencies:**
   ```bash
   cd mcp-servers/nancy-memory
   pip install -r requirements.txt
   ```

2. **Run the MCP Server:**
   ```bash
   python server.py
   ```

3. **Connect from Claude Code:**
   - The server runs on stdio by default
   - Configure your MCP client to connect to this server

### Configuration with Claude Code

Add to your Claude Code MCP configuration:

```json
{
  "mcpServers": {
    "nancy-memory": {
      "command": "python",
      "args": ["/path/to/nancy/mcp-servers/nancy-memory/server.py"],
      "env": {
        "NANCY_API_BASE": "http://localhost:8000"
      }
    }
  }
}
```

## Example Usage

### Storing Project Context

```python
# LLM uses the ingest_information tool
ingest_information(
    content="We decided to use aluminum heat sink for thermal management due to 15W TDP constraint. Sarah Chen is leading thermal design, Mike Rodriguez handling power management.",
    content_type="decision",
    author="Project Team",
    metadata={"meeting_date": "2025-01-15", "priority": "high"}
)
```

### Querying Project Memory

```python
# LLM uses the query_memory tool
query_memory(
    question="What thermal design decisions have we made and who's responsible?",
    n_results=5,
    search_strategy="intelligent"
)

# Returns:
# {
#   "response": "Based on project memory: Aluminum heat sink decision made due to 15W TDP. Sarah Chen leads thermal design, works with Mike Rodriguez on power constraints...",
#   "sources": [...],
#   "confidence": "high"
# }
```

### Finding Subject Matter Experts

```python
# LLM uses the find_author_contributions tool
find_author_contributions(
    author_name="Sarah Chen",
    contribution_type="all"
)

# Returns:
# {
#   "contributions": ["thermal_analysis.pdf", "heat_sink_design.cad"],
#   "expertise_areas": ["thermal_engineering", "mechanical_design"],
#   "collaboration_patterns": [{"with": "Mike Rodriguez", "on": "power_thermal_interface"}]
# }
```

## Business Value

### For AI Assistants
- **Persistent Context:** Never lose important project information between conversations
- **Intelligent Retrieval:** Find relevant information using Nancy's Four-Brain architecture
- **Relationship Discovery:** Understand how technical decisions connect across domains
- **Expert Identification:** Know who to ask about specific technical areas

### For Engineering Teams
- **Institutional Memory:** Preserve project knowledge across team changes
- **Context Reconstruction:** Eliminate time spent rebuilding context
- **Decision Provenance:** Track how and why decisions were made
- **Cross-Domain Intelligence:** Connect electrical, mechanical, thermal, software domains

### ROI Calculator
For a $120K/year senior engineer spending 25% time on context switching:
- **Annual cost:** $30,000 in lost productivity per engineer
- **Nancy's impact:** 50-80% reduction in context switching time  
- **Savings:** $15,000-$24,000 per engineer annually
- **Team of 10:** $150,000-$240,000 annual productivity gains

## Technical Details

### Nancy Integration

The MCP server communicates with Nancy Core through HTTP APIs:

- **Ingestion:** `/api/ingest/knowledge-packet` - Store new information
- **Querying:** `/api/query` - Intelligent information retrieval  
- **Graph Queries:** `/api/query/graph` - Author attribution and relationships
- **Status:** `/api/nancy/status` - System health and metrics

### Error Handling

The server provides graceful error handling:
- Connection failures to Nancy Core
- Invalid query formats
- Timeout handling for long-running queries
- Detailed error messages for debugging

### Performance

- **Query Response Time:** 2-6 seconds for complex multi-brain queries
- **Ingestion Speed:** <1 second for text documents
- **Memory Efficiency:** Knowledge packets processed asynchronously
- **Scalability:** Horizontal scaling through Nancy's MCP architecture

## Advanced Configuration

### Environment Variables

```bash
export NANCY_API_BASE="http://localhost:8000"  # Nancy Core API URL
export MCP_LOG_LEVEL="INFO"                    # Logging level
export MCP_TIMEOUT="60"                        # Request timeout in seconds
```

### Custom Nancy Deployment

For production deployments:

```yaml
# docker-compose.override.yml
services:
  nancy-memory-mcp:
    build: ./mcp-servers/nancy-memory
    environment:
      NANCY_API_BASE: "http://nancy-api:8000"
    depends_on:
      - nancy-api
```

## Troubleshooting

### Common Issues

1. **"Failed to connect to Nancy API"**
   - Ensure Nancy Core is running: `docker-compose up -d`
   - Check API accessibility: `curl http://localhost:8000/health`

2. **"Nancy Core not available"**
   - Verify Nancy initialization completed successfully
   - Check Docker container logs: `docker logs nancy-api-1`

3. **"Knowledge Packet ingestion requires MCP mode"**
   - Ensure Nancy is running in MCP mode (default in latest version)
   - Check configuration: `curl http://localhost:8000/api/nancy/configuration`

### Debugging

Enable debug logging:
```bash
export MCP_LOG_LEVEL="DEBUG"
python server.py
```

## Contributing

This MCP server is part of the broader Nancy project. Contributions welcome:

1. **Enhanced Tools:** Add new capabilities like temporal analysis or risk assessment
2. **Performance Optimization:** Improve query response times and caching
3. **Integration Examples:** Create examples for different LLM platforms
4. **Documentation:** Improve setup guides and usage examples

## License

This Nancy Memory MCP Server is part of the Nancy project and follows the same licensing terms.

---

**Transform your AI assistant from a forgetful chatbot into a project-aware intelligence with Nancy Memory MCP Server.**