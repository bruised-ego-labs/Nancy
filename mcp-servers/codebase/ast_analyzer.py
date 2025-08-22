#!/usr/bin/env python3
"""
AST Analysis Module for Nancy Codebase MCP Server
Provides comprehensive Abstract Syntax Tree parsing using tree-sitter and built-in AST modules.
Supports multiple programming languages with detailed code structure analysis.
"""

import ast
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from tree_sitter import Language, Parser, Node
import logging

logger = logging.getLogger(__name__)


class ASTAnalyzer:
    """
    Comprehensive AST analyzer supporting multiple programming languages.
    Extracted from Nancy's core ingestion service for standalone MCP operation.
    """
    
    def __init__(self):
        self.parsers = {}
        self.languages = {}
        self._initialize_tree_sitter()
        logger.info("ASTAnalyzer initialized with tree-sitter parsing capabilities")
    
    def _initialize_tree_sitter(self):
        """
        Initialize tree-sitter parsers for supported languages.
        """
        try:
            # Dictionary mapping file extensions to tree-sitter language names
            self.language_map = {
                '.py': 'python',
                '.js': 'javascript', 
                '.ts': 'javascript',  # TypeScript uses JavaScript parser
                '.tsx': 'javascript',
                '.jsx': 'javascript',
                '.c': 'c',
                '.cpp': 'cpp',
                '.cc': 'cpp',
                '.cxx': 'cpp',
                '.h': 'c',
                '.hpp': 'cpp',
                '.java': 'java',
                '.go': 'go',
                '.rs': 'rust',
                '.php': 'php',
                '.rb': 'ruby'
            }
            
            # Try to load available language parsers
            for ext, lang_name in self.language_map.items():
                try:
                    # Import the specific tree-sitter language module
                    if lang_name == 'python':
                        try:
                            import tree_sitter_python as ts_python
                            language = Language(ts_python.language(), lang_name)
                        except ImportError:
                            continue
                    elif lang_name == 'javascript':
                        try:
                            import tree_sitter_javascript as ts_javascript
                            language = Language(ts_javascript.language(), lang_name)
                        except ImportError:
                            continue
                    elif lang_name == 'c':
                        try:
                            import tree_sitter_c as ts_c
                            language = Language(ts_c.language(), lang_name)
                        except ImportError:
                            continue
                    elif lang_name == 'cpp':
                        try:
                            import tree_sitter_cpp as ts_cpp
                            language = Language(ts_cpp.language(), lang_name)
                        except ImportError:
                            continue
                    elif lang_name == 'java':
                        try:
                            import tree_sitter_java as ts_java
                            language = Language(ts_java.language(), lang_name)
                        except ImportError:
                            continue
                    elif lang_name == 'go':
                        try:
                            import tree_sitter_go as ts_go
                            language = Language(ts_go.language(), lang_name)
                        except ImportError:
                            continue
                    elif lang_name == 'rust':
                        try:
                            import tree_sitter_rust as ts_rust
                            language = Language(ts_rust.language(), lang_name)
                        except ImportError:
                            continue
                    else:
                        continue
                    
                    parser = Parser()
                    parser.set_language(language)
                    
                    self.languages[lang_name] = language
                    self.parsers[ext] = parser
                    
                except ImportError as import_error:
                    logger.debug(f"Tree-sitter {lang_name} parser not available: {import_error}")
                except Exception as parser_error:
                    logger.warning(f"Failed to initialize {lang_name} parser: {parser_error}")
            
            logger.info(f"Initialized tree-sitter parsers for: {list(self.parsers.keys())}")
            
        except Exception as e:
            logger.error(f"Error initializing tree-sitter: {e}")
    
    def _get_parser_for_file(self, file_path: str) -> Optional[Parser]:
        """
        Get the appropriate tree-sitter parser for a file.
        """
        file_ext = Path(file_path).suffix.lower()
        return self.parsers.get(file_ext)
    
    def analyze_python_ast(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Python code using both built-in AST module and tree-sitter.
        Enhanced extraction of functions, classes, imports, and relationships.
        """
        try:
            # Parse with Python's built-in AST module
            tree = ast.parse(content)
            
            functions = []
            classes = []
            imports = []
            variables = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Extract function information
                    func_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "args": [arg.arg for arg in node.args.args],
                        "returns": ast.unparse(node.returns) if node.returns else None,
                        "docstring": ast.get_docstring(node),
                        "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                        "is_async": isinstance(node, ast.AsyncFunctionDef),
                        "complexity": self._calculate_complexity(node)
                    }
                    functions.append(func_info)
                
                elif isinstance(node, ast.ClassDef):
                    # Extract class information
                    class_info = {
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                        "bases": [ast.unparse(base) for base in node.bases],
                        "decorators": [ast.unparse(dec) for dec in node.decorator_list],
                        "docstring": ast.get_docstring(node),
                        "methods": [],
                        "properties": []
                    }
                    
                    # Extract methods and properties within the class
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                "name": item.name,
                                "line_start": item.lineno,
                                "args": [arg.arg for arg in item.args.args],
                                "docstring": ast.get_docstring(item),
                                "is_property": any(ast.unparse(dec) == 'property' for dec in item.decorator_list),
                                "is_static": any(ast.unparse(dec) == 'staticmethod' for dec in item.decorator_list),
                                "is_class_method": any(ast.unparse(dec) == 'classmethod' for dec in item.decorator_list)
                            }
                            if method_info["is_property"]:
                                class_info["properties"].append(method_info)
                            else:
                                class_info["methods"].append(method_info)
                    
                    classes.append(class_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Extract import information
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({
                                "type": "import",
                                "module": alias.name,
                                "alias": alias.asname,
                                "line": node.lineno
                            })
                    else:  # ImportFrom
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
                "functions": functions,
                "classes": classes,
                "imports": imports,
                "variables": variables,
                "total_lines": len(content.split('\n')),
                "complexity_score": sum(func.get('complexity', 1) for func in functions)
            }
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error in {file_path}: {e}")
            return {"error": f"Syntax error: {e}", "language": "python"}
        except Exception as e:
            logger.error(f"Python AST analysis failed for {file_path}: {e}")
            return {"error": f"Analysis failed: {e}", "language": "python"}
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a function.
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor,
                                ast.ExceptHandler, ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity
    
    def analyze_tree_sitter_ast(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze code using tree-sitter for general language support.
        """
        parser = self._get_parser_for_file(file_path)
        if not parser:
            return {"error": "No parser available for this file type"}
        
        try:
            tree = parser.parse(bytes(content, 'utf8'))
            root_node = tree.root_node
            
            # Get file extension to determine language-specific analysis
            file_ext = Path(file_path).suffix.lower()
            lang_name = self.language_map.get(file_ext, 'unknown')
            
            # Route to language-specific analysis
            if lang_name == 'javascript':
                return self._analyze_javascript_tree(root_node, content, file_path)
            elif lang_name in ['c', 'cpp']:
                return self._analyze_c_cpp_tree(root_node, content, file_path)
            elif lang_name == 'java':
                return self._analyze_java_tree(root_node, content, file_path)
            elif lang_name == 'go':
                return self._analyze_go_tree(root_node, content, file_path)
            else:
                return self._analyze_generic_tree(root_node, content, file_path, lang_name)
            
        except Exception as e:
            logger.error(f"Tree-sitter analysis failed for {file_path}: {e}")
            return {"error": f"Tree-sitter analysis failed: {e}"}
    
    def _analyze_javascript_tree(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze JavaScript/TypeScript AST with enhanced relationship extraction.
        """
        functions = []
        classes = []
        imports = []
        exports = []
        variables = []
        
        def traverse_node(node):
            if node.type == "function_declaration":
                func_name = None
                for child in node.children:
                    if child.type == "identifier":
                        func_name = content[child.start_byte:child.end_byte]
                        break
                
                if func_name:
                    functions.append({
                        "name": func_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "function_declaration",
                        "is_async": "async" in content[node.start_byte:node.end_byte]
                    })
            
            elif node.type == "arrow_function":
                functions.append({
                    "name": "anonymous_arrow",
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "type": "arrow_function",
                    "is_async": "async" in content[node.start_byte:node.end_byte]
                })
            
            elif node.type == "class_declaration":
                class_name = None
                for child in node.children:
                    if child.type == "identifier":
                        class_name = content[child.start_byte:child.end_byte]
                        break
                
                if class_name:
                    classes.append({
                        "name": class_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "methods": []
                    })
            
            elif node.type == "import_statement":
                imports.append({
                    "line": node.start_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            elif node.type == "export_statement":
                exports.append({
                    "line": node.start_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "language": "javascript",
            "functions": functions,
            "classes": classes,
            "imports": imports,
            "exports": exports,
            "variables": variables,
            "total_lines": len(content.split('\n'))
        }
    
    def _analyze_c_cpp_tree(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze C/C++ AST with system-level relationship extraction.
        """
        functions = []
        structures = []
        includes = []
        macros = []
        
        def traverse_node(node):
            if node.type == "function_definition":
                func_name = None
                for child in node.children:
                    if child.type == "function_declarator":
                        for grandchild in child.children:
                            if grandchild.type == "identifier":
                                func_name = content[grandchild.start_byte:grandchild.end_byte]
                                break
                        break
                
                if func_name:
                    functions.append({
                        "name": func_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "function_definition"
                    })
            
            elif node.type in ["struct_specifier", "class_specifier"]:
                struct_name = None
                for child in node.children:
                    if child.type == "type_identifier":
                        struct_name = content[child.start_byte:child.end_byte]
                        break
                
                if struct_name:
                    structures.append({
                        "name": struct_name,
                        "type": node.type,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1
                    })
            
            elif node.type == "preproc_include":
                includes.append({
                    "line": node.start_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            elif node.type == "preproc_def":
                macros.append({
                    "line": node.start_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "language": "c/cpp",
            "functions": functions,
            "structures": structures,
            "includes": includes,
            "macros": macros,
            "total_lines": len(content.split('\n'))
        }
    
    def _analyze_java_tree(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Java AST with object-oriented relationship extraction.
        """
        classes = []
        methods = []
        imports = []
        interfaces = []
        
        def traverse_node(node):
            if node.type == "class_declaration":
                class_name = None
                for child in node.children:
                    if child.type == "identifier":
                        class_name = content[child.start_byte:child.end_byte]
                        break
                
                if class_name:
                    classes.append({
                        "name": class_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "class"
                    })
            
            elif node.type == "interface_declaration":
                interface_name = None
                for child in node.children:
                    if child.type == "identifier":
                        interface_name = content[child.start_byte:child.end_byte]
                        break
                
                if interface_name:
                    interfaces.append({
                        "name": interface_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "interface"
                    })
            
            elif node.type == "method_declaration":
                method_name = None
                for child in node.children:
                    if child.type == "identifier":
                        method_name = content[child.start_byte:child.end_byte]
                        break
                
                if method_name:
                    methods.append({
                        "name": method_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "method"
                    })
            
            elif node.type == "import_declaration":
                imports.append({
                    "line": node.start_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "language": "java",
            "classes": classes,
            "methods": methods,
            "interfaces": interfaces,
            "imports": imports,
            "total_lines": len(content.split('\n'))
        }
    
    def _analyze_go_tree(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze Go AST with package and interface analysis.
        """
        functions = []
        types = []
        imports = []
        interfaces = []
        
        def traverse_node(node):
            if node.type == "function_declaration":
                func_name = None
                for child in node.children:
                    if child.type == "identifier":
                        func_name = content[child.start_byte:child.end_byte]
                        break
                
                if func_name:
                    functions.append({
                        "name": func_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "function"
                    })
            
            elif node.type == "type_declaration":
                types.append({
                    "line_start": node.start_point[0] + 1,
                    "line_end": node.end_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            elif node.type == "import_declaration":
                imports.append({
                    "line": node.start_point[0] + 1,
                    "content": content[node.start_byte:node.end_byte]
                })
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "language": "go",
            "functions": functions,
            "types": types,
            "imports": imports,
            "interfaces": interfaces,
            "total_lines": len(content.split('\n'))
        }
    
    def _analyze_generic_tree(self, root_node: Node, content: str, file_path: str, language: str) -> Dict[str, Any]:
        """
        Generic tree analysis for languages without specific handlers.
        """
        node_types = {}
        
        def traverse_node(node):
            node_type = node.type
            if node_type not in node_types:
                node_types[node_type] = 0
            node_types[node_type] += 1
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "language": language,
            "node_types": node_types,
            "total_lines": len(content.split('\n')),
            "analysis_type": "generic"
        }
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of a single code file.
        Routes to appropriate analyzer based on file extension and language.
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
            
            file_ext = Path(file_path).suffix.lower()
            
            # Route to appropriate analyzer
            if file_ext == '.py':
                ast_result = self.analyze_python_ast(content, file_path)
            else:
                ast_result = self.analyze_tree_sitter_ast(content, file_path)
            
            # Add common file metadata
            ast_result.update({
                "file_path": file_path,
                "file_extension": file_ext,
                "file_size": len(content),
                "line_count": len(content.split('\n')),
                "char_count": len(content)
            })
            
            return ast_result
            
        except Exception as e:
            logger.error(f"Code file analysis failed for {file_path}: {e}")
            return {"error": f"Analysis failed: {e}"}
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.
        """
        return list(self.language_map.keys())
    
    def is_supported_file(self, file_path: str) -> bool:
        """
        Check if file type is supported for analysis.
        """
        file_ext = Path(file_path).suffix.lower()
        return file_ext in self.language_map