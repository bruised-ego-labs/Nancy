#!/usr/bin/env python3
"""
Nancy Codebase MCP Server
Provides comprehensive codebase analysis capabilities for Nancy's Four-Brain architecture.
Handles Git repositories, AST parsing, and generates standardized Nancy Knowledge Packets.
"""

import asyncio
import json
import sys
import hashlib
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add current directory to path for local imports
sys.path.append(str(Path(__file__).parent))
from ast_analyzer import ASTAnalyzer
from git_analyzer import GitAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MCP protocol classes (simplified for standalone operation)
class MCPRequest:
    """Represents an MCP request."""
    def __init__(self, data: Dict[str, Any]):
        self.jsonrpc = data.get("jsonrpc", "2.0")
        self.id = data.get("id")
        self.method = data.get("method")
        self.params = data.get("params", {})

class MCPResponse:
    """Represents an MCP response."""
    def __init__(self, request_id: Any, result: Any = None, error: Any = None):
        self.jsonrpc = "2.0"
        self.id = request_id
        self.result = result
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        response = {
            "jsonrpc": self.jsonrpc,
            "id": self.id
        }
        if self.error:
            response["error"] = self.error
        else:
            response["result"] = self.result
        return response


class NancyKnowledgePacket:
    """
    Standardized Nancy Knowledge Packet for Four-Brain routing.
    """
    
    @staticmethod
    def create_vector_packet(content: str, doc_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create vector brain packet for semantic content."""
        return {
            "type": "vector_content",
            "doc_id": doc_id,
            "content": content,
            "metadata": metadata,
            "brain_routing": "vector"
        }
    
    @staticmethod
    def create_analytical_packet(data: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        """Create analytical brain packet for structured data."""
        return {
            "type": "analytical_data",
            "doc_id": doc_id,
            "data": data,
            "brain_routing": "analytical"
        }
    
    @staticmethod
    def create_graph_packet(entities: List[Dict[str, Any]], doc_id: str) -> Dict[str, Any]:
        """Create graph brain packet for relationships."""
        return {
            "type": "graph_entities",
            "doc_id": doc_id,
            "entities": entities,
            "brain_routing": "graph"
        }


class CodebaseAnalyzer:
    """
    Main codebase analyzer that orchestrates AST parsing, Git analysis,
    and Knowledge Packet generation for Nancy's Four-Brain architecture.
    """
    
    def __init__(self):
        self.ast_analyzer = ASTAnalyzer()
        self.git_analyzer = GitAnalyzer()
        self.supported_extensions = ['.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.c', '.cpp', '.cc', '.cxx', '.h', '.hpp', '.go', '.rs', '.php', '.rb']
        logger.info("CodebaseAnalyzer initialized with AST and Git analysis capabilities")
    
    def generate_doc_id(self, file_path: str, content: str = None) -> str:
        """Generate unique document ID for codebase files."""
        if content:
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()[:8]
        else:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                content_hash = hashlib.sha256(file_content.encode('utf-8')).hexdigest()[:8]
            except:
                content_hash = hashlib.sha256(file_path.encode('utf-8')).hexdigest()[:8]
        
        filename = Path(file_path).name
        return f"code_{filename}_{content_hash}"
    
    def analyze_single_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze a single code file and generate Knowledge Packets.
        """
        try:
            if not os.path.exists(file_path):
                return {"error": f"File does not exist: {file_path}"}
            
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                except Exception as e:
                    return {"error": f"Failed to read file: {e}"}
            
            doc_id = self.generate_doc_id(file_path, content)
            file_ext = Path(file_path).suffix.lower()
            
            knowledge_packets = []
            
            # 1. AST Analysis
            ast_result = self.ast_analyzer.analyze_code_file(file_path)
            
            # 2. Git Analysis (if in a Git repository)
            git_result = None
            if self.git_analyzer.initialize_repository(os.path.dirname(file_path)):
                git_result = self.git_analyzer.get_file_authorship(file_path)
            
            # 3. Generate Vector Brain Packets (for semantic content)
            vector_packets = self._generate_vector_packets(content, file_path, doc_id, ast_result)
            knowledge_packets.extend(vector_packets)
            
            # 4. Generate Analytical Brain Packets (for structured data)
            analytical_packet = self._generate_analytical_packet(
                file_path, doc_id, ast_result, git_result, content
            )
            knowledge_packets.append(analytical_packet)
            
            # 5. Generate Graph Brain Packets (for relationships)
            graph_packets = self._generate_graph_packets(file_path, doc_id, ast_result, git_result)
            knowledge_packets.extend(graph_packets)
            
            return {
                "file_path": file_path,
                "doc_id": doc_id,
                "language": ast_result.get("language", "unknown"),
                "knowledge_packets": knowledge_packets,
                "ast_analysis": ast_result,
                "git_analysis": git_result,
                "total_packets": len(knowledge_packets)
            }
            
        except Exception as e:
            logger.error(f"Single file analysis failed for {file_path}: {e}")
            return {"error": f"Analysis failed: {e}"}
    
    def analyze_repository(self, repo_path: str, file_extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze entire repository and generate comprehensive Knowledge Packets.
        """
        try:
            if not os.path.exists(repo_path):
                return {"error": f"Repository path does not exist: {repo_path}"}
            
            if file_extensions is None:
                file_extensions = self.supported_extensions
            
            # Initialize Git analyzer
            git_initialized = self.git_analyzer.initialize_repository(repo_path)
            
            all_knowledge_packets = []
            file_analyses = []
            repository_stats = {
                "total_files": 0,
                "analyzed_files": 0,
                "languages": set(),
                "authors": set(),
                "total_functions": 0,
                "total_classes": 0
            }
            
            # Walk through repository
            for root, dirs, files in os.walk(repo_path):
                # Skip common non-source directories
                dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'node_modules', '.venv', 'venv'}]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    
                    repository_stats["total_files"] += 1
                    
                    if file_ext in file_extensions:
                        try:
                            file_analysis = self.analyze_single_file(file_path)
                            
                            if "error" not in file_analysis:
                                file_analyses.append(file_analysis)
                                all_knowledge_packets.extend(file_analysis["knowledge_packets"])
                                
                                # Update repository stats
                                repository_stats["analyzed_files"] += 1
                                repository_stats["languages"].add(file_analysis.get("language", "unknown"))
                                
                                ast_analysis = file_analysis.get("ast_analysis", {})
                                repository_stats["total_functions"] += len(ast_analysis.get("functions", []))
                                repository_stats["total_classes"] += len(ast_analysis.get("classes", []))
                                
                                git_analysis = file_analysis.get("git_analysis")
                                if git_analysis and "contributors" in git_analysis:
                                    repository_stats["authors"].update(git_analysis["contributors"])
                                
                        except Exception as e:
                            logger.warning(f"Failed to analyze {file_path}: {e}")
            
            # Generate repository-level analysis
            repo_analysis = {}
            if git_initialized:
                repo_analysis = self._generate_repository_analysis(repo_path)
            
            # Convert sets to lists for JSON serialization
            repository_stats["languages"] = list(repository_stats["languages"])
            repository_stats["authors"] = list(repository_stats["authors"])
            
            return {
                "repository_path": repo_path,
                "total_knowledge_packets": len(all_knowledge_packets),
                "file_analyses": file_analyses,
                "knowledge_packets": all_knowledge_packets,
                "repository_stats": repository_stats,
                "repository_analysis": repo_analysis,
                "git_enabled": git_initialized
            }
            
        except Exception as e:
            logger.error(f"Repository analysis failed for {repo_path}: {e}")
            return {"error": f"Repository analysis failed: {e}"}
    
    def _generate_vector_packets(self, content: str, file_path: str, doc_id: str, ast_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate vector brain packets for semantic search."""
        packets = []
        
        # Main file content packet
        packets.append(NancyKnowledgePacket.create_vector_packet(
            content=content,
            doc_id=doc_id,
            metadata={
                "file_path": file_path,
                "language": ast_result.get("language", "unknown"),
                "type": "file_content",
                "line_count": ast_result.get("total_lines", 0)
            }
        ))
        
        # Function documentation packets
        for func in ast_result.get("functions", []):
            if func.get("docstring"):
                func_doc_id = f"{doc_id}_func_{func['name']}"
                packets.append(NancyKnowledgePacket.create_vector_packet(
                    content=f"Function {func['name']}: {func['docstring']}",
                    doc_id=func_doc_id,
                    metadata={
                        "file_path": file_path,
                        "type": "function_documentation",
                        "function_name": func['name'],
                        "language": ast_result.get("language", "unknown")
                    }
                ))
        
        # Class documentation packets
        for cls in ast_result.get("classes", []):
            if cls.get("docstring"):
                cls_doc_id = f"{doc_id}_class_{cls['name']}"
                packets.append(NancyKnowledgePacket.create_vector_packet(
                    content=f"Class {cls['name']}: {cls['docstring']}",
                    doc_id=cls_doc_id,
                    metadata={
                        "file_path": file_path,
                        "type": "class_documentation",
                        "class_name": cls['name'],
                        "language": ast_result.get("language", "unknown")
                    }
                ))
        
        return packets
    
    def _generate_analytical_packet(self, file_path: str, doc_id: str, ast_result: Dict[str, Any], 
                                  git_result: Optional[Dict[str, Any]], content: str) -> Dict[str, Any]:
        """Generate analytical brain packet for structured data."""
        data = {
            "file_path": file_path,
            "file_name": Path(file_path).name,
            "file_extension": Path(file_path).suffix.lower(),
            "file_size": len(content),
            "line_count": ast_result.get("total_lines", 0),
            "language": ast_result.get("language", "unknown"),
            "function_count": len(ast_result.get("functions", [])),
            "class_count": len(ast_result.get("classes", [])),
            "complexity_score": ast_result.get("complexity_score", 0),
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        # Add Git information if available
        if git_result and "error" not in git_result:
            data.update({
                "primary_author": git_result.get("primary_author"),
                "contributors": git_result.get("contributors", []),
                "total_commits": git_result.get("total_commits", 0),
                "last_modified": git_result.get("last_modified")
            })
        
        return NancyKnowledgePacket.create_analytical_packet(data, doc_id)
    
    def _generate_graph_packets(self, file_path: str, doc_id: str, ast_result: Dict[str, Any], 
                               git_result: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate graph brain packets for relationships."""
        entities = []
        
        # File entity
        file_entity = {
            "id": doc_id,
            "type": "CodeFile",
            "properties": {
                "name": Path(file_path).name,
                "path": file_path,
                "language": ast_result.get("language", "unknown"),
                "extension": Path(file_path).suffix.lower()
            },
            "relationships": []
        }
        
        # Add authorship relationships
        if git_result and "error" not in git_result:
            primary_author = git_result.get("primary_author")
            if primary_author:
                author_id = f"author_{primary_author.replace(' ', '_').lower()}"
                file_entity["relationships"].append({
                    "type": "AUTHORED_BY",
                    "target_id": author_id,
                    "properties": {"role": "primary_author"}
                })
                
                # Create author entity
                entities.append({
                    "id": author_id,
                    "type": "Developer",
                    "properties": {
                        "name": primary_author,
                        "commits_to_file": git_result.get("total_commits", 0)
                    },
                    "relationships": []
                })
            
            # Add contributor relationships
            for contributor in git_result.get("contributors", []):
                if contributor != primary_author:
                    contributor_id = f"author_{contributor.replace(' ', '_').lower()}"
                    file_entity["relationships"].append({
                        "type": "CONTRIBUTED_TO",
                        "target_id": contributor_id,
                        "properties": {"role": "contributor"}
                    })
        
        entities.append(file_entity)
        
        # Function entities and relationships
        for func in ast_result.get("functions", []):
            func_id = f"{doc_id}_func_{func['name']}"
            func_entity = {
                "id": func_id,
                "type": "Function",
                "properties": {
                    "name": func['name'],
                    "line_start": func.get('line_start', 0),
                    "line_end": func.get('line_end', 0),
                    "is_async": func.get('is_async', False),
                    "complexity": func.get('complexity', 1),
                    "has_docstring": bool(func.get('docstring'))
                },
                "relationships": [{
                    "type": "DEFINED_IN",
                    "target_id": doc_id,
                    "properties": {}
                }]
            }
            entities.append(func_entity)
        
        # Class entities and relationships
        for cls in ast_result.get("classes", []):
            cls_id = f"{doc_id}_class_{cls['name']}"
            cls_entity = {
                "id": cls_id,
                "type": "Class",
                "properties": {
                    "name": cls['name'],
                    "line_start": cls.get('line_start', 0),
                    "line_end": cls.get('line_end', 0),
                    "method_count": len(cls.get('methods', [])),
                    "property_count": len(cls.get('properties', [])),
                    "has_docstring": bool(cls.get('docstring'))
                },
                "relationships": [{
                    "type": "DEFINED_IN",
                    "target_id": doc_id,
                    "properties": {}
                }]
            }
            
            # Add method relationships
            for method in cls.get("methods", []):
                method_id = f"{cls_id}_method_{method['name']}"
                method_entity = {
                    "id": method_id,
                    "type": "Method",
                    "properties": {
                        "name": method['name'],
                        "line_start": method.get('line_start', 0),
                        "is_static": method.get('is_static', False),
                        "is_class_method": method.get('is_class_method', False)
                    },
                    "relationships": [{
                        "type": "METHOD_OF",
                        "target_id": cls_id,
                        "properties": {}
                    }]
                }
                entities.append(method_entity)
            
            entities.append(cls_entity)
        
        return [NancyKnowledgePacket.create_graph_packet(entities, doc_id)]
    
    def _generate_repository_analysis(self, repo_path: str) -> Dict[str, Any]:
        """Generate repository-level analysis using Git data."""
        try:
            repo_summary = self.git_analyzer.get_repository_summary()
            activity_analysis = self.git_analyzer.analyze_repository_activity(days_back=30)
            ownership_analysis = self.git_analyzer.analyze_code_ownership()
            
            return {
                "summary": repo_summary,
                "recent_activity": activity_analysis,
                "code_ownership": ownership_analysis
            }
        except Exception as e:
            logger.error(f"Repository analysis failed: {e}")
            return {"error": f"Repository analysis failed: {e}"}


class CodebaseMCPServer:
    """
    Nancy Codebase MCP Server providing comprehensive code analysis capabilities.
    """
    
    def __init__(self):
        self.analyzer = CodebaseAnalyzer()
        logger.info("Nancy Codebase MCP Server initialized")
    
    async def handle_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests."""
        try:
            request = MCPRequest(request_data)
            
            if request.method == "analyze_file":
                result = await self._handle_analyze_file(request.params)
            elif request.method == "analyze_repository":
                result = await self._handle_analyze_repository(request.params)
            elif request.method == "get_file_authorship":
                result = await self._handle_get_authorship(request.params)
            elif request.method == "get_developer_expertise":
                result = await self._handle_developer_expertise(request.params)
            elif request.method == "get_supported_languages":
                result = await self._handle_supported_languages(request.params)
            elif request.method == "health_check":
                result = await self._handle_health_check(request.params)
            else:
                result = None
                error = {"code": -32601, "message": f"Method not found: {request.method}"}
                return MCPResponse(request.id, error=error).to_dict()
            
            return MCPResponse(request.id, result=result).to_dict()
            
        except Exception as e:
            logger.error(f"Request handling failed: {e}")
            error = {"code": -32603, "message": f"Internal error: {str(e)}"}
            return MCPResponse(request_data.get("id"), error=error).to_dict()
    
    async def _handle_analyze_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle single file analysis request."""
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("file_path parameter is required")
        
        return self.analyzer.analyze_single_file(file_path)
    
    async def _handle_analyze_repository(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle repository analysis request."""
        repo_path = params.get("repo_path")
        file_extensions = params.get("file_extensions")
        
        if not repo_path:
            raise ValueError("repo_path parameter is required")
        
        return self.analyzer.analyze_repository(repo_path, file_extensions)
    
    async def _handle_get_authorship(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file authorship request."""
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("file_path parameter is required")
        
        if not self.analyzer.git_analyzer.initialize_repository(os.path.dirname(file_path)):
            return {"error": "Not a Git repository"}
        
        return self.analyzer.git_analyzer.get_file_authorship(file_path)
    
    async def _handle_developer_expertise(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle developer expertise analysis request."""
        author_name = params.get("author_name")
        repo_path = params.get("repo_path", ".")
        
        if not author_name:
            raise ValueError("author_name parameter is required")
        
        if not self.analyzer.git_analyzer.initialize_repository(repo_path):
            return {"error": "Not a Git repository"}
        
        return self.analyzer.git_analyzer.get_developer_expertise(author_name)
    
    async def _handle_supported_languages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle supported languages request."""
        return {
            "supported_extensions": self.analyzer.ast_analyzer.get_supported_extensions(),
            "parsers_available": list(self.analyzer.ast_analyzer.parsers.keys()),
            "languages_supported": list(self.analyzer.ast_analyzer.languages.keys())
        }
    
    async def _handle_health_check(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle health check request."""
        return {
            "status": "healthy",
            "server": "nancy_codebase_mcp",
            "version": "1.0.0",
            "capabilities": [
                "analyze_file",
                "analyze_repository", 
                "get_file_authorship",
                "get_developer_expertise",
                "get_supported_languages"
            ],
            "ast_parsers": len(self.analyzer.ast_analyzer.parsers),
            "git_support": True
        }


# Main server execution
async def main():
    """Main server loop for standalone testing."""
    server = CodebaseMCPServer()
    
    print("Nancy Codebase MCP Server starting...")
    print("Available methods:")
    print("  - analyze_file: Analyze a single code file")
    print("  - analyze_repository: Analyze entire repository")
    print("  - get_file_authorship: Get Git authorship info")
    print("  - get_developer_expertise: Analyze developer expertise")
    print("  - get_supported_languages: List supported languages")
    print("  - health_check: Server health status")
    print("\nReady for requests...")
    
    # Example usage for testing
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
        if os.path.isfile(test_path):
            print(f"\nTesting file analysis: {test_path}")
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "analyze_file",
                "params": {"file_path": test_path}
            }
        else:
            print(f"\nTesting repository analysis: {test_path}")
            request = {
                "jsonrpc": "2.0", 
                "id": 1,
                "method": "analyze_repository",
                "params": {"repo_path": test_path}
            }
        
        response = await server.handle_request(request)
        print(json.dumps(response, indent=2))


if __name__ == "__main__":
    asyncio.run(main())