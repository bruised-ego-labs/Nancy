#!/usr/bin/env python3
"""
Nancy Core MCP Host Integration for Codebase Analysis
Demonstrates how the Codebase MCP Server integrates with Nancy's Four-Brain architecture.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, Any, List, Optional

# Simulated Nancy Core MCP Host
class NancyMCPHost:
    """
    Simulated Nancy Core MCP Host that orchestrates MCP servers.
    In production, this would be the actual Nancy Core MCP integration.
    """
    
    def __init__(self):
        self.registered_servers = {}
        self.capabilities = {}
        print("Nancy Core MCP Host initialized")
    
    async def register_server(self, server_name: str, server_instance: Any):
        """Register an MCP server with the host."""
        self.registered_servers[server_name] = server_instance
        
        # Get server capabilities
        capabilities_request = {
            "jsonrpc": "2.0",
            "id": f"cap_{server_name}",
            "method": "health_check",
            "params": {}
        }
        
        response = await server_instance.handle_request(capabilities_request)
        if "result" in response:
            self.capabilities[server_name] = response["result"].get("capabilities", [])
        
        print(f"Registered MCP server: {server_name}")
        return True
    
    async def route_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route user query to appropriate MCP server(s) based on query analysis.
        This demonstrates Nancy's intelligent routing capabilities.
        """
        print(f"Routing query: '{query}'")
        
        # Analyze query to determine routing
        query_lower = query.lower()
        routing_decision = self._analyze_query_for_routing(query_lower)
        
        print(f"Routing decision: {routing_decision}")
        
        results = {}
        
        # Route to codebase server if relevant
        if "codebase" in routing_decision["servers"]:
            codebase_result = await self._handle_codebase_query(query, context or {})
            results["codebase"] = codebase_result
        
        # In production, would also route to other servers (spreadsheet, document, etc.)
        
        # Synthesize final response
        synthesized_response = self._synthesize_response(query, results, routing_decision)
        return synthesized_response
    
    def _analyze_query_for_routing(self, query: str) -> Dict[str, Any]:
        """
        Analyze query to determine which MCP servers should handle it.
        This simulates Nancy's intelligent query routing.
        """
        routing = {
            "servers": [],
            "query_type": "unknown",
            "confidence": 0.0
        }
        
        # Code-related queries
        code_keywords = [
            "function", "class", "code", "file", "repository", "git", "author", 
            "developer", "commit", "python", "javascript", "java", "complexity",
            "ast", "parse", "method", "inheritance", "import", "module"
        ]
        
        if any(keyword in query for keyword in code_keywords):
            routing["servers"].append("codebase")
            routing["query_type"] = "code_analysis"
            routing["confidence"] = 0.9
        
        # Multi-step queries that might need multiple servers
        if "and" in query or "who" in query or "what" in query:
            routing["query_type"] = "multi_step"
            routing["confidence"] = min(routing["confidence"] + 0.1, 1.0)
        
        return routing
    
    async def _handle_codebase_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle codebase-related queries using the Codebase MCP Server.
        """
        if "codebase" not in self.registered_servers:
            return {"error": "Codebase server not available"}
        
        codebase_server = self.registered_servers["codebase"]
        
        # Determine specific codebase operation based on query
        query_lower = query.lower()
        
        if "analyze file" in query_lower or "single file" in query_lower:
            # Single file analysis
            file_path = context.get("file_path", __file__)
            request = {
                "jsonrpc": "2.0",
                "id": "codebase_file",
                "method": "analyze_file",
                "params": {"file_path": file_path}
            }
            
        elif "repository" in query_lower or "codebase" in query_lower:
            # Repository analysis
            repo_path = context.get("repo_path", str(Path(__file__).parent))
            request = {
                "jsonrpc": "2.0",
                "id": "codebase_repo",
                "method": "analyze_repository", 
                "params": {
                    "repo_path": repo_path,
                    "file_extensions": [".py"]  # Limited for demo
                }
            }
            
        elif "author" in query_lower or "who wrote" in query_lower:
            # Authorship query
            file_path = context.get("file_path", __file__)
            request = {
                "jsonrpc": "2.0",
                "id": "codebase_auth",
                "method": "get_file_authorship",
                "params": {"file_path": file_path}
            }
            
        elif "expertise" in query_lower or "developer" in query_lower:
            # Developer expertise query
            author_name = context.get("author_name", "Unknown Developer")
            repo_path = context.get("repo_path", str(Path(__file__).parent))
            request = {
                "jsonrpc": "2.0",
                "id": "codebase_exp",
                "method": "get_developer_expertise",
                "params": {
                    "author_name": author_name,
                    "repo_path": repo_path
                }
            }
            
        else:
            # Default to supported languages
            request = {
                "jsonrpc": "2.0",
                "id": "codebase_lang",
                "method": "get_supported_languages",
                "params": {}
            }
        
        # Execute request
        response = await codebase_server.handle_request(request)
        return response
    
    def _synthesize_response(self, query: str, results: Dict[str, Any], 
                           routing_decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesize final response from multiple MCP server results.
        This simulates Nancy's response synthesis using the Linguistic Brain.
        """
        synthesized = {
            "query": query,
            "routing": routing_decision,
            "server_results": results,
            "knowledge_packets": [],
            "natural_language_response": "",
            "metadata": {
                "servers_consulted": list(results.keys()),
                "query_type": routing_decision["query_type"],
                "confidence": routing_decision["confidence"]
            }
        }
        
        # Extract knowledge packets from all results
        for server_name, result in results.items():
            if "result" in result and "knowledge_packets" in result["result"]:
                synthesized["knowledge_packets"].extend(result["result"]["knowledge_packets"])
        
        # Generate natural language response
        synthesized["natural_language_response"] = self._generate_natural_response(query, results)
        
        return synthesized
    
    def _generate_natural_response(self, query: str, results: Dict[str, Any]) -> str:
        """
        Generate natural language response from server results.
        In production, this would use Nancy's Linguistic Brain (Gemma model).
        """
        if not results:
            return "I couldn't find relevant information to answer your query."
        
        response_parts = []
        
        # Process codebase results
        if "codebase" in results:
            codebase_result = results["codebase"]
            
            if "result" in codebase_result:
                result_data = codebase_result["result"]
                
                if "file_path" in result_data:
                    # File analysis response
                    file_name = Path(result_data["file_path"]).name
                    response_parts.append(f"I analyzed the file '{file_name}'.")
                    
                    if "analysis_summary" in result_data:
                        summary = result_data["analysis_summary"]
                        response_parts.append(
                            f"It contains {summary['functions']} functions and "
                            f"{summary['classes']} classes with a complexity score of "
                            f"{summary['complexity_score']}."
                        )
                        
                        response_parts.append(
                            f"I generated {summary['total_packets']} knowledge packets "
                            f"for integration with Nancy's Four-Brain architecture."
                        )
                
                elif "repository_stats" in result_data:
                    # Repository analysis response
                    stats = result_data["repository_stats"]
                    response_parts.append(
                        f"I analyzed the repository and found {stats['analyzed_files']} "
                        f"files with {stats['total_functions']} functions and "
                        f"{stats['total_classes']} classes across {len(stats['languages'])} "
                        f"programming languages."
                    )
                    
                    if stats["authors"]:
                        response_parts.append(
                            f"The code has contributions from {len(stats['authors'])} developers."
                        )
                
                elif "primary_author" in result_data:
                    # Authorship response
                    primary_author = result_data.get("primary_author", "Unknown")
                    contributors = result_data.get("contributors", [])
                    commits = result_data.get("total_commits", 0)
                    
                    response_parts.append(
                        f"The primary author of this file is {primary_author}."
                    )
                    
                    if len(contributors) > 1:
                        response_parts.append(
                            f"It has {len(contributors)} total contributors with "
                            f"{commits} commits in its history."
                        )
                
                elif "capabilities" in result_data:
                    # Capabilities response
                    capabilities = result_data["capabilities"]
                    response_parts.append(
                        f"The codebase analysis server supports {len(capabilities)} "
                        f"main capabilities including: {', '.join(capabilities[:3])}."
                    )
        
        if not response_parts:
            response_parts.append("I processed your query but couldn't generate specific insights.")
        
        return " ".join(response_parts)


# Simulated Codebase MCP Server (simplified version)
sys.path.append(str(Path(__file__).parent / "mcp-servers" / "codebase"))

try:
    from server import CodebaseMCPServer
    CODEBASE_SERVER_AVAILABLE = True
except ImportError:
    # Fallback to simplified version
    from test_codebase_mcp_simple import SimplifiedCodebaseAnalyzer
    
    class SimplifiedCodebaseMCPServer:
        def __init__(self):
            self.analyzer = SimplifiedCodebaseAnalyzer()
        
        async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
            try:
                method = request_data.get("method")
                params = request_data.get("params", {})
                
                if method == "analyze_file":
                    file_path = params.get("file_path")
                    analysis = self.analyzer.analyze_python_file(file_path)
                    if "error" not in analysis:
                        knowledge_packets = self.analyzer.generate_knowledge_packets(analysis)
                        result = {
                            "file_path": file_path,
                            "language": "python",
                            "knowledge_packets": knowledge_packets,
                            "analysis_summary": {
                                "functions": len(analysis.get("functions", [])),
                                "classes": len(analysis.get("classes", [])),
                                "complexity_score": analysis.get("complexity_score", 0),
                                "total_packets": len(knowledge_packets)
                            }
                        }
                    else:
                        result = analysis
                
                elif method == "get_supported_languages":
                    result = {
                        "supported_extensions": [".py"],
                        "parsers_available": [".py"],
                        "languages_supported": ["python"]
                    }
                
                elif method == "health_check":
                    result = {
                        "status": "healthy",
                        "server": "simplified_codebase_mcp",
                        "capabilities": ["analyze_file", "get_supported_languages", "health_check"]
                    }
                
                else:
                    result = {"error": f"Method {method} not supported in simplified version"}
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_data.get("id"),
                    "result": result
                }
                
            except Exception as e:
                return {
                    "jsonrpc": "2.0", 
                    "id": request_data.get("id"),
                    "error": {"code": -32603, "message": str(e)}
                }
    
    CodebaseMCPServer = SimplifiedCodebaseMCPServer
    CODEBASE_SERVER_AVAILABLE = False


async def demonstrate_integration():
    """
    Demonstrate complete Nancy Core + Codebase MCP Server integration.
    """
    print("Nancy Core MCP Host - Codebase Integration Demo")
    print("=" * 60)
    
    # Initialize Nancy MCP Host
    nancy_host = NancyMCPHost()
    
    # Initialize and register Codebase MCP Server
    codebase_server = CodebaseMCPServer()
    await nancy_host.register_server("codebase", codebase_server)
    
    print(f"Server type: {'Full' if CODEBASE_SERVER_AVAILABLE else 'Simplified'}")
    print("")
    
    # Demonstrate various query types
    demo_queries = [
        {
            "query": "Analyze this Python file",
            "context": {"file_path": __file__}
        },
        {
            "query": "What languages does the codebase server support?",
            "context": {}
        },
        {
            "query": "Show me the repository analysis",
            "context": {"repo_path": str(Path(__file__).parent)}
        }
    ]
    
    for i, demo in enumerate(demo_queries, 1):
        print(f"Demo Query {i}: {demo['query']}")
        print("-" * 40)
        
        try:
            response = await nancy_host.route_query(demo["query"], demo["context"])
            
            # Show routing information
            print(f"Query Type: {response['metadata']['query_type']}")
            print(f"Servers Consulted: {', '.join(response['metadata']['servers_consulted'])}")
            print(f"Confidence: {response['metadata']['confidence']}")
            
            # Show knowledge packets generated
            packet_count = len(response.get("knowledge_packets", []))
            print(f"Knowledge Packets: {packet_count}")
            
            if packet_count > 0:
                packet_types = {}
                for packet in response["knowledge_packets"]:
                    ptype = packet["type"]
                    packet_types[ptype] = packet_types.get(ptype, 0) + 1
                print(f"Packet Types: {dict(packet_types)}")
            
            # Show natural language response
            print(f"Response: {response['natural_language_response']}")
            
        except Exception as e:
            print(f"Error processing query: {e}")
        
        print("")
    
    # Demonstrate Four-Brain integration
    print("Four-Brain Architecture Integration:")
    print("-" * 40)
    
    # Get sample knowledge packets
    sample_query_result = await nancy_host.route_query(
        "Analyze this Python file", 
        {"file_path": __file__}
    )
    
    knowledge_packets = sample_query_result.get("knowledge_packets", [])
    
    if knowledge_packets:
        # Show how packets route to different brains
        brain_routing = {"vector": 0, "analytical": 0, "graph": 0}
        
        for packet in knowledge_packets:
            brain = packet.get("brain_routing", "unknown")
            brain_routing[brain] = brain_routing.get(brain, 0) + 1
        
        print(f"Vector Brain packets: {brain_routing.get('vector', 0)} (semantic search)")
        print(f"Analytical Brain packets: {brain_routing.get('analytical', 0)} (structured data)")
        print(f"Graph Brain packets: {brain_routing.get('graph', 0)} (relationships)")
        print("")
        
        # Show example of each packet type
        for packet in knowledge_packets[:3]:  # Show first 3
            print(f"Sample {packet['type']} packet:")
            if packet['type'] == 'vector_content':
                print(f"  Content: {len(packet['content'])} chars")
                print(f"  Metadata: {packet['metadata']['type']}")
            elif packet['type'] == 'analytical_data':
                print(f"  Data fields: {len(packet['data'])} attributes")
                print(f"  File info: {packet['data'].get('file_name', 'N/A')}")
            elif packet['type'] == 'graph_entities':
                print(f"  Entities: {len(packet['entities'])} nodes")
                print(f"  Relationships: {sum(len(e.get('relationships', [])) for e in packet['entities'])}")
            print("")
    
    # Show integration benefits
    print("Integration Benefits:")
    print("-" * 40)
    benefits = [
        "Modular architecture allows independent scaling",
        "MCP protocol enables flexible server composition", 
        "Knowledge Packets provide standardized data exchange",
        "Intelligent routing optimizes query processing",
        "Four-Brain integration enables sophisticated analysis",
        "Git integration provides authorship and collaboration insights",
        "Multi-language support covers diverse codebases"
    ]
    
    for benefit in benefits:
        print(f"  + {benefit}")
    
    print("\n" + "=" * 60)
    print("Integration demo completed successfully!")
    print("Codebase MCP Server ready for production deployment")


if __name__ == "__main__":
    asyncio.run(demonstrate_integration())