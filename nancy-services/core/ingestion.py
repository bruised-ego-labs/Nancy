from .search import AnalyticalBrain
from .knowledge_graph import RelationalBrain
from .nlp import VectorBrain
import os
import hashlib
import spacy
import re

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
        Enhanced entity extraction with relationship discovery using LLM if available.
        """
        doc = self.nlp(text)
        
        # Extract person entities
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                # Create person nodes and link to document
                self.relational_brain.add_concept_node(ent.text, "Person")
                self.relational_brain.add_relationship(
                    source_node_label="Person",
                    source_node_name=ent.text,
                    relationship_type="MENTIONED_IN",
                    target_node_label="Document",
                    target_node_name=current_filename,
                    context=f"Mentioned in {current_filename}"
                )
        
        # Extract document references
        document_patterns = [
            r'\b(\w+\.\w{2,4})\b',  # file.ext
            r'\b(\w+\s+\w+\s+document)\b',  # "power analysis document"
            r'\b(\w+\s+report)\b',  # "thermal report"
            r'\b(\w+\s+analysis)\b',  # "stress analysis"
            r'\b(\w+\s+specification)\b',  # "design specification"
            r'\b(\w+\s+requirements)\b'  # "system requirements"
        ]
        
        for pattern in document_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match.lower() != current_filename.lower():
                    self.relational_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=current_filename,
                        relationship_type="REFERENCES",
                        target_node_label="Document",
                        target_node_name=match,
                        context=f"Referenced in {current_filename}"
                    )
        
        # Extract technical concepts and constraints
        concept_patterns = {
            "power": ["power consumption", "power management", "power supply", "battery life"],
            "thermal": ["thermal constraints", "temperature", "heat dissipation", "cooling"],
            "mechanical": ["mechanical design", "stress analysis", "material selection"],
            "electrical": ["electrical design", "circuit", "schematic", "EMC", "compliance"],
            "software": ["firmware", "software", "algorithm", "protocol", "interface"]
        }
        
        text_lower = text.lower()
        for concept_type, keywords in concept_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Create concept node and relationship
                    self.relational_brain.add_concept_node(keyword, "TechnicalConcept")
                    self.relational_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=current_filename,
                        relationship_type="DISCUSSES",
                        target_node_label="TechnicalConcept",
                        target_node_name=keyword,
                        context=f"Technical concept discussed in {current_filename}"
                    )
        
        # Extract decision and influence relationships
        decision_patterns = [
            r'(decided|determined|chose|selected)\s+([^.]{1,50})',
            r'(impacts?|affects?|influences?)\s+([^.]{1,50})',
            r'(requires?|needs?|depends on)\s+([^.]{1,50})',
            r'(constrains?|limits?)\s+([^.]{1,50})'
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for verb, target in matches:
                relationship_map = {
                    "decided": "DECISION_MADE",
                    "determined": "DECISION_MADE",
                    "chose": "DECISION_MADE",
                    "selected": "DECISION_MADE",
                    "impacts": "AFFECTS",
                    "affects": "AFFECTS",
                    "influences": "INFLUENCES",
                    "requires": "REQUIRES",
                    "needs": "REQUIRES",
                    "depends": "DEPENDS_ON",
                    "constrains": "CONSTRAINS",
                    "limits": "CONSTRAINS"
                }
                
                rel_type = relationship_map.get(verb.lower(), "RELATES_TO")
                
                # Create a concept for the target if it's meaningful
                if len(target.strip()) > 5 and len(target.strip()) < 100:
                    concept_name = target.strip()[:50]  # Limit length
                    self.relational_brain.add_concept_node(concept_name, "DecisionTarget")
                    self.relational_brain.add_relationship(
                        source_node_label="Document",
                        source_node_name=current_filename,
                        relationship_type=rel_type,
                        target_node_label="DecisionTarget", 
                        target_node_name=concept_name,
                        context=f"{verb} relationship from {current_filename}"
                    )
        
        # Try to use LLM for enhanced relationship extraction if available
        try:
            from .llm_client import LLMClient
            llm_client = LLMClient()
            
            # Extract a meaningful chunk of text for LLM analysis
            text_chunk = text[:2000] if len(text) > 2000 else text
            relationships = llm_client.extract_document_relationships(text_chunk, current_filename)
            
            for rel in relationships:
                self.relational_brain.add_relationship(
                    source_node_label=rel.get("source_type", "Document"),
                    source_node_name=rel["source"],
                    relationship_type=rel["relationship"],
                    target_node_label=rel.get("target_type", "Concept"),
                    target_node_name=rel["target"],
                    context=rel.get("context", f"LLM-extracted from {current_filename}")
                )
                
        except Exception as e:
            print(f"LLM relationship extraction failed: {e}")
            # Continue without LLM enhancement


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
