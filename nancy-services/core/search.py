import duckdb
import os
from datetime import datetime

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
                ingested_at TIMESTAMP
            )
        """)

    def insert_document_metadata(self, doc_id: str, filename: str, size: int, file_type: str):
        """
        Inserts metadata for a new document.
        """
        ingested_at = datetime.utcnow()
        self.con.execute(
            "INSERT INTO documents (id, filename, size, file_type, ingested_at) VALUES (?, ?, ?, ?, ?)",
            (doc_id, filename, size, file_type, ingested_at)
        )
        print(f"Inserted metadata for {filename} into DuckDB.")

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