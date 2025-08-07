from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain

class QueryOrchestrator:
    """
    The core intelligence that decides how to combine 
    the three databases for optimal answers.
    """
    def __init__(self):
        """
        Initializes the Query Orchestrator and the three brains.
        """
        self.analytical_brain = AnalyticalBrain()
        self.graph_brain = GraphBrain()
        self.vector_brain = VectorBrain()
        print("Query Orchestrator initialized.")

    def query_authored_documents(self, author_name: str):
        """
        Finds all documents authored by a specific person.
        """
        print(f"Orchestrator received author query for: {author_name}")
        
        # 1. Relational Brain: Get all document filenames for the author
        filenames = self.graph_brain.get_documents_by_author(author_name)
        
        # In a real system, you might want to get metadata from DuckDB as well
        
        return {
            "status": "success",
            "author": author_name,
            "documents": filenames
        }

    def query(self, query_text: str, n_results: int = 5):
        """
        Processes a query by finding semantically similar content in the VectorBrain
        and augmenting it with metadata from the AnalyticalBrain and GraphBrain.
        """
        print(f"Orchestrator received query: {query_text}")

        # 1. Vector Brain: Find similar document chunks
        vector_results = self.vector_brain.query(query_texts=[query_text], n_results=n_results)

        # 2. Extract doc_ids from the vector search results
        doc_ids = []
        if vector_results and vector_results.get('metadatas'):
            for metadata_list in vector_results['metadatas']:
                for metadata in metadata_list:
                    if metadata and 'source' in metadata:
                        doc_ids.append(metadata['source'])
        
        unique_doc_ids = list(set(doc_ids))

        # 3. Analytical Brain: Get the full metadata for these documents
        doc_metadata = self.analytical_brain.get_documents_by_ids(unique_doc_ids)
        
        # Create a lookup map for faster access
        doc_metadata_map = {doc['id']: doc for doc in doc_metadata}

        # 4. Synthesize the results
        synthesized_results = []
        if vector_results and vector_results.get('ids'):
            for i, id_list in enumerate(vector_results['ids']):
                for j, chunk_id in enumerate(id_list):
                    doc_id = vector_results['metadatas'][i][j]['source']
                    doc_meta = doc_metadata_map.get(doc_id)
                    
                    # 5. Relational Brain: Get author for each document
                    author = self.graph_brain.get_author_of_document(doc_meta['filename']) if doc_meta else "Unknown"
                    
                    synthesized_results.append({
                        "chunk_id": chunk_id,
                        "document_metadata": doc_meta,
                        "author": author,
                        "distance": vector_results['distances'][i][j],
                        "text": vector_results['documents'][i][j]
                    })

        return {
            "status": "success",
            "results": synthesized_results
        }
