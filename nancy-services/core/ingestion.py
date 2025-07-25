from .search import AnalyticalBrain
from .knowledge_graph import RelationalBrain
from .nlp import VectorBrain
import os
import hashlib
import spacy

class IngestionService:
    """
    Handles the ingestion of data from various sources.
    """
    def __init__(self):
        self.analytical_brain = AnalyticalBrain()
        self.relational_brain = RelationalBrain()
        self.vector_brain = VectorBrain()
        # Load the spacy model
        self.nlp = spacy.load("en_core_web_sm")

    def _get_file_type(self, filename: str):
        return os.path.splitext(filename)[1].lower()

    def _generate_doc_id(self, filename: str, content: bytes) -> str:
        """Creates a unique ID for the document based on its name and content."""
        return hashlib.sha256(filename.encode() + content).hexdigest()

    def _extract_entities(self, text: str, current_filename: str):
        """
        Uses spacy to extract named entities and create relationships.
        """
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Link the person to the current document
                self.relational_brain.add_relationship(
                    source_node_label="Person",
                    source_node_name=ent.text,
                    relationship_type="MENTIONED_IN",
                    target_node_label="Document",
                    target_node_name=current_filename
                )
        
        # A simple way to find references to other documents
        # In a real system, this would be more robust
        for token in doc:
            if token.text.endswith(".txt"):
                self.relational_brain.add_relationship(
                    source_node_label="Document",
                    source_node_name=current_filename,
                    relationship_type="REFERENCES",
                    target_node_label="Document",
                    target_node_name=token.text
                )


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

        # 3. Vector Brain & Entity Extraction
        # Define a list of text-based file extensions to process
        text_based_extensions = ['.txt', '.md', '.log', '.py', '.js', '.html', '.css', '.json']
        
        if file_type in text_based_extensions:
            try:
                text = content.decode('utf-8')
                # Embed and store the text
                self.vector_brain.embed_and_store_text(doc_id=doc_id, text=text, nlp=self.nlp)
                # Extract entities and create relationships
                self._extract_entities(text, filename)
            except UnicodeDecodeError:
                return {"error": f"Could not decode file {filename} as UTF-8 text."}
        else:
            print(f"Skipping vector embedding and entity extraction for non-text file: {filename}")


        return {
            "filename": filename,
            "doc_id": doc_id,
            "status": "ingestion complete",
        }
