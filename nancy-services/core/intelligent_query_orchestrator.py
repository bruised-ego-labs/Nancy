"""
Intelligent Query Orchestrator for Nancy - TRUE Four-Brain Architecture
Uses LLM for query analysis and response synthesis as advertised in README.md
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain
from .llm_client import LLMClient, QueryIntent, QueryType

class IntelligentQueryOrchestrator:
    """
    True intelligent query orchestrator that uses LLM for query analysis and response synthesis.
    Implements the "Intelligent Query Processing" described in README.md.
    """
    
    def __init__(self):
        print("Initializing Intelligent Query Orchestrator with Lazy Four-Brain Architecture...")
        
        # Lazy initialization - only create brains when needed
        self._vector_brain = None
        self._analytical_brain = None
        self._graph_brain = None
        self._llm_client = None
        
        print("Intelligent Query Orchestrator ready (brains will initialize on-demand)")
    
    @property
    def vector_brain(self):
        """Lazy-load VectorBrain only when needed"""
        if self._vector_brain is None:
            print("  → Initializing VectorBrain (ChromaDB)...")
            self._vector_brain = VectorBrain()
            print("  ✓ VectorBrain ready")
        return self._vector_brain
    
    @property  
    def analytical_brain(self):
        """Lazy-load AnalyticalBrain only when needed"""
        if self._analytical_brain is None:
            print("  → Initializing AnalyticalBrain (DuckDB)...")
            self._analytical_brain = AnalyticalBrain()
            print("  ✓ AnalyticalBrain ready")
        return self._analytical_brain
    
    @property
    def graph_brain(self):
        """Lazy-load GraphBrain only when needed"""
        if self._graph_brain is None:
            print("  → Initializing GraphBrain (Neo4j)...")
            self._graph_brain = GraphBrain()
            print("  ✓ GraphBrain ready")
        return self._graph_brain
    
    @property
    def llm_client(self):
        """Lazy-load LLM Client only when needed"""
        if self._llm_client is None:
            print("  → Initializing LinguisticBrain (Local LLM)...")
            self._llm_client = LLMClient(preferred_llm="local_gemma")
            print("  ✓ LinguisticBrain ready")
        return self._llm_client
    
    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Process query using true four-brain intelligent orchestration:
        1. Use LLM to analyze query intent
        2. Orchestrate searches across appropriate brains
        3. Use LLM to synthesize intelligent response
        """
        print(f"\n=== INTELLIGENT QUERY PROCESSING ===")
        print(f"Query: {query_text}")
        
        try:
            # Step 1: LLM-based Query Intent Analysis
            print("Step 1: Analyzing query intent with LinguisticBrain (LLM)...")
            query_intent = self.llm_client.analyze_query_intent(query_text)
            print(f"✓ Query Intent: {query_intent.query_type.value} (confidence: {query_intent.confidence})")
            print(f"  Reasoning: {query_intent.reasoning}")
            
            # Step 2: Orchestrate Multi-Brain Search
            print("Step 2: Orchestrating multi-brain search...")
            raw_results = self._execute_intelligent_search(query_text, query_intent, n_results)
            
            # Step 3: LLM-based Response Synthesis
            print("Step 3: Synthesizing intelligent response with LinguisticBrain (LLM)...")
            synthesized_response = self.llm_client.synthesize_response(query_text, raw_results, query_intent)
            
            # Return complete intelligent response
            return {
                "query": query_text,
                "strategy_used": f"intelligent_{query_intent.query_type.value}",
                "intent_analysis": {
                    "type": query_intent.query_type.value,
                    "confidence": query_intent.confidence,
                    "reasoning": query_intent.reasoning,
                    "semantic_terms": query_intent.semantic_terms,
                    "entities": query_intent.entities,
                    "time_constraints": query_intent.time_constraints,
                    "metadata_filters": query_intent.metadata_filters,
                    "relationship_targets": query_intent.relationship_targets
                },
                "raw_results": raw_results.get("results", []),
                "synthesized_response": synthesized_response,
                "brains_used": self._determine_brains_used(query_intent),
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Clear error reporting - no silent fallbacks
            error_message = f"Intelligent query processing failed: {str(e)}"
            print(f"❌ {error_message}")
            raise RuntimeError(error_message)
    
    def _execute_intelligent_search(self, query: str, intent: QueryIntent, n_results: int) -> Dict[str, Any]:
        """
        Execute search across appropriate brains based on LLM-analyzed intent
        """
        results = {"results": [], "metadata": {}}
        
        # Vector search (always included for semantic similarity)
        if intent.semantic_terms:
            print("  → VectorBrain: Semantic search")
            vector_results = self.vector_brain.query(intent.semantic_terms, n_results)
            if vector_results and vector_results.get('documents') and vector_results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(zip(
                    vector_results['documents'][0],
                    vector_results['metadatas'][0] if vector_results.get('metadatas') and vector_results['metadatas'][0] else [{}] * len(vector_results['documents'][0]),
                    vector_results['distances'][0] if vector_results.get('distances') and vector_results['distances'][0] else [0.0] * len(vector_results['documents'][0])
                )):
                    results["results"].append({
                        "text": doc,
                        "metadata": metadata,
                        "distance": distance,
                        "source": "vector",
                        "chunk_id": vector_results.get('ids', [[]])[0][i] if vector_results.get('ids') else f"vector_{i}"
                    })
        
        # Analytical search (for metadata queries)
        if intent.query_type in [QueryType.METADATA_FILTER, QueryType.TEMPORAL_ANALYSIS] or intent.time_constraints:
            print("  → AnalyticalBrain: Metadata analysis")
            # Build analytical query based on intent
            analytical_results = self._query_analytical_brain(intent, n_results)
            results["results"].extend(analytical_results)
        
        # Graph search (for relationship queries)
        if intent.query_type in [QueryType.AUTHOR_ATTRIBUTION, QueryType.RELATIONSHIP_DISCOVERY, QueryType.CROSS_REFERENCE]:
            print("  → GraphBrain: Relationship exploration")
            graph_results = self._query_graph_brain(intent, n_results)
            results["results"].extend(graph_results)
        
        # Hybrid complex queries use all brains
        if intent.query_type == QueryType.HYBRID_COMPLEX:
            print("  → All Brains: Complex hybrid analysis")
            # Already got vector results above
            # Add analytical and graph results
            analytical_results = self._query_analytical_brain(intent, n_results // 2)
            graph_results = self._query_graph_brain(intent, n_results // 2)
            results["results"].extend(analytical_results + graph_results)
        
        # Sort by relevance and deduplicate
        results["results"] = self._deduplicate_and_rank_results(results["results"], n_results)
        
        print(f"  ✓ Found {len(results['results'])} total results from {len(self._determine_brains_used(intent))} brains")
        return results
    
    def _query_analytical_brain(self, intent: QueryIntent, n_results: int) -> List[Dict]:
        """Query the analytical brain based on intent"""
        try:
            # Build analytical query based on intent
            if intent.time_constraints:
                # Time-based queries
                if intent.time_constraints.get("start_date") and intent.time_constraints.get("end_date"):
                    query = f"SELECT * FROM documents WHERE ingested_at BETWEEN '{intent.time_constraints['start_date']}' AND '{intent.time_constraints['end_date']}' LIMIT {n_results}"
                else:
                    query = f"SELECT * FROM documents ORDER BY ingested_at DESC LIMIT {n_results}"
            elif intent.metadata_filters:
                # Metadata filtering
                conditions = []
                for key, value in intent.metadata_filters.items():
                    if key == "author":
                        conditions.append(f"author = '{value}'")
                    elif key == "file_type":
                        conditions.append(f"file_type = '{value}'")
                
                where_clause = " AND ".join(conditions) if conditions else "1=1"
                query = f"SELECT * FROM documents WHERE {where_clause} LIMIT {n_results}"
            else:
                # Default to recent documents
                query = f"SELECT * FROM documents ORDER BY ingested_at DESC LIMIT {n_results}"
            
            print(f"    Analytical query: {query}")
            analytical_data = self.analytical_brain.query_documents(query)
            
            results = []
            for doc in analytical_data:
                results.append({
                    "text": f"Document: {doc.get('filename', 'Unknown')} by {doc.get('author', 'Unknown')}",
                    "metadata": doc,
                    "distance": 0.0,  # Not applicable for analytical
                    "source": "analytical",
                    "chunk_id": f"analytical_{doc.get('id', 'unknown')}"
                })
            
            return results
        except Exception as e:
            print(f"    Analytical brain query failed: {e}")
            return []
    
    def _query_graph_brain(self, intent: QueryIntent, n_results: int) -> List[Dict]:
        """Query the graph brain based on intent"""
        try:
            results = []
            
            # Author attribution queries
            if intent.query_type == QueryType.AUTHOR_ATTRIBUTION and intent.entities:
                for entity in intent.entities:
                    print(f"    Searching for documents by: {entity}")
                    authored_docs = self.graph_brain.get_authored_documents(entity)
                    for doc in authored_docs[:n_results]:
                        results.append({
                            "text": f"Document authored by {entity}: {doc.get('filename', doc.get('document', 'Unknown'))}",
                            "metadata": doc,
                            "distance": 0.0,
                            "source": "graph",
                            "chunk_id": f"graph_author_{entity}_{len(results)}"
                        })
            
            # Relationship discovery
            elif intent.query_type == QueryType.RELATIONSHIP_DISCOVERY and intent.relationship_targets:
                for target in intent.relationship_targets:
                    print(f"    Exploring relationships for: {target}")
                    relationships = self.graph_brain.explore_relationships(target)
                    for rel in relationships[:n_results]:
                        results.append({
                            "text": f"Relationship: {rel.get('source', 'Unknown')} -> {rel.get('relationship', 'RELATES')} -> {rel.get('target', 'Unknown')}",
                            "metadata": rel,
                            "distance": 0.0,
                            "source": "graph",
                            "chunk_id": f"graph_rel_{len(results)}"
                        })
            
            # Cross-reference queries
            elif intent.query_type == QueryType.CROSS_REFERENCE:
                print("    Finding document cross-references")
                # Get documents that reference each other
                cross_refs = self.graph_brain.get_cross_references()
                for ref in cross_refs[:n_results]:
                    results.append({
                        "text": f"Cross-reference: {ref.get('source', 'Unknown')} references {ref.get('target', 'Unknown')}",
                        "metadata": ref,
                        "distance": 0.0,
                        "source": "graph",
                        "chunk_id": f"graph_xref_{len(results)}"
                    })
            
            return results[:n_results]
        except Exception as e:
            print(f"    Graph brain query failed: {e}")
            return []
    
    def _deduplicate_and_rank_results(self, results: List[Dict], n_results: int) -> List[Dict]:
        """Remove duplicates and rank results by relevance"""
        seen_texts = set()
        unique_results = []
        
        # Sort by distance (lower is better for vector results)
        results.sort(key=lambda x: x.get('distance', 1.0))
        
        for result in results:
            text_key = result.get('text', '')[:100]  # Use first 100 chars as key
            if text_key not in seen_texts:
                seen_texts.add(text_key)
                unique_results.append(result)
                
                if len(unique_results) >= n_results:
                    break
        
        return unique_results
    
    def _determine_brains_used(self, intent: QueryIntent) -> List[str]:
        """Determine which brains were used based on query intent"""
        brains = ["vector"]  # Vector always used
        
        if intent.query_type in [QueryType.METADATA_FILTER, QueryType.TEMPORAL_ANALYSIS] or intent.time_constraints:
            brains.append("analytical")
        
        if intent.query_type in [QueryType.AUTHOR_ATTRIBUTION, QueryType.RELATIONSHIP_DISCOVERY, QueryType.CROSS_REFERENCE]:
            brains.append("graph")
        
        if intent.query_type == QueryType.HYBRID_COMPLEX:
            brains.extend(["analytical", "graph"])
        
        brains.append("linguistic")  # LLM always used for analysis and synthesis
        return list(set(brains))  # Remove duplicates
    
    def health_check(self) -> Dict[str, Any]:
        """Check health of all four brains"""
        health = {
            "overall": "healthy",
            "brains": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check VectorBrain
        try:
            collections = self.vector_brain.client.list_collections()
            health["brains"]["vector"] = {
                "status": "healthy",
                "collections": len(collections),
                "details": "ChromaDB operational"
            }
        except Exception as e:
            health["brains"]["vector"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health["overall"] = "degraded"
        
        # Check AnalyticalBrain
        try:
            test_query = "SELECT COUNT(*) as count FROM documents"
            result = self.analytical_brain.query_documents(test_query)
            health["brains"]["analytical"] = {
                "status": "healthy",
                "document_count": result[0].get("count", 0) if result else 0,
                "details": "DuckDB operational"
            }
        except Exception as e:
            health["brains"]["analytical"] = {
                "status": "unhealthy",
                "error": str(e) 
            }
            health["overall"] = "degraded"
        
        # Check GraphBrain  
        try:
            # Simple test query
            with self.graph_brain.driver.session() as session:
                result = session.run("RETURN 'Neo4j is working' as message")
                record = result.single()
                health["brains"]["graph"] = {
                    "status": "healthy",
                    "details": record["message"] if record else "Neo4j operational"
                }
        except Exception as e:
            health["brains"]["graph"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["overall"] = "degraded"
        
        # Check LinguisticBrain (LLM)
        try:
            # Test LLM with simple query
            test_intent = self.llm_client.analyze_query_intent("test query")
            health["brains"]["linguistic"] = {
                "status": "healthy",
                "model": self.llm_client.local_model_name,
                "details": "Local LLM operational"
            }
        except Exception as e:
            health["brains"]["linguistic"] = {
                "status": "unhealthy", 
                "error": str(e)
            }
            health["overall"] = "unhealthy"  # LLM is critical
        
        return health