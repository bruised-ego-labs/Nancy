# Nancy Spreadsheet MCP Server

Standalone MCP server providing comprehensive spreadsheet processing capabilities for Nancy's Four-Brain architecture. This server extracts spreadsheet data and generates standardized Nancy Knowledge Packets for seamless integration.

## Features

- **Multi-format Support**: Excel (.xlsx, .xls) and CSV files
- **Multi-sheet Processing**: Comprehensive analysis of all sheets in Excel workbooks
- **Engineering Intelligence**: Domain-specific analysis for thermal, mechanical, electrical, and quality data
- **Four-Brain Data Distribution**: Generates vector, analytical, and graph data for Nancy's architecture
- **Knowledge Packet Generation**: Standardized output format for Nancy Core integration

## Installation

```bash
cd mcp-servers/spreadsheet
pip install -r requirements.txt
```

## Usage

The server is designed to run as part of Nancy's MCP ecosystem:

```bash
# Start the server
python server.py

# Or via Nancy Core configuration
# Add to nancy-config.yaml:
# mcp_servers:
#   enabled_servers:
#     - name: "nancy-spreadsheet-server"
#       executable: "python"
#       args: ["mcp-servers/spreadsheet/server.py"]
```

## Capabilities

### Processing Features
- **Multi-sheet Excel Analysis**: Processes all sheets in Excel workbooks
- **Column Intelligence**: Detects numeric, categorical, and identifier columns
- **Engineering Domain Detection**: Recognizes thermal, mechanical, electrical data patterns
- **Relationship Extraction**: Creates graph relationships between columns and values
- **Semantic Summary Generation**: Produces searchable text summaries for vector search

### Knowledge Packet Output
Each processed spreadsheet generates a Nancy Knowledge Packet containing:

- **Vector Data**: Semantic summaries for each sheet
- **Analytical Data**: Structured table data with column types
- **Graph Data**: Entities and relationships for columns and values
- **Processing Hints**: Brain routing and classification guidance
- **Quality Metrics**: Confidence scores and processing status

## Configuration

See `config.yaml` for detailed configuration options including:
- File size and complexity limits
- Quality thresholds
- Performance settings
- Nancy integration parameters

## MCP Protocol Compliance

Implements standard MCP methods:
- `nancy/ingest`: Process spreadsheet files
- `nancy/health_check`: Server health and capabilities
- `nancy/capabilities`: Supported features and file types

## Error Handling

- Graceful fallback for corrupted files
- Encoding detection for CSV files
- Detailed error reporting with context
- Retry mechanisms for transient failures

## Performance

Optimized for:
- Large Excel files (up to 100MB)
- Multiple sheets (up to 50 per file)
- High row counts (up to 1M rows per sheet)
- Concurrent request processing

## Integration with Nancy Core

This MCP server is designed for Phase 2 of Nancy's migration to MCP architecture:
1. Extracts from monolithic nancy-services/core/ingestion.py
2. Provides backwards compatibility
3. Enables independent scaling and deployment
4. Maintains full feature parity with original implementation