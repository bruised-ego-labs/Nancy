#!/usr/bin/env python3
"""
Simplified test script for Nancy Codebase MCP Server
Demonstrates core functionality without requiring tree-sitter dependencies.
"""

import asyncio
import json
import sys
import os
import ast
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Simplified Knowledge Packet class for testing
class NancyKnowledgePacket:
    @staticmethod
    def create_vector_packet(content: str, doc_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "type": "vector_content",
            "doc_id": doc_id,
            "content": content,
            "metadata": metadata,
            "brain_routing": "vector"
        }
    
    @staticmethod
    def create_analytical_packet(data: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
        return {
            "type": "analytical_data",
            "doc_id": doc_id,
            "data": data,
            "brain_routing": "analytical"
        }
    
    @staticmethod
    def create_graph_packet(entities: List[Dict[str, Any]], doc_id: str) -> Dict[str, Any]:
        return {
            "type": "graph_entities",
            "doc_id": doc_id,
            "entities": entities,
            "brain_routing": "graph"
        }


class SimplifiedCodebaseAnalyzer:
    """
    Simplified codebase analyzer for demonstration purposes.
    Uses only built-in Python AST module for analysis.
    """
    
    def __init__(self):
        self.supported_extensions = ['.py']
        print("SimplifiedCodebaseAnalyzer initialized (Python AST only)")
    
    def generate_doc_id(self, file_path: str, content: str = None) -> str:
        """Generate unique document ID."""
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
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file using built-in AST."""
        try:
            if not os.path.exists(file_path):
                return {"error": f"File does not exist: {file_path}"}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse with Python AST
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "docstring": ast.get_docstring(node),
                        "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "complexity": self._calculate_complexity(node)
                    })
                
                elif isinstance(node, ast.ClassDef):
                    class_methods = []
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_methods.append({
                                "name": item.name,
                                "line_start": item.lineno,
                                "docstring": ast.get_docstring(item)
                            })
                    
                    classes.append({
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "docstring": ast.get_docstring(node),
                        "methods": class_methods,
                        "method_count": len(class_methods)
                    })
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
                    else:
                        for alias in node.names:
                            imports.append({
                                "type": "from_import",
                                "module": node.module,
                                "name": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
            
            return {
                "language": "python",
                "file_path": file_path,
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "total_lines": len(content.split('\n')),
                "complexity_score": sum(func.get('complexity', 1) for func in functions),
                "content": content
            }
            
        except Exception as e:
            return {"error": f"Analysis failed: {e}"}
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity
    
    def generate_knowledge_packets(self, analysis_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate Nancy Knowledge Packets from analysis."""
        if "error" in analysis_result:
            return []
        
        file_path = analysis_result["file_path"]
        content = analysis_result["content"]
        doc_id = self.generate_doc_id(file_path, content)
        
        packets = []
        
        # 1. Vector Brain Packets
        # Main file content
        packets.append(NancyKnowledgePacket.create_vector_packet(
            content=content,
            doc_id=doc_id,
            metadata={
                "file_path": file_path,
                "language": "python",
                "type": "file_content",
                "line_count": analysis_result["total_lines"]
            }
        ))
        
        # Function documentation
        for func in analysis_result["functions"]:
            if func.get("docstring"):
                func_doc_id = f"{doc_id}_func_{func['name']}"
                packets.append(NancyKnowledgePacket.create_vector_packet(
                    content=f"Function {func['name']}: {func['docstring']}",
                    doc_id=func_doc_id,
                    metadata={
                        "file_path": file_path,
                        "type": "function_documentation",
                        "function_name": func['name'],
                        "language": "python"
                    }
                ))
        
        # Class documentation
        for cls in analysis_result["classes"]:
            if cls.get("docstring"):
                cls_doc_id = f"{doc_id}_class_{cls['name']}"
                packets.append(NancyKnowledgePacket.create_vector_packet(
                    content=f"Class {cls['name']}: {cls['docstring']}",
                    doc_id=cls_doc_id,
                    metadata={
                        "file_path": file_path,
                        "type": "class_documentation",
                        "class_name": cls['name'],
                        "language": "python"
                    }
                ))
        
        # 2. Analytical Brain Packet
        packets.append(NancyKnowledgePacket.create_analytical_packet(
            data={
                "file_path": file_path,
                "file_name": Path(file_path).name,
                "file_extension": ".py",
                "file_size": len(content),
                "line_count": analysis_result["total_lines"],
                "language": "python",
                "function_count": len(analysis_result["functions"]),
                "class_count": len(analysis_result["classes"]),
                "import_count": len(analysis_result["imports"]),
                "complexity_score": analysis_result["complexity_score"],
                "analysis_timestamp": datetime.now().isoformat()
            },
            doc_id=doc_id
        ))
        
        # 3. Graph Brain Packets
        entities = []
        
        # File entity
        file_entity = {
            "id": doc_id,
            "type": "CodeFile",
            "properties": {
                "name": Path(file_path).name,
                "path": file_path,
                "language": "python",
                "extension": ".py"
            },
            "relationships": []
        }
        entities.append(file_entity)
        
        # Function entities
        for func in analysis_result["functions"]:
            func_id = f"{doc_id}_func_{func['name']}"
            func_entity = {
                "id": func_id,
                "type": "Function",
                "properties": {
                    "name": func['name'],
                    "line_start": func['line_start'],
                    "line_end": func['line_end'],
                    "is_async": func['is_async'],
                    "complexity": func['complexity'],
                    "has_docstring": bool(func.get('docstring'))
                },
                "relationships": [{
                    "type": "DEFINED_IN",
                    "target_id": doc_id,
                    "properties": {}
                }]
            }
            entities.append(func_entity)
        
        # Class entities
        for cls in analysis_result["classes"]:
            cls_id = f"{doc_id}_class_{cls['name']}"
            cls_entity = {
                "id": cls_id,
                "type": "Class",
                "properties": {
                    "name": cls['name'],
                    "line_start": cls['line_start'],
                    "line_end": cls['line_end'],
                    "method_count": cls['method_count'],
                    "has_docstring": bool(cls.get('docstring'))
                },
                "relationships": [{
                    "type": "DEFINED_IN",
                    "target_id": doc_id,
                    "properties": {}
                }]
            }
            entities.append(cls_entity)
            
            # Method entities
            for method in cls["methods"]:
                method_id = f"{cls_id}_method_{method['name']}"
                method_entity = {
                    "id": method_id,
                    "type": "Method",
                    "properties": {
                        "name": method['name'],
                        "line_start": method['line_start'],
                        "has_docstring": bool(method.get('docstring'))
                    },
                    "relationships": [{
                        "type": "METHOD_OF",
                        "target_id": cls_id,
                        "properties": {}
                    }]
                }
                entities.append(method_entity)
        
        packets.append(NancyKnowledgePacket.create_graph_packet(entities, doc_id))
        
        return packets


async def test_simplified_analysis():
    """Test simplified codebase analysis."""
    print("Nancy Codebase MCP Server - Simplified Test")
    print("=" * 60)
    
    analyzer = SimplifiedCodebaseAnalyzer()
    
    # Test with this script itself
    test_file = __file__
    
    print(f"Analyzing file: {Path(test_file).name}")
    
    # Perform analysis
    analysis_result = analyzer.analyze_python_file(test_file)
    
    if "error" in analysis_result:
        print(f"ERROR: {analysis_result['error']}")
        return
    
    print(f"Analysis completed!")
    print(f"Language: {analysis_result['language']}")
    print(f"Lines: {analysis_result['total_lines']}")
    print(f"Functions: {len(analysis_result['functions'])}")
    print(f"Classes: {len(analysis_result['classes'])}")
    print(f"Imports: {len(analysis_result['imports'])}")
    print(f"Complexity Score: {analysis_result['complexity_score']}")
    
    # Generate Knowledge Packets
    print(f"\nGenerating Knowledge Packets...")
    knowledge_packets = analyzer.generate_knowledge_packets(analysis_result)
    
    print(f"Generated {len(knowledge_packets)} Knowledge Packets")
    
    # Analyze packet distribution
    packet_types = {}
    for packet in knowledge_packets:
        ptype = packet["type"]
        packet_types[ptype] = packet_types.get(ptype, 0) + 1
    
    print(f"\nPacket Distribution:")
    for ptype, count in packet_types.items():
        print(f"   {ptype}: {count}")
    
    # Show detailed examples
    print(f"\nVector Brain Packets:")
    vector_packets = [p for p in knowledge_packets if p["type"] == "vector_content"]
    for i, packet in enumerate(vector_packets[:3]):  # Show first 3
        metadata = packet["metadata"]
        content_preview = packet["content"][:100] + "..." if len(packet["content"]) > 100 else packet["content"]
        print(f"   {i+1}. {metadata['type']} - {len(packet['content'])} chars")
        print(f"      Preview: {content_preview}")
    
    print(f"\nAnalytical Brain Packet:")
    analytical_packets = [p for p in knowledge_packets if p["type"] == "analytical_data"]
    if analytical_packets:
        data = analytical_packets[0]["data"]
        print(f"   File: {data['file_name']}")
        print(f"   Functions: {data['function_count']}")
        print(f"   Classes: {data['class_count']}")
        print(f"   Complexity: {data['complexity_score']}")
    
    print(f"\nGraph Brain Packet:")
    graph_packets = [p for p in knowledge_packets if p["type"] == "graph_entities"]
    if graph_packets:
        entities = graph_packets[0]["entities"]
        entity_types = {}
        for entity in entities:
            etype = entity['type']
            entity_types[etype] = entity_types.get(etype, 0) + 1
        print(f"   Total entities: {len(entities)}")
        print(f"   Entity types: {dict(entity_types)}")
        
        # Show relationships
        total_relationships = sum(len(e.get('relationships', [])) for e in entities)
        print(f"   Total relationships: {total_relationships}")
    
    # Demonstrate MCP-style response format
    print(f"\nMCP Response Format:")
    mcp_response = {
        "jsonrpc": "2.0",
        "id": 1,
        "result": {
            "file_path": test_file,
            "doc_id": analyzer.generate_doc_id(test_file),
            "language": "python",
            "knowledge_packets": knowledge_packets,
            "analysis_summary": {
                "functions": len(analysis_result['functions']),
                "classes": len(analysis_result['classes']),
                "complexity_score": analysis_result['complexity_score'],
                "total_packets": len(knowledge_packets)
            }
        }
    }
    
    print(f"   Response size: {len(json.dumps(mcp_response))} characters")
    print(f"   Status: Ready for Nancy Core integration")
    
    print("\n" + "=" * 60)
    print("Simplified test completed successfully!")
    print("Core Knowledge Packet generation verified")
    print("Ready for full tree-sitter integration")
    
    return mcp_response


if __name__ == "__main__":
    asyncio.run(test_simplified_analysis())