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