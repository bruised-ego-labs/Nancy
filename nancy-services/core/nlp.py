import chromadb
import os
from chromadb import Documents, EmbeddingFunction, Embeddings
from fastembed import TextEmbedding

class FastEmbedEmbeddingFunction(EmbeddingFunction):
    """
    A custom embedding function for ChromaDB that uses the fastembed library.
    """
    def __init__(self, model_name: str = 'BAAI/bge-small-en-v1.5'):
        # Initialize the TextEmbedding model
        print(f"Initializing fastembed model: {model_name}")
        self._model = TextEmbedding(model_name=model_name)
        print("Fastembed model initialized.")

    def __call__(self, input: Documents) -> Embeddings:
        # Embed the documents and convert the numpy arrays to lists
        embeddings = self._model.embed(input)
        return [e.tolist() for e in embeddings]

def get_chroma_client():
    """
    Returns a ChromaDB client connected to the specified host.
    """
    host = os.getenv("CHROMA_HOST", "chromadb")
    client = chromadb.HttpClient(host=host, port=8000)
    return client

class VectorBrain:
    """
    Handles interactions with the Vector Brain (ChromaDB).
    """
    def __init__(self):
        # Let's see what models are available
        supported_models = TextEmbedding.list_supported_models()
        print("Supported fastembed models:")
        for model in supported_models:
            print(model)

        self.client = get_chroma_client()
        

        self.collection = self.client.get_or_create_collection(
            name="nancy_documents",
            embedding_function=FastEmbedEmbeddingFunction(model_name='BAAI/bge-small-en-v1.5')
        )
        print("VectorBrain initialized with fastembed.")


    def _chunk_text(self, text: str, nlp, chunk_size: int = 384):
        """
        Splits a long text into smaller, semantically meaningful chunks using sentences.
        """
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        chunks = []
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += " " + sentence
            else:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

    def embed_and_store_text(self, doc_id: str, text: str, nlp):
        """
        Chunks text and stores it in ChromaDB.
        Embedding is handled automatically by the collection's embedding function.
        """
        chunks = self._chunk_text(text, nlp)
        
        # Create unique IDs for each chunk
        chunk_ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]

        self.collection.add(
            documents=chunks,
            metadatas=[{"source": doc_id} for _ in chunks],
            ids=chunk_ids
        )
        print(f"Added {len(chunks)} chunks for document {doc_id} to ChromaDB.")

    def query(self, query_texts: list[str], n_results: int = 5):
        """
        Queries the vector database for similar documents.
        The query text is automatically embedded by the collection's embedding function.
        """
        results = self.collection.query(
            query_texts=query_texts,
            n_results=n_results
        )
        return results
