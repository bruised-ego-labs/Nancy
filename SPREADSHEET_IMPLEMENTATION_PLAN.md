# Nancy Spreadsheet Integration Implementation Plan

## Current Status Assessment (August 13, 2025)

### ✅ What's Working
- CSV file upload via `/api/ingest` endpoint
- Metadata storage in Analytical Brain (DuckDB)
- Document and author nodes in Graph Brain (Neo4j)
- Four-brain architecture infrastructure

### ❌ What Needs Implementation
- Structured data parsing (CSV/Excel content processing)
- Vector embeddings for spreadsheet summaries
- Column relationship mapping in Graph Brain
- Enhanced DuckDB schema for tabular data
- Neo4j APOC procedures configuration

## Implementation Requirements

### 1. Dependencies Addition
```bash
# Add to requirements.txt
pandas>=2.0.0
openpyxl>=3.1.0
xlsxwriter>=3.0.0
```

### 2. Enhanced Ingestion Service

**File: `nancy-services/core/ingestion.py`**

Add spreadsheet processing logic:
```python
def _process_spreadsheet(self, filename: str, content: bytes, doc_id: str):
    """Process CSV/Excel files for structured data extraction"""
    import pandas as pd
    import io
    
    # Determine file type and read appropriately
    if filename.endswith('.csv'):
        df = pd.read_csv(io.BytesIO(content))
    elif filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(content), sheet_name=None)  # Read all sheets
    
    # Store structured data in DuckDB
    self.analytical_brain.store_spreadsheet_data(doc_id, filename, df)
    
    # Create column relationships in Neo4j
    self.graph_brain.add_spreadsheet_schema(filename, df.columns.tolist())
    
    # Generate text summary for vector embedding
    summary = self._generate_spreadsheet_summary(df, filename)
    self.vector_brain.embed_and_store_text(doc_id, summary, self.nlp)
```

### 3. Enhanced Analytical Brain

**File: `nancy-services/core/search.py`**

Add methods for structured data storage:
```python
def store_spreadsheet_data(self, doc_id: str, filename: str, dataframe):
    """Store structured spreadsheet data in DuckDB"""
    table_name = self._sanitize_table_name(filename)
    
    # Create table from dataframe
    self.conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM dataframe")
    
    # Store metadata linking doc_id to table
    self.conn.execute("""
        INSERT INTO spreadsheet_metadata (doc_id, filename, table_name, columns, row_count)
        VALUES (?, ?, ?, ?, ?)
    """, (doc_id, filename, table_name, str(list(dataframe.columns)), len(dataframe)))

def query_spreadsheet_data(self, query: str):
    """Execute SQL queries on spreadsheet data"""
    return self.conn.execute(query).fetchall()
```

### 4. Enhanced Graph Brain

**File: `nancy-services/core/knowledge_graph.py`**

Add spreadsheet relationship modeling:
```python
def add_spreadsheet_schema(self, filename: str, columns: list):
    """Create column nodes and relationships for spreadsheet"""
    # Create table node
    self.driver.execute_query(
        "MERGE (t:Table {name: $filename}) RETURN t",
        filename=filename
    )
    
    # Create column nodes and relationships
    for i, col in enumerate(columns):
        self.driver.execute_query("""
            MERGE (c:Column {name: $col_name, table: $filename})
            MERGE (t:Table {name: $filename})
            MERGE (c)-[:BELONGS_TO]->(t)
            SET c.position = $position
        """, col_name=col, filename=filename, position=i)
```

### 5. Vector Brain Enhancement

Generate meaningful summaries for spreadsheet content:
```python
def _generate_spreadsheet_summary(self, df, filename: str) -> str:
    """Generate a searchable summary of spreadsheet content"""
    summary_parts = [
        f"Spreadsheet: {filename}",
        f"Contains {len(df)} rows and {len(df.columns)} columns",
        f"Columns: {', '.join(df.columns)}",
    ]
    
    # Add sample data insights
    for col in df.columns:
        if df[col].dtype in ['object', 'string']:
            unique_values = df[col].unique()[:5]  # First 5 unique values
            summary_parts.append(f"{col} includes: {', '.join(map(str, unique_values))}")
        elif df[col].dtype in ['int64', 'float64']:
            summary_parts.append(f"{col} ranges from {df[col].min()} to {df[col].max()}")
    
    return " | ".join(summary_parts)
```

## Testing Plan

### Phase 1: Infrastructure Setup
1. Add dependencies to requirements.txt
2. Rebuild Docker containers
3. Configure Neo4j APOC procedures

### Phase 2: Core Implementation
1. Implement spreadsheet processing in ingestion.py
2. Add structured storage to AnalyticalBrain
3. Enhance GraphBrain with column relationships
4. Test with sample CSV files

### Phase 3: Query Enhancement
1. Implement SQL query capabilities for tabular data
2. Add cross-brain queries (e.g., "Find all thermal data for components owned by Sarah Chen")
3. Test natural language to SQL translation

### Phase 4: Validation
1. Test component requirements CSV
2. Test test results CSV with join queries
3. Test project overview and team directory integration
4. Benchmark against baseline RAG

## Expected Engineering Team Value

### Foundational Capabilities Unlocked
1. **Structured Data Queries**: "Show me all components with thermal constraints above 70°C"
2. **Cross-Reference Analysis**: "Which test results correspond to components owned by Sarah Chen?"
3. **Project Intelligence**: "What projects are over budget and who are the leads?"
4. **Relationship Discovery**: "Find dependencies between thermal constraints and power requirements"

### Multi-Brain Integration
- **Analytical**: SQL queries on structured data
- **Graph**: Column relationships and data lineage
- **Vector**: Natural language search across content
- **Linguistic**: Intelligent query routing and synthesis

## Implementation Priority

**HIGH PRIORITY (Foundation)**:
1. Add pandas/openpyxl dependencies
2. Modify ingestion.py to process CSV files as text
3. Fix Neo4j APOC configuration

**MEDIUM PRIORITY (Enhancement)**:
1. Structured data storage in DuckDB
2. Column relationship modeling in Neo4j
3. Enhanced query capabilities

**LOW PRIORITY (Advanced)**:
1. Multi-sheet Excel support
2. Automated column type detection
3. Data visualization integration

## Success Metrics

- CSV files processed with full four-brain integration
- Natural language queries return structured data results
- Author attribution works across spreadsheet content
- Cross-brain queries (structure + relationships + content) functional
- Engineering teams can ask questions like "Who owns the failing thermal tests?"

## Next Steps

1. **Immediate**: Add CSV to text_based_extensions in ingestion.py
2. **Short-term**: Add pandas dependency and rebuild containers
3. **Medium-term**: Implement full structured data processing
4. **Long-term**: Advanced spreadsheet intelligence features