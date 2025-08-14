import duckdb
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, Optional

def get_duckdb_connection():
    """
    Returns a DuckDB connection.
    The database file is stored in the mounted 'data' volume.
    """
    db_path = os.path.join("data", "project_nancy.duckdb")
    con = duckdb.connect(database=db_path, read_only=False)
    return con

class AnalyticalBrain:
    """
    Handles interactions with the Analytical Brain (DuckDB).
    """
    def __init__(self):
        self.con = get_duckdb_connection()
        self.setup_tables()

    def setup_tables(self):
        """
        Creates the necessary tables if they don't exist.
        The ID is now a VARCHAR to store the full SHA256 hash.
        """
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id VARCHAR PRIMARY KEY,
                filename VARCHAR,
                size INTEGER,
                file_type VARCHAR,
                ingested_at TIMESTAMP,
                metadata JSON
            )
        """)
        
        # Create table for spreadsheet registry
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS spreadsheet_registry (
                doc_id VARCHAR,
                filename VARCHAR,
                sheet_name VARCHAR,
                table_name VARCHAR,
                row_count INTEGER,
                column_count INTEGER,
                created_at TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES documents(id)
            )
        """)

    def insert_document_metadata(self, doc_id: str, filename: str, size: int, file_type: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Inserts metadata for a new document. Handles duplicates gracefully.
        """
        import json
        ingested_at = datetime.utcnow()
        metadata_json = None if metadata is None else json.dumps(metadata)
        
        try:
            # First check if document already exists
            existing = self.con.execute(
                "SELECT id FROM documents WHERE id = ?", 
                (doc_id,)
            ).fetchone()
            
            if existing:
                print(f"Document {filename} (ID: {doc_id[:8]}...) already exists in DuckDB. Skipping insertion.")
                return
            
            # Insert new document
            self.con.execute(
                "INSERT INTO documents (id, filename, size, file_type, ingested_at, metadata) VALUES (?, ?, ?, ?, ?, ?)",
                (doc_id, filename, size, file_type, ingested_at, metadata_json)
            )
            print(f"Inserted metadata for {filename} into DuckDB.")
            
        except Exception as e:
            print(f"Error inserting document metadata for {filename}: {e}")
            # Re-raise the exception if it's not a duplicate key constraint
            if "Duplicate key" not in str(e):
                raise

    def query(self, sql_query: str):
        """
        Queries the analytical database.
        """
        return self.con.execute(sql_query).fetchall()

    def get_documents_by_ids(self, doc_ids: list[str]) -> list[dict]:
        """
        Retrieves document metadata for a list of document IDs.
        """
        if not doc_ids:
            return []
        
        # Create a placeholder string for the IN clause
        placeholders = ', '.join(['?'] * len(doc_ids))
        query = f"SELECT * FROM documents WHERE id IN ({placeholders})"
        
        results = self.con.execute(query, doc_ids).fetchall()
        
        # Convert list of tuples to list of dicts
        columns = [desc[0] for desc in self.con.description]
        return [dict(zip(columns, row)) for row in results]
    
    def filter_documents(self, filters: dict) -> list[dict]:
        """
        Advanced document filtering based on metadata constraints.
        
        Supported filters:
        - author: string (requires join with GraphBrain)
        - file_type: string or list
        - start_date, end_date: datetime strings
        - min_size, max_size: integers (bytes)
        - filename_contains: string
        """
        query_parts = ["SELECT * FROM documents WHERE 1=1"]
        params = []
        
        # File type filtering
        if 'file_type' in filters:
            file_types = filters['file_type']
            if isinstance(file_types, list):
                placeholders = ', '.join(['?'] * len(file_types))
                query_parts.append(f"AND file_type IN ({placeholders})")
                params.extend(file_types)
            else:
                query_parts.append("AND file_type = ?")
                params.append(file_types)
        
        # Date range filtering
        if 'start_date' in filters:
            query_parts.append("AND ingested_at >= ?")
            params.append(filters['start_date'])
        
        if 'end_date' in filters:
            query_parts.append("AND ingested_at <= ?")
            params.append(filters['end_date'])
        
        # Size filtering
        if 'min_size' in filters:
            query_parts.append("AND size >= ?")
            params.append(filters['min_size'])
        
        if 'max_size' in filters:
            query_parts.append("AND size <= ?")
            params.append(filters['max_size'])
        
        # Filename filtering
        if 'filename_contains' in filters:
            query_parts.append("AND filename LIKE ?")
            params.append(f"%{filters['filename_contains']}%")
        
        # Add ordering
        query_parts.append("ORDER BY ingested_at DESC")
        
        full_query = " ".join(query_parts)
        results = self.con.execute(full_query, params).fetchall()
        
        # Convert to dict format
        columns = [desc[0] for desc in self.con.description]
        return [dict(zip(columns, row)) for row in results]
    
    def get_document_statistics(self) -> dict:
        """
        Get analytical statistics about the document collection.
        """
        stats = {}
        
        # Total documents
        total_docs = self.con.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        stats['total_documents'] = total_docs
        
        # File type distribution
        file_types = self.con.execute("""
            SELECT file_type, COUNT(*) as count 
            FROM documents 
            GROUP BY file_type 
            ORDER BY count DESC
        """).fetchall()
        stats['file_type_distribution'] = [{"type": ft[0], "count": ft[1]} for ft in file_types]
        
        # Size statistics
        size_stats = self.con.execute("""
            SELECT 
                AVG(size) as avg_size,
                MIN(size) as min_size,
                MAX(size) as max_size,
                SUM(size) as total_size
            FROM documents
        """).fetchone()
        
        if size_stats[0] is not None:
            stats['size_statistics'] = {
                'average_size': int(size_stats[0]),
                'min_size': size_stats[1],
                'max_size': size_stats[2],
                'total_size': size_stats[3]
            }
        
        # Documents by date (last 30 days)
        recent_docs = self.con.execute("""
            SELECT DATE(ingested_at) as date, COUNT(*) as count
            FROM documents 
            WHERE ingested_at >= DATE('now', '-30 days')
            GROUP BY DATE(ingested_at)
            ORDER BY date DESC
        """).fetchall()
        stats['recent_activity'] = [{"date": rd[0], "count": rd[1]} for rd in recent_docs]
        
        return stats
    
    def search_documents_by_content_metadata(self, search_term: str, limit: int = 50) -> list[dict]:
        """
        Search documents by filename or metadata (not content - that's VectorBrain's job).
        """
        query = """
            SELECT * FROM documents 
            WHERE filename LIKE ? 
            ORDER BY ingested_at DESC 
            LIMIT ?
        """
        
        search_pattern = f"%{search_term}%"
        results = self.con.execute(query, (search_pattern, limit)).fetchall()
        
        columns = [desc[0] for desc in self.con.description]
        return [dict(zip(columns, row)) for row in results]
    
    def update_document_metadata(self, doc_id: str, additional_metadata: Dict[str, Any]):
        """
        Update document metadata with additional information (e.g., spreadsheet details).
        """
        try:
            # Get existing metadata
            existing = self.con.execute(
                "SELECT metadata FROM documents WHERE id = ?", 
                (doc_id,)
            ).fetchone()
            
            if not existing:
                print(f"Warning: Document {doc_id} not found for metadata update. Skipping.")
                return
                
            if existing[0]:
                # Parse existing metadata and merge with new
                import json
                try:
                    current_metadata = json.loads(existing[0])
                except Exception as json_error:
                    print(f"Warning: Could not parse existing metadata as JSON: {json_error}")
                    print(f"Existing metadata content: {repr(existing[0][:100])}...")
                    current_metadata = {}
            else:
                current_metadata = {}
            
            # Merge new metadata
            current_metadata.update(additional_metadata)
            
            # Update the document with proper JSON encoding
            import json
            self.con.execute(
                "UPDATE documents SET metadata = ? WHERE id = ?",
                (json.dumps(current_metadata), doc_id)
            )
            
            print(f"Updated metadata for document {doc_id}")
            
        except Exception as e:
            print(f"Error updating document metadata: {e}")
    
    def store_spreadsheet_data(self, table_name: str, df: pd.DataFrame, metadata: Dict[str, Any]):
        """
        Store spreadsheet data directly in DuckDB for structured querying.
        """
        try:
            # Clean table name for DuckDB compliance
            clean_table_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in table_name)
            
            # Register the DataFrame as a DuckDB table
            # This allows SQL queries directly on the pandas DataFrame
            self.con.register(clean_table_name, df)
            
            # Create a persistent table from the DataFrame
            create_table_sql = f"CREATE TABLE IF NOT EXISTS {clean_table_name} AS SELECT * FROM {clean_table_name}"
            self.con.execute(create_table_sql)
            
            # Register in spreadsheet registry
            self.con.execute("""
                INSERT INTO spreadsheet_registry 
                (doc_id, filename, sheet_name, table_name, row_count, column_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata['doc_id'],
                metadata['filename'], 
                metadata['sheet_name'],
                clean_table_name,
                len(df),
                len(df.columns),
                datetime.utcnow()
            ))
            
            print(f"Stored spreadsheet data in table {clean_table_name}")
            
        except Exception as e:
            print(f"Error storing spreadsheet data: {e}")
            raise e
    
    def query_spreadsheet_data(self, doc_id: str, sheet_name: Optional[str] = None, sql_filter: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Query spreadsheet data with optional filtering.
        """
        try:
            # Find the table(s) for this document
            registry_query = "SELECT * FROM spreadsheet_registry WHERE doc_id = ?"
            params = [doc_id]
            
            if sheet_name:
                registry_query += " AND sheet_name = ?"
                params.append(sheet_name)
            
            tables = self.con.execute(registry_query, params).fetchall()
            
            if not tables:
                return {"error": f"No spreadsheet data found for document {doc_id}"}
            
            results = {}
            
            for table_info in tables:
                table_name = table_info[3]  # table_name column
                sheet = table_info[2]       # sheet_name column
                
                # Build query
                query = f"SELECT * FROM {table_name}"
                
                if sql_filter:
                    query += f" WHERE {sql_filter}"
                
                query += f" LIMIT {limit}"
                
                # Execute query
                data = self.con.execute(query).fetchall()
                columns = [desc[0] for desc in self.con.description]
                
                results[sheet] = {
                    "columns": columns,
                    "data": [dict(zip(columns, row)) for row in data],
                    "row_count": table_info[4],  # total row count
                    "column_count": table_info[5]  # total column count
                }
            
            return results
            
        except Exception as e:
            print(f"Error querying spreadsheet data: {e}")
            return {"error": str(e)}
    
    def get_spreadsheet_summary(self, doc_id: str) -> Dict[str, Any]:
        """
        Get summary information about spreadsheets for a document.
        """
        try:
            summary = self.con.execute("""
                SELECT 
                    sheet_name,
                    table_name,
                    row_count,
                    column_count,
                    created_at
                FROM spreadsheet_registry 
                WHERE doc_id = ?
                ORDER BY created_at
            """, (doc_id,)).fetchall()
            
            if not summary:
                return {"error": f"No spreadsheet data found for document {doc_id}"}
            
            sheets = []
            total_rows = 0
            total_cols = 0
            
            for sheet_info in summary:
                sheet_data = {
                    "sheet_name": sheet_info[0],
                    "table_name": sheet_info[1], 
                    "row_count": sheet_info[2],
                    "column_count": sheet_info[3],
                    "created_at": sheet_info[4]
                }
                sheets.append(sheet_data)
                total_rows += sheet_info[2]
                total_cols = max(total_cols, sheet_info[3])
            
            return {
                "doc_id": doc_id,
                "total_sheets": len(sheets),
                "total_rows": total_rows,
                "max_columns": total_cols,
                "sheets": sheets
            }
            
        except Exception as e:
            print(f"Error getting spreadsheet summary: {e}")
            return {"error": str(e)}
    
    def search_spreadsheet_content(self, search_term: str, doc_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Search across all spreadsheet data for content matching the search term.
        """
        try:
            # Get all spreadsheet tables
            registry_query = "SELECT doc_id, filename, sheet_name, table_name FROM spreadsheet_registry"
            params = []
            
            if doc_id:
                registry_query += " WHERE doc_id = ?"
                params.append(doc_id)
            
            tables = self.con.execute(registry_query, params).fetchall()
            
            results = []
            
            for table_info in tables:
                table_doc_id, filename, sheet_name, table_name = table_info
                
                try:
                    # Get table columns to search text columns
                    columns_info = self.con.execute(f"PRAGMA table_info({table_name})").fetchall()
                    text_columns = [col[1] for col in columns_info if 'VARCHAR' in col[2] or 'TEXT' in col[2]]
                    
                    if text_columns:
                        # Build search query for text columns
                        search_conditions = [f"{col} LIKE ?" for col in text_columns]
                        search_query = f"""
                            SELECT * FROM {table_name} 
                            WHERE {' OR '.join(search_conditions)}
                            LIMIT 50
                        """
                        
                        search_params = [f"%{search_term}%" for _ in text_columns]
                        matches = self.con.execute(search_query, search_params).fetchall()
                        
                        if matches:
                            columns = [desc[0] for desc in self.con.description]
                            results.append({
                                "doc_id": table_doc_id,
                                "filename": filename,
                                "sheet_name": sheet_name,
                                "matches": [dict(zip(columns, row)) for row in matches]
                            })
                
                except Exception as e:
                    print(f"Error searching table {table_name}: {e}")
                    continue
            
            return {
                "search_term": search_term,
                "total_matches": len(results),
                "results": results
            }
            
        except Exception as e:
            print(f"Error searching spreadsheet content: {e}")
            return {"error": str(e)}