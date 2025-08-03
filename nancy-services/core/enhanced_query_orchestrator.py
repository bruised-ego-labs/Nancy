"""
Enhanced Query Orchestrator for Nancy Project
Demonstrates intelligent use of all three databases based on query type and content.
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .search import AnalyticalBrain
from .knowledge_graph import RelationalBrain
from .nlp import VectorBrain

class QueryAnalyzer:
    """
    Analyzes incoming queries to determine the optimal database strategy.
    """
    
    @staticmethod
    def analyze_query_intent(query: str) -> Dict[str, Any]:
        """
        Analyzes the query to determine intent and optimal database strategy.
        """
        query_lower = query.lower()
        
        intent = {
            'type': 'hybrid',  # Default to hybrid approach
            'primary_brain': 'vector',  # Default to vector-first
            'needs_vector': True,
            'needs_analytical': True,
            'needs_relational': True,
            'focus': 'content',  # content, people, metadata, relationships
            'temporal': None,  # recent, old, specific_date
            'entities': []
        }
        
        # Detect query patterns
        patterns = {
            'author_focused': [
                r'\b(who\s+wrote|author|created\s+by|written\s+by)\b',
                r'\b(documents?\s+by|files?\s+by)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:wrote|created|authored)\b'
            ],
            'relationship_focused': [
                r'\b(related\s+to|connected\s+to|similar\s+documents?)\b',
                r'\b(what\s+other|show\s+me\s+all|find\s+all)\b',
                r'\b(dependencies|references|links)\b'
            ],
            'temporal_focused': [
                r'\b(recent|latest|newest|last\s+\w+)\b',
                r'\b(old|oldest|first|earliest)\b',
                r'\b(yesterday|today|this\s+week|last\s+month)\b',
                r'\b(\d{4}|\d{1,2}/\d{1,2})\b'  # dates
            ],
            'analytical_focused': [
                r'\b(how\s+many|count|number\s+of|statistics)\b',
                r'\b(largest|smallest|biggest|most|least)\b',
                r'\b(compare|comparison|vs\.|versus)\b',
                r'\b(trend|pattern|frequency)\b'
            ],
            'content_focused': [
                r'\b(about|contains|mentions|discusses)\b',
                r'\b(find\s+text|search\s+for|content\s+about)\b'
            ]
        }
        
        # Check for specific patterns
        for category, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, query_lower):
                    if category == 'author_focused':
                        intent.update({
                            'type': 'relationship_primary',
                            'primary_brain': 'relational',
                            'focus': 'people'
                        })
                    elif category == 'relationship_focused':
                        intent.update({
                            'type': 'graph_exploration',
                            'primary_brain': 'relational',
                            'focus': 'relationships'
                        })
                    elif category == 'temporal_focused':
                        intent.update({
                            'type': 'analytical_primary',
                            'primary_brain': 'analytical',
                            'focus': 'metadata',
                            'temporal': 'recent' if any(word in query_lower for word in ['recent', 'latest', 'newest']) else 'temporal'
                        })
                    elif category == 'analytical_focused':
                        intent.update({
                            'type': 'analytical_primary',
                            'primary_brain': 'analytical',
                            'focus': 'metadata'
                        })
                    break
        
        # Extract potential person names (simple heuristic)
        name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
        potential_names = re.findall(name_pattern, query)
        intent['entities'] = [name for name in potential_names if len(name.split()) <= 3]
        
        return intent

class EnhancedQueryOrchestrator:
    """
    Enhanced orchestrator that intelligently combines the three brains based on query analysis.
    """
    
    def __init__(self):
        """
        Initialize the three brains and query analyzer.
        """
        self.analytical_brain = AnalyticalBrain()
        self.relational_brain = RelationalBrain()
        self.vector_brain = VectorBrain()
        self.query_analyzer = QueryAnalyzer()
        print("Enhanced Query Orchestrator initialized with intelligent routing.")

    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Main query method that routes to appropriate strategy based on query analysis.
        """
        print(f"Enhanced Orchestrator analyzing query: {query_text}")
        
        # Analyze the query to determine strategy
        intent = self.query_analyzer.analyze_query_intent(query_text)
        print(f"Query intent: {intent}")
        
        # Route to appropriate strategy
        strategy_map = {
            'relationship_primary': self._strategy_relationship_first,
            'analytical_primary': self._strategy_analytical_first,
            'graph_exploration': self._strategy_graph_exploration,
            'hybrid': self._strategy_hybrid
        }
        
        strategy_func = strategy_map.get(intent['type'], self._strategy_hybrid)
        return strategy_func(query_text, intent, n_results)

    def _strategy_relationship_first(self, query_text: str, intent: Dict, n_results: int) -> Dict[str, Any]:
        """
        Strategy that starts with relationship/people queries (Neo4j first).
        Optimal for: "Who wrote X?", "Documents by John", "Show me Scott's work"
        """
        print("Using RELATIONSHIP-FIRST strategy")
        
        results = {
            "strategy_used": "relationship_first",
            "intent": intent,
            "results": []
        }
        
        # 1. Check if we have potential author names in the query
        if intent['entities']:
            for entity in intent['entities']:
                print(f"Searching for documents by potential author: {entity}")
                documents = self.relational_brain.get_documents_by_author(entity)
                
                if documents:
                    # Found author, get metadata for their documents
                    doc_metadata_list = []
                    for filename in documents:
                        # Get doc metadata from analytical brain
                        metadata_query = f"SELECT * FROM documents WHERE filename = '{filename}'"
                        metadata_results = self.analytical_brain.query(metadata_query)
                        if metadata_results:
                            doc_metadata_list.append(dict(zip(
                                ['id', 'filename', 'size', 'file_type', 'ingested_at'], 
                                metadata_results[0]
                            )))
                    
                    # Now do vector search within these documents
                    if doc_metadata_list:
                        doc_ids = [doc['id'] for doc in doc_metadata_list]
                        vector_results = self.vector_brain.query([query_text], n_results=n_results)
                        
                        # Filter vector results to only include docs by this author
                        filtered_results = self._filter_vector_results_by_doc_ids(
                            vector_results, doc_ids, doc_metadata_list, entity
                        )
                        
                        results["results"].extend(filtered_results)
        
        # If no author-specific results, fall back to hybrid approach
        if not results["results"]:
            print("No author-specific results found, falling back to hybrid strategy")
            return self._strategy_hybrid(query_text, intent, n_results)
        
        return results

    def _strategy_analytical_first(self, query_text: str, intent: Dict, n_results: int) -> Dict[str, Any]:
        """
        Strategy that starts with analytical queries (DuckDB first).
        Optimal for: "Recent documents", "Largest files", "How many files by John?"
        """
        print("Using ANALYTICAL-FIRST strategy")
        
        results = {
            "strategy_used": "analytical_first",
            "intent": intent,
            "results": []
        }
        
        # Build analytical query based on intent
        base_query = "SELECT * FROM documents"
        conditions = []
        
        if intent.get('temporal') == 'recent':
            # Find recent documents (last 7 days)
            recent_date = datetime.utcnow() - timedelta(days=7)
            conditions.append(f"ingested_at > '{recent_date.isoformat()}'")
        
        # Add entity filtering if author names detected
        if intent['entities']:
            # Get documents by these authors from Neo4j first
            all_author_docs = []
            for entity in intent['entities']:
                author_docs = self.relational_brain.get_documents_by_author(entity)
                all_author_docs.extend(author_docs)
            
            if all_author_docs:
                filename_list = "', '".join(all_author_docs)
                conditions.append(f"filename IN ('{filename_list}')")
        
        # Construct final query
        if conditions:
            analytical_query = f"{base_query} WHERE {' AND '.join(conditions)} ORDER BY ingested_at DESC"
        else:
            analytical_query = f"{base_query} ORDER BY ingested_at DESC LIMIT {n_results * 2}"
        
        print(f"Analytical query: {analytical_query}")
        metadata_results = self.analytical_brain.query(analytical_query)
        
        if metadata_results:
            # Convert to dict format
            doc_metadata_list = [dict(zip(
                ['id', 'filename', 'size', 'file_type', 'ingested_at'], 
                row
            )) for row in metadata_results]
            
            # Now do targeted vector search within these documents
            doc_ids = [doc['id'] for doc in doc_metadata_list]
            vector_results = self.vector_brain.query([query_text], n_results=n_results)
            
            # Create author lookup
            author_lookup = {}
            for doc in doc_metadata_list:
                author = self.relational_brain.get_author_of_document(doc['filename'])
                author_lookup[doc['id']] = author or "Unknown"
            
            # Synthesize results
            results["results"] = self._filter_vector_results_by_doc_ids(
                vector_results, doc_ids, doc_metadata_list, None, author_lookup
            )
        
        return results

    def _strategy_graph_exploration(self, query_text: str, intent: Dict, n_results: int) -> Dict[str, Any]:
        """
        Strategy for exploring relationships and connections.
        Optimal for: "Related documents", "Who else worked on this?", "Connected topics"
        """
        print("Using GRAPH-EXPLORATION strategy")
        
        results = {
            "strategy_used": "graph_exploration",
            "intent": intent,
            "results": []
        }
        
        # First, do a vector search to find relevant documents
        initial_vector_results = self.vector_brain.query([query_text], n_results=3)
        
        if initial_vector_results and initial_vector_results.get('ids'):
            # Get the top document(s) and explore their relationships
            top_doc_ids = [
                initial_vector_results['metadatas'][0][i]['source'] 
                for i in range(min(2, len(initial_vector_results['ids'][0])))
            ]
            
            # Get metadata for these documents
            doc_metadata = self.analytical_brain.get_documents_by_ids(top_doc_ids)
            
            related_authors = []
            related_documents = []
            
            for doc in doc_metadata:
                # Find the author of this document
                author = self.relational_brain.get_author_of_document(doc['filename'])
                if author and author not in related_authors:
                    related_authors.append(author)
                    
                    # Find other documents by this author
                    other_docs = self.relational_brain.get_documents_by_author(author)
                    related_documents.extend([d for d in other_docs if d != doc['filename']])
            
            # Get metadata for related documents
            if related_documents:
                related_doc_metadata = []
                for filename in set(related_documents):  # Remove duplicates
                    metadata_query = f"SELECT * FROM documents WHERE filename = '{filename}'"
                    metadata_results = self.analytical_brain.query(metadata_query)
                    if metadata_results:
                        related_doc_metadata.append(dict(zip(
                            ['id', 'filename', 'size', 'file_type', 'ingested_at'], 
                            metadata_results[0]
                        )))
                
                # Now do vector search within the expanded document set
                all_doc_ids = top_doc_ids + [doc['id'] for doc in related_doc_metadata]
                vector_results = self.vector_brain.query([query_text], n_results=n_results)
                
                # Create comprehensive author lookup
                author_lookup = {}
                for author in related_authors:
                    author_docs = self.relational_brain.get_documents_by_author(author)
                    for doc_filename in author_docs:
                        # Find the doc_id for this filename
                        for doc in doc_metadata + related_doc_metadata:
                            if doc['filename'] == doc_filename:
                                author_lookup[doc['id']] = author
                
                results["results"] = self._filter_vector_results_by_doc_ids(
                    vector_results, all_doc_ids, doc_metadata + related_doc_metadata, 
                    None, author_lookup
                )
                
                results["related_authors"] = related_authors
                results["explored_connections"] = len(related_documents)
        
        return results

    def _strategy_hybrid(self, query_text: str, intent: Dict, n_results: int) -> Dict[str, Any]:
        """
        Default hybrid strategy - improved version of current approach.
        """
        print("Using HYBRID strategy")
        
        # Enhanced version of current approach
        vector_results = self.vector_brain.query(query_texts=[query_text], n_results=n_results)
        
        doc_ids = []
        if vector_results and vector_results.get('metadatas'):
            for metadata_list in vector_results['metadatas']:
                for metadata in metadata_list:
                    if metadata and 'source' in metadata:
                        doc_ids.append(metadata['source'])
        
        unique_doc_ids = list(set(doc_ids))
        doc_metadata = self.analytical_brain.get_documents_by_ids(unique_doc_ids)
        doc_metadata_map = {doc['id']: doc for doc in doc_metadata}
        
        synthesized_results = []
        if vector_results and vector_results.get('ids'):
            for i, id_list in enumerate(vector_results['ids']):
                for j, chunk_id in enumerate(id_list):
                    doc_id = vector_results['metadatas'][i][j]['source']
                    doc_meta = doc_metadata_map.get(doc_id)
                    
                    author = self.relational_brain.get_author_of_document(doc_meta['filename']) if doc_meta else "Unknown"
                    
                    synthesized_results.append({
                        "chunk_id": chunk_id,
                        "document_metadata": doc_meta,
                        "author": author,
                        "distance": vector_results['distances'][i][j],
                        "text": vector_results['documents'][i][j]
                    })

        return {
            "strategy_used": "hybrid",
            "intent": intent,
            "results": synthesized_results
        }

    def _filter_vector_results_by_doc_ids(self, vector_results: Dict, target_doc_ids: List[str], 
                                        doc_metadata_list: List[Dict], author_filter: Optional[str] = None,
                                        author_lookup: Optional[Dict] = None) -> List[Dict]:
        """
        Filter and format vector results to only include specific document IDs.
        """
        filtered_results = []
        doc_metadata_map = {doc['id']: doc for doc in doc_metadata_list}
        
        if vector_results and vector_results.get('ids'):
            for i, id_list in enumerate(vector_results['ids']):
                for j, chunk_id in enumerate(id_list):
                    doc_id = vector_results['metadatas'][i][j]['source']
                    
                    # Only include results from target documents
                    if doc_id in target_doc_ids:
                        doc_meta = doc_metadata_map.get(doc_id)
                        
                        # Determine author
                        if author_lookup and doc_id in author_lookup:
                            author = author_lookup[doc_id]
                        elif author_filter:
                            author = author_filter
                        else:
                            author = self.relational_brain.get_author_of_document(doc_meta['filename']) if doc_meta else "Unknown"
                        
                        filtered_results.append({
                            "chunk_id": chunk_id,
                            "document_metadata": doc_meta,
                            "author": author,
                            "distance": vector_results['distances'][i][j],
                            "text": vector_results['documents'][i][j]
                        })
        
        return filtered_results

    def query_authored_documents(self, author_name: str) -> Dict[str, Any]:
        """
        Specialized method for author-focused queries.
        """
        print(f"Enhanced Orchestrator received author query for: {author_name}")
        
        filenames = self.relational_brain.get_documents_by_author(author_name)
        
        if not filenames:
            return {
                "status": "success",
                "author": author_name,
                "documents": [],
                "message": f"No documents found for author '{author_name}'"
            }
        
        # Get detailed metadata for each document
        detailed_docs = []
        for filename in filenames:
            metadata_query = f"SELECT * FROM documents WHERE filename = '{filename}'"
            metadata_results = self.analytical_brain.query(metadata_query)
            if metadata_results:
                doc_info = dict(zip(
                    ['id', 'filename', 'size', 'file_type', 'ingested_at'], 
                    metadata_results[0]
                ))
                detailed_docs.append(doc_info)
        
        return {
            "status": "success",
            "author": author_name,
            "documents": detailed_docs,
            "document_count": len(detailed_docs)
        }
