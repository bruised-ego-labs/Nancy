"""
LangChain Router-Based Query Orchestrator for Nancy's Four-Brain Architecture

Uses LangChain's router patterns instead of iterative ReAct agents for:
- Fast, deterministic query routing
- Direct brain execution without reasoning loops
- Predictable response times and quality metrics
- Maintains all Four-Brain intelligence capabilities
"""

import json
import time
from typing import Dict, List, Any, Optional, Type
from datetime import datetime
from pydantic import BaseModel, Field

# LangChain imports for routing (not agents)
from langchain.schema import Document
from langchain.prompts import PromptTemplate
from langchain.chains.router import MultiPromptChain, LLMRouterChain
from langchain.chains.router.llm_router import RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.chains import ConversationChain, LLMChain
from langchain.callbacks.base import BaseCallbackHandler
from langchain.llms.base import LLM
import re

# Nancy's existing brains
from .search import AnalyticalBrain
from .knowledge_graph import GraphBrain
from .nlp import VectorBrain
from .llm_client import LLMClient

class Gemma3LLM(LLM):
    """Custom LangChain LLM wrapper for Gemma 3 1B via Google AI API"""
    
    def __init__(self):
        super().__init__()
    
    def _get_llm_client(self):
        """Lazy load LLM client to avoid field validation issues"""
        return LLMClient(preferred_llm="gemini")  # Uses Gemma 3 via our API
    
    @property
    def _llm_type(self) -> str:
        return "gemma-3n-e4b-it"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        # Split system and user parts if formatted with system prompt
        if "\n\nUser:" in prompt and "\nAssistant:" in prompt:
            parts = prompt.split("\n\nUser:")
            system_prompt = parts[0]
            user_prompt = parts[1].replace("\nAssistant:", "")
        else:
            system_prompt = "You are a helpful AI assistant."
            user_prompt = prompt
        
        try:
            llm_client = self._get_llm_client()
            response = llm_client._call_llm(system_prompt, user_prompt)
            return response
        except Exception as e:
            print(f"Gemma 3 LLM call failed: {e}")
            return f"Error: {str(e)}"

class NancyRouterCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for Nancy's router-based logging"""
    
    def __init__(self):
        self.routing_steps = []
        self.start_time = None
        
    def on_chain_start(self, serialized, inputs, **kwargs):
        chain_name = serialized.get('name', 'Unknown Chain')
        print(f"  → Executing Chain: {chain_name}")
        self.routing_steps.append({
            "type": "chain_start",
            "chain": chain_name,
            "timestamp": datetime.now().isoformat()
        })
    
    def on_chain_end(self, outputs, **kwargs):
        print(f"    ✓ Chain completed successfully")
        self.routing_steps.append({
            "type": "chain_end", 
            "timestamp": datetime.now().isoformat()
        })

# Old custom chains removed - using simple chains that work with MultiPromptChain

# Old custom chains removed - using simple chains that work with MultiPromptChain

def create_simple_destination_chains(vector_brain, analytical_brain, graph_brain, llm):
    """Create destination chains that actually call Nancy's brains and work with MultiPromptChain"""
    
    # Custom chains that actually execute brain logic
    from langchain.chains.base import Chain
    
    class VectorBrainChain(Chain):
        """Chain that actually calls VectorBrain"""
        
        @property
        def input_keys(self):
            return ["input"]
            
        @property  
        def output_keys(self):
            return ["text"]
        
        def _call(self, inputs, run_manager=None):
            query = inputs["input"]
            original_query = query.split('.')[0]  # Remove router additions
            print(f"VectorBrain executing search for: {original_query}")
            
            try:
                results = vector_brain.query([original_query], 5)
                
                if not results or not results.get('documents') or not results['documents'][0]:
                    return {"text": "VECTOR_SEARCH_RESULTS: No relevant documents found."}
                
                # Return raw context for synthesis step
                context_parts = []
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0][:3],
                    results['metadatas'][0][:3] if results.get('metadatas') and results['metadatas'][0] else [{}] * 3,
                    results['distances'][0][:3] if results.get('distances') and results['distances'][0] else [0.0] * 3
                )):
                    source_file = metadata.get('source', 'Unknown file')
                    context_parts.append(f"Source: {source_file}\nContent: {doc[:500]}...")
                
                # Return raw results with special prefix for synthesis detection
                raw_results = "VECTOR_SEARCH_RESULTS:\n" + "\n\n".join(context_parts[:3])
                return {"text": raw_results}
                    
            except Exception as e:
                return {"text": f"VECTOR_SEARCH_ERROR: {str(e)}"}
    
    class AnalyticalBrainChain(Chain):
        """Chain that actually calls AnalyticalBrain"""
        
        @property
        def input_keys(self):
            return ["input"]
            
        @property
        def output_keys(self):
            return ["text"]
        
        def _call(self, inputs, run_manager=None):
            query = inputs["input"].lower()
            print(f"AnalyticalBrain executing query: {query}")
            
            try:
                if 'count' in query or 'how many' in query or 'number' in query:
                    sql = "SELECT COUNT(*) as total_files, AVG(size) as avg_size, COUNT(DISTINCT file_type) as file_types FROM documents"
                elif 'recent' in query or 'latest' in query:
                    sql = "SELECT filename, size, file_type, ingested_at FROM documents ORDER BY ingested_at DESC LIMIT 10"
                else:
                    sql = "SELECT filename, size, file_type FROM documents LIMIT 10"
                
                print(f"Executing SQL: {sql}")
                results = analytical_brain.query(sql)
                print(f"DEBUG: Query results: {results}")
                
                if not results:
                    response = "No database results found."
                elif 'COUNT' in sql:
                    # Handle COUNT query results more carefully
                    response = "Database statistics:\n"
                    try:
                        row = results[0]
                        print(f"DEBUG: COUNT query result row: {row}")
                        total = str(row[0]) if row[0] is not None else "0"
                        avg_size = str(row[1]) if len(row) > 1 and row[1] is not None else "0"
                        file_types = str(row[2]) if len(row) > 2 and row[2] is not None else "0"
                        response += f"• Total files: {total}\n• Average size: {avg_size} bytes\n• File types: {file_types}"
                    except Exception as e:
                        response += f"Error processing COUNT results: {str(e)}"
                else:
                    response_parts = [f"Database results ({len(results)} files):"]
                    for i, row in enumerate(results[:10], 1):
                        try:
                            if len(row) >= 3:
                                filename = str(row[0]) if row[0] is not None else "unknown"
                                size = str(row[1]) if row[1] is not None else "0"
                                file_type = str(row[2]) if row[2] is not None else "unknown"
                                if len(row) > 3 and row[3] is not None:
                                    timestamp = str(row[3])
                                    response_parts.append(f"{i}. {filename} ({file_type}, {size} bytes) - {timestamp}")
                                else:
                                    response_parts.append(f"{i}. {filename} ({file_type}, {size} bytes)")
                        except Exception as row_error:
                            response_parts.append(f"{i}. Error processing row: {str(row_error)}")
                    response = "\n".join(response_parts)
                    
            except Exception as e:
                response = f"Database query error: {str(e)}"
            
            return {"text": response}
    
    class GraphBrainChain(Chain):
        """Chain that actually calls GraphBrain"""
        
        @property
        def input_keys(self):
            return ["input"]
            
        @property
        def output_keys(self):
            return ["text"]
        
        def _call(self, inputs, run_manager=None):
            query = inputs["input"].lower()
            original_query = inputs["input"]
            print(f"GraphBrain executing enhanced query: {query}")
            
            try:
                # Enhanced routing using foundational relationship schema
                if any(word in query for word in ['expert', 'expertise', 'specialist']):
                    # Use expertise-based queries
                    topic_keywords = ["thermal", "electrical", "mechanical", "firmware", "software", "design"]
                    for keyword in topic_keywords:
                        if keyword in query:
                            expertise_results = graph_brain.find_expertise_and_roles(topic=keyword)
                            if expertise_results:
                                response = f"GRAPH_EXPERTISE_RESULTS: {keyword} expertise: {expertise_results}"
                                return {"text": response}
                    
                    # Fallback to general expertise
                    all_expertise = graph_brain.find_expertise_and_roles()
                    response = f"GRAPH_EXPERTISE_RESULTS: All expertise areas: {all_expertise[:10]}"
                    
                elif any(word in query for word in ['technical', 'system', 'component', 'interface']):
                    # Use technical relationship queries
                    technical_terms = ["thermal", "electrical", "mechanical", "processor", "memory", "circuit"]
                    for term in technical_terms:
                        if term in query:
                            tech_relationships = graph_brain.find_technical_relationships(term)
                            if tech_relationships:
                                response = f"GRAPH_TECHNICAL_RESULTS: {term} relationships: {tech_relationships}"
                                return {"text": response}
                    
                    # Fallback to cross-references
                    cross_refs = graph_brain.get_cross_references()
                    response = f"GRAPH_TECHNICAL_RESULTS: Technical cross-references: {cross_refs[:5]}"
                    
                elif any(word in query for word in ['decision', 'decide', 'choice', 'why']):
                    # Use decision/project management queries
                    query_words = query.split()
                    for word in query_words:
                        if len(word) > 4:
                            decision_provenance = graph_brain.find_decision_provenance(word)
                            if decision_provenance:
                                response = f"GRAPH_DECISION_RESULTS: Decision provenance for {word}: {decision_provenance}"
                                return {"text": response}
                    
                    # Fallback: show general decision structure
                    response = "GRAPH_DECISION_RESULTS: No specific decision provenance found for this query"
                    
                elif any(word in query for word in ['collaborate', 'team', 'work together']):
                    # Use collaboration queries
                    collaboration_data = graph_brain.get_author_collaboration_network()
                    if collaboration_data:
                        response = f"GRAPH_COLLABORATION_RESULTS: Collaboration network: {collaboration_data[:5]}"
                    else:
                        response = "GRAPH_COLLABORATION_RESULTS: No collaboration data found"
                        
                elif 'author' in query and ('list' in query or 'show' in query):
                    # Get all authors from Neo4j
                    with graph_brain.driver.session() as session:
                        result = session.run("MATCH (p:Person) RETURN p.name as name")
                        authors = [record["name"] for record in result]
                        print(f"Found {len(authors)} authors in graph database")
                        if authors:
                            response = f"GRAPH_AUTHOR_RESULTS: Authors in graph database ({len(authors)} found): {', '.join(authors)}"
                        else:
                            response = "GRAPH_AUTHOR_RESULTS: No authors found in the graph database"
                            
                elif 'who wrote' in query or ('author' in query and ('named' in query or 'called' in query)):
                    # Try to extract author name from query
                    import re
                    name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
                    potential_names = re.findall(name_pattern, original_query)
                    
                    if potential_names:
                        for name in potential_names:
                            if name not in ['What', 'Who', 'Where', 'When', 'How', 'The', 'Is']:
                                print(f"Searching for author: {name}")
                                docs = graph_brain.get_documents_by_author(name)
                                if docs:
                                    response = f"GRAPH_AUTHOR_RESULTS: Documents by {name}:\n" + "\n".join([f"• {doc}" for doc in docs])
                                    break
                        else:
                            # Author not found, show available authors
                            with graph_brain.driver.session() as session:
                                result = session.run("MATCH (p:Person) RETURN p.name as name")
                                authors = [record["name"] for record in result]
                                if authors:
                                    response = f"GRAPH_AUTHOR_RESULTS: Author not found. Available authors: {', '.join(authors)}"
                                else:
                                    response = "GRAPH_AUTHOR_RESULTS: No authors found in graph database"
                    else:
                        response = "GRAPH_AUTHOR_RESULTS: No author name detected in query. Available authors: Mike Rodriguez, Sarah Chen, Lisa Park, Scott Johnson"
                else:
                    # Enhanced fallback: use general relationship exploration
                    print("Using enhanced relationship exploration...")
                    relationships = graph_brain.get_knowledge_graph_statistics()
                    if relationships:
                        response = f"GRAPH_GENERAL_RESULTS: Knowledge graph overview: {relationships}"
                    else:
                        # Ultimate fallback: show all authors
                        with graph_brain.driver.session() as session:
                            result = session.run("MATCH (p:Person) RETURN p.name as name")
                            authors = [record["name"] for record in result]
                            if authors:
                                response = f"GRAPH_AUTHOR_RESULTS: Available authors: {', '.join(authors)}"
                            else:
                                response = "GRAPH_AUTHOR_RESULTS: No authors found in graph database"
                            
            except Exception as e:
                response = f"GRAPH_ERROR: Graph database error: {str(e)}"
            
            return {"text": response}
    
    return {
        "vector_brain": VectorBrainChain(),
        "analytical_brain": AnalyticalBrainChain(),
        "graph_brain": GraphBrainChain()
    }

def create_query_router(llm):
    """Create the main query router that decides which brain to use"""
    
    # Create destination info for the router with concrete examples
    destinations = [
        "vector_brain: Use this for questions about the *content or substance* of documents. Examples: 'What are the thermal constraints?', 'Summarize the key integration points', 'What are the system requirements?', 'Explain the electrical design decisions'",
        "analytical_brain: Use this *only* for questions about file metadata and statistics. Examples: 'How many files are in the project?', 'What is the largest file?', 'Show me recent files', 'List all document types'", 
        "graph_brain: Use this for questions about *relationships, expertise, decisions, and collaboration*. Examples: 'Who are the thermal experts?', 'What technical systems interface with electrical components?', 'What decisions influenced the design?', 'Who collaborated on this project?', 'Show me all authors'"
    ]
    
    destinations_str = "\n".join(destinations)
    router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(destinations=destinations_str)
    
    router_prompt = PromptTemplate(
        template=router_template,
        input_variables=["input"],
        output_parser=RouterOutputParser(),
    )
    
    # Create router chain
    router_chain = LLMRouterChain.from_llm(llm, router_prompt)
    
    return router_chain

class LangChainOrchestrator:
    """
    LangChain Router-Based orchestrator that uses deterministic routing
    instead of iterative ReAct agents for faster, more predictable responses.
    """
    
    def __init__(self):
        print("Initializing LangChain Router-Based Nancy Orchestrator...")
        
        # Initialize Nancy's brains
        print("  → Initializing Nancy's Four Brains...")
        self.vector_brain = VectorBrain()
        self.analytical_brain = AnalyticalBrain() 
        self.graph_brain = GraphBrain()
        self.llm_client = LLMClient(preferred_llm="gemini")
        
        # Initialize LangChain LLM - use Gemma 3 1B for everything
        print("  → Initializing LangChain LLM connection...")
        import os
        
        # Use Gemma 3 1B for LangChain router via custom wrapper
        self.langchain_llm = Gemma3LLM()
        print("  ✓ LangChain using Gemma 3 1B for routing, analysis, and synthesis")
        
        # Create brain-specific chains (simple versions compatible with router)
        print("  → Creating Brain-specific LangChain Chains...")
        self.destination_chains = create_simple_destination_chains(
            self.vector_brain, self.analytical_brain, self.graph_brain, self.langchain_llm
        )
        
        # Create the router
        print("  → Setting up Query Router...")
        self.router_chain = create_query_router(self.langchain_llm)
        
        # Create the multi-prompt chain
        self.multi_prompt_chain = MultiPromptChain(
            router_chain=self.router_chain,
            destination_chains=self.destination_chains,
            default_chain=self.destination_chains["vector_brain"],  # Default to vector search
            verbose=True
        )
        
        # Create custom callback handler
        self.callback_handler = NancyRouterCallbackHandler()
        
        print("✓ LangChain Router-Based Nancy Orchestrator ready!")
        print(f"  Available Brains: {', '.join(self.destination_chains.keys())}")
    
    def query(self, query_text: str, n_results: int = 5) -> Dict[str, Any]:
        """
        Process query using LangChain router for deterministic brain selection
        """
        print(f"\n=== LANGCHAIN ROUTER-BASED NANCY QUERY ===")
        print(f"Query: {query_text}")
        
        start_time = time.time()
        
        try:
            # Reset callback handler for this query
            self.callback_handler.routing_steps = []
            self.callback_handler.start_time = start_time
            
            # Step 1: Analyze query complexity and determine strategy
            print("Step 1: Analyzing query complexity...")
            multi_step_needed = self._needs_multi_step_processing(query_text)
            
            if multi_step_needed:
                print("Step 2: Multi-step processing detected - first finding content, then relationships...")
                response = self._execute_multi_step_query(query_text)
            else:
                print("Step 2: Single-step processing - routing to appropriate brain...")
                result = self.multi_prompt_chain.invoke(
                    {"input": query_text}, 
                    callbacks=[self.callback_handler]
                )
                raw_response = result["text"]
                
                # Step 3: Check if response needs synthesis
                print("Step 3: Checking if synthesis is needed...")
                if raw_response.startswith("VECTOR_SEARCH_RESULTS:") or raw_response.startswith("Database results"):
                    print("Step 4: Performing final synthesis...")
                    # Extract raw data and synthesize final answer
                    llm_client = LLMClient(preferred_llm="gemini")
                    system_prompt = "You are Nancy, an AI assistant for engineering teams. Based on the provided information, answer the user's question directly and concisely. Provide specific information from the sources."
                    user_prompt = f"Original question: {query_text}\n\nRetrieved information:\n{raw_response}\n\nPlease provide a direct, synthesized answer to the question:"
                    
                    response = llm_client._call_llm(system_prompt, user_prompt)
                else:
                    response = raw_response
            
            query_time = time.time() - start_time
            print(f"✓ LangChain Router + Synthesis completed in {query_time:.1f}s")
            
            # Extract routing information
            selected_brain = "unknown"
            confidence = 0.5
            
            # Try to extract which brain was selected from callback steps
            for step in self.callback_handler.routing_steps:
                if step.get("type") == "chain_start":
                    chain_name = step.get("chain", "")
                    if "vector" in chain_name.lower():
                        selected_brain = "vector_brain"
                        confidence = 0.8
                    elif "analytical" in chain_name.lower():
                        selected_brain = "analytical_brain"
                        confidence = 0.8
                    elif "graph" in chain_name.lower():
                        selected_brain = "graph_brain"
                        confidence = 0.9
                    break
            
            return {
                "query": query_text,
                "strategy_used": "langchain_router",
                "response": response,
                "routing_info": {
                    "selected_brain": selected_brain,
                    "confidence": confidence,
                    "routing_method": "llm_router"
                },
                "routing_steps": self.callback_handler.routing_steps,
                "query_time": query_time,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            query_time = time.time() - start_time
            error_message = f"LangChain router orchestration failed: {str(e)}"
            print(f"❌ {error_message}")
            
            return {
                "query": query_text,
                "strategy_used": "langchain_router",
                "response": f"I encountered an error processing your query: {error_message}",
                "error": error_message,
                "routing_steps": self.callback_handler.routing_steps,
                "query_time": query_time,
                "processing_timestamp": datetime.utcnow().isoformat()
            }
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check health of LangChain router orchestrator and all brain chains
        """
        health = {
            "overall": "healthy",
            "orchestrator": "langchain_router",
            "brains": {},
            "router_ready": False,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Test each brain individually
        try:
            # Test vector brain
            test_result = self.vector_brain.query(["test"], 1)
            health["brains"]["vector"] = {
                "status": "healthy" if test_result else "degraded",
                "details": "ChromaDB operational"
            }
        except Exception as e:
            health["brains"]["vector"] = {"status": "unhealthy", "error": str(e)}
            health["overall"] = "degraded"
            
        try:
            # Test analytical brain  
            test_result = self.analytical_brain.query("SELECT COUNT(*) FROM documents LIMIT 1")
            health["brains"]["analytical"] = {
                "status": "healthy" if test_result else "degraded",
                "details": "DuckDB operational"
            }
        except Exception as e:
            health["brains"]["analytical"] = {"status": "unhealthy", "error": str(e)}
            health["overall"] = "degraded"
            
        try:
            # Test graph brain
            with self.graph_brain.driver.session() as session:
                result = session.run("MATCH (n) RETURN count(n) as total LIMIT 1")
                health["brains"]["graph"] = {
                    "status": "healthy",
                    "details": "Neo4j operational"
                }
        except Exception as e:
            health["brains"]["graph"] = {"status": "unhealthy", "error": str(e)}
            health["overall"] = "degraded"
            
        # Test router chain
        try:
            if self.multi_prompt_chain and self.router_chain:
                health["router_ready"] = True
            else:
                health["overall"] = "unhealthy"
        except Exception as e:
            health["router_ready"] = False
            health["router_error"] = str(e)
            health["overall"] = "unhealthy"
        
        return health
    
    def _needs_multi_step_processing(self, query: str) -> bool:
        """
        Determine if a query needs multi-step processing based on complexity patterns
        """
        query_lower = query.lower()
        
        # Look for patterns that require finding content first, then relationships
        multi_part_patterns = [
            # "What X and who Y" patterns
            ("what" in query_lower and "who" in query_lower),
            # "How X relate to Y" patterns - need graph relationships
            ("how" in query_lower and any(word in query_lower for word in ["relate", "connect", "impact", "affect", "influence"])),
            # Questions about relationships between technical concepts
            ("relationship" in query_lower or "dependencies" in query_lower),
            # Complex technical queries that might involve multiple domains
            (len([word for word in ["electrical", "mechanical", "thermal", "firmware", "software"] if word in query_lower]) > 1),
        ]
        
        return any(multi_part_patterns)
    
    def _execute_multi_step_query(self, query: str) -> str:
        """
        Execute a multi-step query: first find relevant content, then explore relationships
        """
        print("  → Step 2a: Finding relevant content with vector search...")
        
        # Step 1: Get relevant context using vector brain
        try:
            vector_results = self.vector_brain.query([query], 5)
            
            if not vector_results or not vector_results.get('documents') or not vector_results['documents'][0]:
                return "No relevant documents found to analyze relationships."
            
            # Prepare context from vector search
            context_parts = []
            for i, (doc, metadata, distance) in enumerate(zip(
                vector_results['documents'][0][:3],
                vector_results['metadatas'][0][:3] if vector_results.get('metadatas') and vector_results['metadatas'][0] else [{}] * 3,
                vector_results['distances'][0][:3] if vector_results.get('distances') and vector_results['distances'][0] else [0.0] * 3
            )):
                source_file = metadata.get('source', 'Unknown file')
                context_parts.append(f"Source: {source_file}\nContent: {doc[:500]}...")
            
            context_summary = "\n\n".join(context_parts[:3])
            
            print("  → Step 2b: Exploring relationships in the found context...")
            
            # Step 2: Now explore relationships using the enhanced graph brain
            relationship_context = self._explore_contextual_relationships(query, context_summary)
            
            # Step 3: Synthesize findings from both vector search and graph relationships
            llm_client = LLMClient(preferred_llm="gemini")
            system_prompt = """You are Nancy, an AI assistant for engineering teams. You have access to a multi-brain architecture that finds both semantic content and relationship data.

Your task is to synthesize information from both document content and relationship analysis to provide comprehensive answers. Focus on:
- Technical details from the documents
- People involved and their expertise/roles
- How systems and components relate to each other
- Decision chains and responsibilities
- Cross-domain impacts and dependencies"""
            
            combined_context = f"DOCUMENT CONTENT:\n{context_summary}\n\nRELATIONSHIP ANALYSIS:\n{relationship_context}"
            user_prompt = f"Original question: {query}\n\nCombined analysis:\n{combined_context}\n\nProvide a comprehensive answer that synthesizes both the technical content and relationship insights:"
            
            response = llm_client._call_llm(system_prompt, user_prompt)
            return response
            
        except Exception as e:
            print(f"Multi-step query failed: {e}")
            return f"Error in multi-step processing: {str(e)}"
    
    def _explore_contextual_relationships(self, query: str, context_summary: str) -> str:
        """
        Explore relationships in the graph brain based on query type and context
        """
        query_lower = query.lower()
        
        # Analyze query to determine which types of relationships to explore
        relationship_insights = []
        
        try:
            # 1. Check for people/expertise questions
            if any(word in query_lower for word in ["who", "expert", "expertise", "team", "role"]):
                print("    → Exploring people and expertise relationships...")
                
                # Extract potential names or expertise areas from query
                import re
                name_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
                potential_names = re.findall(name_pattern, query)
                
                if potential_names:
                    for name in potential_names:
                        if name not in ['What', 'Who', 'Where', 'When', 'How', 'The', 'Is', 'Are']:
                            expertise_results = self.graph_brain.find_expertise_and_roles(person_name=name)
                            if expertise_results:
                                relationship_insights.append(f"Expertise for {name}: {expertise_results}")
                
                # Also look for topic-based expertise
                topic_keywords = ["thermal", "electrical", "mechanical", "firmware", "software", "design"]
                for keyword in topic_keywords:
                    if keyword in query_lower:
                        topic_experts = self.graph_brain.find_expertise_and_roles(topic=keyword)
                        if topic_experts:
                            relationship_insights.append(f"{keyword} experts: {topic_experts}")
            
            # 2. Check for technical relationships
            if any(word in query_lower for word in ["system", "component", "interface", "depend", "constraint", "affect"]):
                print("    → Exploring technical system relationships...")
                
                # Look for technical terms in the context to explore
                technical_terms = ["thermal", "electrical", "mechanical", "memory", "processor", "circuit", "power"]
                for term in technical_terms:
                    if term in query_lower or term in context_summary.lower():
                        tech_relationships = self.graph_brain.find_technical_relationships(term)
                        if tech_relationships:
                            relationship_insights.append(f"Technical relationships for {term}: {tech_relationships}")
            
            # 3. Check for cross-team/collaboration questions
            if any(word in query_lower for word in ["collaborate", "work together", "team", "influence", "impact"]):
                print("    → Exploring collaboration relationships...")
                
                # Look for collaboration networks
                collaboration_data = self.graph_brain.get_author_collaboration_network()
                if collaboration_data:
                    relationship_insights.append(f"Collaboration network: {collaboration_data[:5]}")  # Limit results
            
            # 4. Check for decision/project management questions
            if any(word in query_lower for word in ["decision", "decide", "choice", "why", "reason", "approve"]):
                print("    → Exploring decision relationships...")
                
                # Extract potential topics from query for decision analysis
                topic_words = query_lower.split()
                for word in topic_words:
                    if len(word) > 4 and word not in ["decision", "decide", "choice", "about", "regarding"]:
                        decision_provenance = self.graph_brain.find_decision_provenance(word)
                        if decision_provenance:
                            relationship_insights.append(f"Decision provenance for {word}: {decision_provenance}")
            
            # 5. Check for cross-disciplinary relationships
            disciplines = ["electrical", "mechanical", "thermal", "firmware", "software"]
            query_disciplines = [d for d in disciplines if d in query_lower]
            if len(query_disciplines) > 1:
                print("    → Exploring cross-disciplinary relationships...")
                
                for discipline in query_disciplines:
                    cross_refs = self.graph_brain.get_cross_references()
                    discipline_refs = [ref for ref in cross_refs if discipline in ref.get('source', '').lower() or discipline in ref.get('target', '').lower()]
                    if discipline_refs:
                        relationship_insights.append(f"Cross-references for {discipline}: {discipline_refs[:3]}")
            
            # Compile relationship insights
            if relationship_insights:
                relationship_context = "RELATIONSHIP ANALYSIS FINDINGS:\n\n" + "\n\n".join(relationship_insights)
                print(f"    ✓ Found {len(relationship_insights)} relationship insights")
                return relationship_context
            else:
                print("    → No specific relationships found, using general exploration...")
                
                # Fallback: try to find any relationships for entities mentioned in the context
                words = context_summary.split()
                for word in words[:10]:  # Check first 10 words for entities
                    if len(word) > 4 and word.isalpha() and word[0].isupper():
                        entity_relationships = self.graph_brain.explore_relationships(word)
                        if entity_relationships:
                            relationship_insights.append(f"Relationships for {word}: {entity_relationships[:2]}")
                            break
                
                if relationship_insights:
                    return "GENERAL RELATIONSHIP FINDINGS:\n\n" + "\n\n".join(relationship_insights)
                else:
                    return "No significant relationships found in the graph brain for this query."
        
        except Exception as e:
            print(f"Error exploring relationships: {e}")
            return f"Error exploring relationships: {str(e)}"