# Nancy Spreadsheet Ingestion Architecture

## Overview

Nancy's Four-Brain architecture now supports comprehensive spreadsheet ingestion for Excel (.xlsx, .xls) and CSV files. This implementation extends Nancy's existing strengths in document analysis and relationship discovery to structured tabular data, enabling engineering teams to leverage their spreadsheet-based workflows while gaining the benefits of Nancy's intelligent knowledge base.

## Architecture Integration

### Four-Brain Processing Flow

When a spreadsheet is ingested, Nancy processes it through all four brains:

#### 1. Analytical Brain (DuckDB)
- **Raw Data Storage**: Spreadsheet data is stored directly as queryable tables
- **Metadata Tracking**: Sheet information, row/column counts, data types
- **Registry System**: Tracks all spreadsheet tables with lookup capabilities
- **SQL Queries**: Direct analytical queries on spreadsheet content

#### 2. Graph Brain (Neo4j)
- **Document Relationships**: Links spreadsheets to their parent documents
- **Sheet Structure**: Creates nodes for sheets and columns
- **Column Dependencies**: Detects calculated fields and cross-column relationships
- **Value Categorization**: Creates concept nodes for categorical data
- **Mathematical Relationships**: Identifies correlations between numeric columns

#### 3. Vector Brain (ChromaDB)
- **Semantic Summaries**: Generates searchable descriptions of sheet purpose and content
- **Column Descriptions**: Embeds statistical summaries and data characteristics
- **Sample Context**: Includes representative data for semantic search
- **Multi-Sheet Context**: Handles complex Excel files with multiple worksheets

#### 4. Linguistic Brain (Gemma)
- **Query Routing**: Determines when to use spreadsheet-specific capabilities
- **Natural Language**: Translates user questions into appropriate database queries
- **Cross-Brain Synthesis**: Combines structured data insights with relationship analysis

## Implementation Details

### File Processing Pipeline

```python
# Entry point: IngestionService.ingest_file()
if file_type in ['.xlsx', '.xls', '.csv']:
    return self._process_spreadsheet(filename, content, doc_id, file_type, author)
```

### Core Methods

#### `_process_spreadsheet()`
- Parses Excel/CSV files using pandas and openpyxl
- Handles multi-sheet Excel workbooks
- Coordinates processing across all four brains
- Returns comprehensive ingestion statistics

#### `_store_spreadsheet_data()`
- Creates DuckDB tables from pandas DataFrames
- Registers tables in spreadsheet registry
- Enables direct SQL queries on spreadsheet content

#### `_extract_spreadsheet_relationships()`
- Creates graph nodes for sheets, columns, and values
- Detects calculated fields and dependencies
- Links categorical values to their columns
- Identifies mathematical relationships between columns

#### `_generate_spreadsheet_summary()`
- Creates comprehensive text descriptions for vector search
- Includes column statistics, data types, and sample data
- Optimized for semantic search and natural language queries

## Key Features

### 1. Multi-Sheet Excel Support
- Processes all sheets in Excel workbooks
- Maintains sheet-to-document relationships
- Enables cross-sheet analysis and queries

### 2. Intelligent Relationship Detection
- **Calculated Fields**: Identifies columns that appear to be computed from others
- **Categorical Relationships**: Links columns to their unique values
- **Mathematical Dependencies**: Detects correlations and potential formulas
- **Cross-Column Analysis**: Finds patterns and relationships between data columns

### 3. Structured Query Capabilities
- **Direct SQL Access**: Query spreadsheet data using DuckDB SQL
- **Filtered Searches**: Search within specific sheets or documents
- **Content Search**: Full-text search across all spreadsheet text fields
- **Metadata Queries**: Find spreadsheets by characteristics (row count, column types, etc.)

### 4. Semantic Search Integration
- **Natural Language Queries**: Ask questions about spreadsheet content
- **Cross-Document Search**: Find related information across spreadsheets and text documents
- **Context-Aware Results**: Understand the purpose and structure of spreadsheets

## Usage Examples

### Basic Ingestion
```python
from core.ingestion import IngestionService

ingestion = IngestionService()
with open('requirements.xlsx', 'rb') as f:
    content = f.read()

result = ingestion.ingest_file('requirements.xlsx', content, author='Engineering Team')
print(f"Processed {result['sheets_processed']} sheets with {result['total_rows']} rows")
```

### Querying Spreadsheet Data
```python
# Direct SQL queries on spreadsheet data
analytical_brain = AnalyticalBrain()
results = analytical_brain.query_spreadsheet_data(
    doc_id='abc123',
    sql_filter="Category = 'Thermal' AND Status = 'Verified'"
)

# Search across all spreadsheets
search_results = analytical_brain.search_spreadsheet_content('power consumption')
```

### Graph Relationship Queries
```python
# Find all columns related to a specific sheet
graph_brain = GraphBrain()
columns = graph_brain.find_related_concepts('requirements.xlsx:Requirements', 'HAS_COLUMN')

# Discover calculated field dependencies
dependencies = graph_brain.find_relationships('CALCULATED_FROM')
```

## Engineering Team Benefits

### 1. **Requirements Management**
- Track requirement compliance across multiple spreadsheets
- Link requirements to test results and design documents
- Discover dependencies between system requirements

### 2. **Test Data Analysis**
- Query test results across multiple test campaigns
- Correlate test data with design parameters
- Track testing progress and compliance status

### 3. **Component Management**
- Analyze supply chain data and component relationships
- Find alternative components based on specifications
- Track inventory levels and procurement status

### 4. **Cross-Disciplinary Insights**
- Connect mechanical constraints with electrical requirements
- Link thermal analysis results to power consumption data
- Discover relationships between design decisions and test outcomes

## Technical Implementation

### Database Schema

#### Documents Table (Enhanced)
```sql
CREATE TABLE documents (
    id VARCHAR PRIMARY KEY,
    filename VARCHAR,
    size INTEGER,
    file_type VARCHAR,
    ingested_at TIMESTAMP,
    metadata JSON  -- New: stores spreadsheet-specific metadata
);
```

#### Spreadsheet Registry
```sql
CREATE TABLE spreadsheet_registry (
    doc_id VARCHAR,
    filename VARCHAR,
    sheet_name VARCHAR,
    table_name VARCHAR,
    row_count INTEGER,
    column_count INTEGER,
    created_at TIMESTAMP,
    FOREIGN KEY (doc_id) REFERENCES documents(id)
);
```

### Graph Schema Extensions

#### New Node Types
- `Spreadsheet`: Represents individual sheets
- `Column`: Represents spreadsheet columns
- `CategoryValue`: Represents categorical data values
- `CalculatedField`: Represents computed columns

#### New Relationship Types
- `CONTAINS_SHEET`: Document → Spreadsheet
- `HAS_COLUMN`: Spreadsheet → Column
- `CALCULATED_FROM`: Column → Column (dependencies)
- `CONTAINS_VALUE`: Column → CategoryValue
- `IS_CALCULATED_FIELD`: Column → CalculatedField

## Error Handling

### Robust File Processing
- **Corrupt Files**: Graceful handling of damaged spreadsheets
- **Protected Files**: Clear error messages for password-protected files
- **Large Files**: Memory-efficient processing of large datasets
- **Format Variations**: Support for different Excel formats and CSV encodings

### Fallback Mechanisms
- **Missing Dependencies**: Falls back to basic metadata storage if advanced processing fails
- **Parsing Errors**: Continues processing other sheets if one fails
- **Database Issues**: Provides detailed error messages and maintains system stability

## Performance Considerations

### Memory Management
- **Streaming Processing**: Large files processed in chunks
- **Selective Loading**: Only loads necessary sheets and columns
- **Efficient Storage**: Optimized DuckDB table structures

### Query Optimization
- **Indexed Access**: Registry enables fast spreadsheet lookup
- **Selective Queries**: Filters applied at database level
- **Cached Results**: Vector embeddings cached for repeated access

## Testing and Validation

### Comprehensive Test Suite
The `test_spreadsheet_ingestion.py` script validates:
- Excel and CSV file parsing
- Multi-sheet workbook handling
- Four-brain integration
- Error handling scenarios
- Query functionality

### Test Data Sets
- **Engineering Requirements**: Multi-sheet Excel with requirements tracking
- **Test Results**: CSV with validation data and measurements
- **Component Database**: Excel with inventory and supply chain data

## Future Enhancements

### Advanced Formula Processing
- **Excel Formula Parsing**: Extract and understand cell formulas
- **Dependency Graphs**: Create detailed calculation dependency trees
- **Formula Validation**: Verify formula correctness and relationships

### Enhanced Analytics
- **Statistical Analysis**: Automatic detection of trends and outliers
- **Cross-Sheet Relationships**: Discover relationships between different sheets
- **Time Series Analysis**: Handle temporal data in spreadsheets

### Integration Improvements
- **Real-time Updates**: Support for live spreadsheet data feeds
- **Version Control**: Track changes and versions of spreadsheet data
- **Collaborative Features**: Multi-user spreadsheet analysis and annotation

## Conclusion

Nancy's spreadsheet ingestion capability transforms static tabular data into an intelligent, queryable knowledge base. By leveraging the Four-Brain architecture, engineering teams can now seamlessly integrate their existing spreadsheet workflows with Nancy's powerful analysis and discovery capabilities, enabling better decision-making and cross-disciplinary collaboration.

The implementation provides immediate value for requirements management, test data analysis, and component tracking while laying the foundation for advanced analytics and automated insights discovery.