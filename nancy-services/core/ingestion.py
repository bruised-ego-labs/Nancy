from .search import AnalyticalBrain
from .knowledge_graph import RelationalBrain
from .nlp import VectorBrain
import os
import hashlib

class IngestionService:
    """
    Handles the ingestion of data from various sources.
    """
    def __init__(self):
        self.analytical_brain = AnalyticalBrain()
        self.relational_brain = RelationalBrain()
        self.vector_brain = VectorBrain()

    def _get_file_type(self, filename: str):
        return os.path.splitext(filename)[1].lower()

    def _generate_doc_id(self, filename: str, content: bytes) -> str:
        """Creates a unique ID for the document based on its name and content."""
        return hashlib.sha256(filename.encode() + content).hexdigest()

    def ingest_file(self, filename: str, content: bytes, author: str = "Unknown"):
        """
        Processes an uploaded file and stores it in the three brains.
        """
        file_type = self._get_file_type(filename)
        doc_id = self._generate_doc_id(filename, content)

        # 1. Analytical Brain: Store metadata
        self.analytical_brain.insert_document_metadata(
            doc_id=doc_id, # Pass the hash as a string
            filename=filename,
            size=len(content),
            file_type=file_type
        )

        # 2. Relational Brain: Create a document node and link the author
        self.relational_brain.add_document_node(filename=filename, file_type=file_type)
        self.relational_brain.add_author_relationship(filename=filename, author_name=author)

        # 3. Vector Brain: Embed and store content (if it's a text file)
        if file_type == ".txt":
            try:
                text = content.decode('utf-8')
                self.vector_brain.embed_and_store_text(doc_id=doc_id, text=text)
            except UnicodeDecodeError:
                return {"error": f"Could not decode file {filename} as UTF-8 text."}
        else:
            print(f"Skipping vector embedding for non-TXT file: {filename}")


        return {
            "filename": filename,
            "doc_id": doc_id,
            "status": "ingestion complete",
        }