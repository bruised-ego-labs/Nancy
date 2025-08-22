#!/usr/bin/env python3
"""
Python Language Processor for Nancy Codebase MCP Server
Enhanced Python-specific analysis including import dependencies, decorator analysis,
and advanced code patterns recognition.
"""

import ast
import re
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PythonProcessor:
    """
    Enhanced Python code processor with advanced AST analysis and pattern recognition.
    """
    
    def __init__(self):
        self.import_patterns = {}
        self.decorator_registry = set()
        logger.debug("PythonProcessor initialized")
    
    def analyze_imports(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze Python imports with dependency mapping and categorization.
        """
        imports = {
            "standard_library": [],
            "third_party": [],
            "local": [],
            "relative": [],
            "import_graph": {}
        }
        
        # Common standard library modules (partial list)
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'collections', 'itertools',
            'functools', 're', 'math', 'random', 'pathlib', 'typing',
            'asyncio', 'concurrent', 'multiprocessing', 'threading',
            'logging', 'unittest', 'pytest', 'sqlite3', 'urllib',
            'http', 'email', 'xml', 'csv', 'configparser'
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]
                    import_info = {
                        "module": alias.name,
                        "alias": alias.asname,
                        "line": node.lineno,
                        "type": "import"
                    }
                    
                    # Categorize import
                    if module_name in stdlib_modules:
                        imports["standard_library"].append(import_info)
                    elif module_name.startswith('.'):
                        imports["relative"].append(import_info)
                    elif '.' not in alias.name and module_name.islower():
                        imports["local"].append(import_info)
                    else:
                        imports["third_party"].append(import_info)
                        
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_name = node.module.split('.')[0]
                    for alias in node.names:
                        import_info = {
                            "module": node.module,
                            "name": alias.name,
                            "alias": alias.asname,
                            "line": node.lineno,
                            "type": "from_import",
                            "level": node.level
                        }
                        
                        # Categorize import
                        if node.level > 0:  # Relative import
                            imports["relative"].append(import_info)
                        elif module_name in stdlib_modules:
                            imports["standard_library"].append(import_info)
                        elif module_name.islower() and '.' not in node.module:
                            imports["local"].append(import_info)
                        else:
                            imports["third_party"].append(import_info)
        
        return imports
    
    def analyze_decorators(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze Python decorators and their usage patterns.
        """
        decorators = {
            "function_decorators": [],
            "class_decorators": [],
            "decorator_usage": {},
            "custom_decorators": []
        }
        
        common_decorators = {
            'property', 'staticmethod', 'classmethod', 'dataclass',
            'lru_cache', 'cached_property', 'abstractmethod', 'override',
            'pytest.fixture', 'click.command', 'route', 'app.route'
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.decorator_list:
                for decorator in node.decorator_list:
                    dec_name = ast.unparse(decorator)
                    decorators["function_decorators"].append({
                        "function": node.name,
                        "decorator": dec_name,
                        "line": decorator.lineno,
                        "is_common": dec_name in common_decorators
                    })
                    
                    # Track usage count
                    decorators["decorator_usage"][dec_name] = decorators["decorator_usage"].get(dec_name, 0) + 1
                    
            elif isinstance(node, ast.ClassDef) and node.decorator_list:
                for decorator in node.decorator_list:
                    dec_name = ast.unparse(decorator)
                    decorators["class_decorators"].append({
                        "class": node.name,
                        "decorator": dec_name,
                        "line": decorator.lineno,
                        "is_common": dec_name in common_decorators
                    })
                    
                    decorators["decorator_usage"][dec_name] = decorators["decorator_usage"].get(dec_name, 0) + 1
        
        # Identify custom decorators (not in common list)
        for dec_name, count in decorators["decorator_usage"].items():
            if dec_name not in common_decorators and not dec_name.startswith('pytest.'):
                decorators["custom_decorators"].append({
                    "name": dec_name,
                    "usage_count": count
                })
        
        return decorators
    
    def analyze_exception_handling(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze exception handling patterns in Python code.
        """
        exceptions = {
            "try_blocks": [],
            "exception_types": {},
            "bare_except": 0,
            "finally_blocks": 0,
            "custom_exceptions": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                try_info = {
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "handlers": [],
                    "has_finally": bool(node.finalbody),
                    "has_else": bool(node.orelse)
                }
                
                for handler in node.handlers:
                    if handler.type:
                        exc_type = ast.unparse(handler.type)
                        exceptions["exception_types"][exc_type] = exceptions["exception_types"].get(exc_type, 0) + 1
                        try_info["handlers"].append({
                            "exception_type": exc_type,
                            "variable": handler.name,
                            "line": handler.lineno
                        })
                    else:
                        exceptions["bare_except"] += 1
                        try_info["handlers"].append({
                            "exception_type": "bare_except",
                            "variable": handler.name,
                            "line": handler.lineno
                        })
                
                if node.finalbody:
                    exceptions["finally_blocks"] += 1
                
                exceptions["try_blocks"].append(try_info)
            
            elif isinstance(node, ast.ClassDef):
                # Check if class inherits from Exception
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == 'Exception':
                        exceptions["custom_exceptions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node)
                        })
                    elif isinstance(base, ast.Attribute) and 'Exception' in ast.unparse(base):
                        exceptions["custom_exceptions"].append({
                            "name": node.name,
                            "line": node.lineno,
                            "docstring": ast.get_docstring(node)
                        })
        
        return exceptions
    
    def analyze_async_patterns(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze async/await patterns in Python code.
        """
        async_patterns = {
            "async_functions": [],
            "await_expressions": [],
            "async_context_managers": [],
            "async_iterators": [],
            "concurrent_patterns": []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.AsyncFunctionDef):
                async_patterns["async_functions"].append({
                    "name": node.name,
                    "line_start": node.lineno,
                    "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
                    "args": [arg.arg for arg in node.args.args],
                    "docstring": ast.get_docstring(node),
                    "decorators": [ast.unparse(dec) for dec in node.decorator_list]
                })
                
            elif isinstance(node, ast.Await):
                async_patterns["await_expressions"].append({
                    "line": node.lineno,
                    "expression": ast.unparse(node.value)
                })
                
            elif isinstance(node, ast.AsyncWith):
                async_patterns["async_context_managers"].append({
                    "line": node.lineno,
                    "context_expr": [ast.unparse(item.context_expr) for item in node.items]
                })
                
            elif isinstance(node, ast.AsyncFor):
                async_patterns["async_iterators"].append({
                    "line": node.lineno,
                    "target": ast.unparse(node.target),
                    "iter": ast.unparse(node.iter)
                })
        
        return async_patterns
    
    def analyze_comprehensions(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze list, dict, and set comprehensions.
        """
        comprehensions = {
            "list_comprehensions": [],
            "dict_comprehensions": [],
            "set_comprehensions": [],
            "generator_expressions": [],
            "complexity_scores": {}
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ListComp):
                comp_info = {
                    "line": node.lineno,
                    "element": ast.unparse(node.elt),
                    "generators": len(node.generators),
                    "conditions": sum(len(gen.ifs) for gen in node.generators)
                }
                comprehensions["list_comprehensions"].append(comp_info)
                
            elif isinstance(node, ast.DictComp):
                comp_info = {
                    "line": node.lineno,
                    "key": ast.unparse(node.key),
                    "value": ast.unparse(node.value),
                    "generators": len(node.generators),
                    "conditions": sum(len(gen.ifs) for gen in node.generators)
                }
                comprehensions["dict_comprehensions"].append(comp_info)
                
            elif isinstance(node, ast.SetComp):
                comp_info = {
                    "line": node.lineno,
                    "element": ast.unparse(node.elt),
                    "generators": len(node.generators),
                    "conditions": sum(len(gen.ifs) for gen in node.generators)
                }
                comprehensions["set_comprehensions"].append(comp_info)
                
            elif isinstance(node, ast.GeneratorExp):
                comp_info = {
                    "line": node.lineno,
                    "element": ast.unparse(node.elt),
                    "generators": len(node.generators),
                    "conditions": sum(len(gen.ifs) for gen in node.generators)
                }
                comprehensions["generator_expressions"].append(comp_info)
        
        # Calculate complexity scores
        for comp_type, comps in comprehensions.items():
            if comp_type != "complexity_scores" and comps:
                avg_generators = sum(c.get("generators", 0) for c in comps) / len(comps)
                avg_conditions = sum(c.get("conditions", 0) for c in comps) / len(comps)
                comprehensions["complexity_scores"][comp_type] = {
                    "count": len(comps),
                    "avg_generators": round(avg_generators, 2),
                    "avg_conditions": round(avg_conditions, 2)
                }
        
        return comprehensions
    
    def analyze_type_hints(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Analyze Python type hints usage.
        """
        type_hints = {
            "function_annotations": [],
            "variable_annotations": [],
            "type_imports": [],
            "generic_types": [],
            "coverage_score": 0.0
        }
        
        total_functions = 0
        annotated_functions = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                total_functions += 1
                func_hints = {
                    "name": node.name,
                    "line": node.lineno,
                    "return_annotation": ast.unparse(node.returns) if node.returns else None,
                    "arg_annotations": []
                }
                
                has_annotations = bool(node.returns)
                
                for arg in node.args.args:
                    if arg.annotation:
                        has_annotations = True
                        func_hints["arg_annotations"].append({
                            "arg": arg.arg,
                            "annotation": ast.unparse(arg.annotation)
                        })
                    else:
                        func_hints["arg_annotations"].append({
                            "arg": arg.arg,
                            "annotation": None
                        })
                
                if has_annotations:
                    annotated_functions += 1
                
                type_hints["function_annotations"].append(func_hints)
                
            elif isinstance(node, ast.AnnAssign):
                type_hints["variable_annotations"].append({
                    "target": ast.unparse(node.target),
                    "annotation": ast.unparse(node.annotation),
                    "line": node.lineno
                })
        
        # Calculate coverage score
        if total_functions > 0:
            type_hints["coverage_score"] = round((annotated_functions / total_functions) * 100, 2)
        
        return type_hints
    
    def enhanced_analyze(self, content: str, file_path: str) -> Dict[str, Any]:
        """
        Perform enhanced Python analysis combining all processors.
        """
        try:
            tree = ast.parse(content)
            
            # Base AST analysis
            base_analysis = self._basic_ast_analysis(tree)
            
            # Enhanced analyses
            imports = self.analyze_imports(tree)
            decorators = self.analyze_decorators(tree)
            exceptions = self.analyze_exception_handling(tree)
            async_patterns = self.analyze_async_patterns(tree)
            comprehensions = self.analyze_comprehensions(tree)
            type_hints = self.analyze_type_hints(tree)
            
            # Combine results
            enhanced_result = {
                **base_analysis,
                "imports": imports,
                "decorators": decorators,
                "exception_handling": exceptions,
                "async_patterns": async_patterns,
                "comprehensions": comprehensions,
                "type_hints": type_hints,
                "code_quality_metrics": self._calculate_quality_metrics(
                    base_analysis, imports, decorators, exceptions, type_hints
                )
            }
            
            return enhanced_result
            
        except SyntaxError as e:
            logger.warning(f"Python syntax error in {file_path}: {e}")
            return {"error": f"Syntax error: {e}", "language": "python"}
        except Exception as e:
            logger.error(f"Enhanced Python analysis failed for {file_path}: {e}")
            return {"error": f"Analysis failed: {e}", "language": "python"}
    
    def _basic_ast_analysis(self, tree: ast.AST) -> Dict[str, Any]:
        """
        Basic AST analysis (similar to original implementation).
        """
        functions = []
        classes = []
        variables = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
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
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            "name": item.name,
                            "line_start": item.lineno,
                            "args": [arg.arg for arg in item.args.args],
                            "docstring": ast.get_docstring(item),
                            "is_property": any('property' in ast.unparse(dec) for dec in item.decorator_list),
                            "is_static": any('staticmethod' in ast.unparse(dec) for dec in item.decorator_list),
                            "is_class_method": any('classmethod' in ast.unparse(dec) for dec in item.decorator_list)
                        }
                        if method_info["is_property"]:
                            class_info["properties"].append(method_info)
                        else:
                            class_info["methods"].append(method_info)
                
                classes.append(class_info)
        
        return {
            "language": "python",
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "total_lines": len(content.split('\n')) if 'content' in locals() else 0,
            "complexity_score": sum(func.get('complexity', 1) for func in functions)
        }
    
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
    
    def _calculate_quality_metrics(self, base_analysis: Dict[str, Any], 
                                 imports: Dict[str, Any], decorators: Dict[str, Any],
                                 exceptions: Dict[str, Any], type_hints: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate code quality metrics."""
        return {
            "type_hint_coverage": type_hints.get("coverage_score", 0),
            "docstring_coverage": self._calculate_docstring_coverage(base_analysis),
            "exception_handling_score": self._calculate_exception_score(exceptions),
            "import_organization": self._calculate_import_score(imports),
            "async_usage": len(base_analysis.get("functions", [])) > 0 and any(
                f.get("is_async", False) for f in base_analysis.get("functions", [])
            ),
            "decorator_usage": len(decorators.get("decorator_usage", {})),
            "overall_score": 0.0  # To be calculated
        }
    
    def _calculate_docstring_coverage(self, base_analysis: Dict[str, Any]) -> float:
        """Calculate docstring coverage percentage."""
        total_items = len(base_analysis.get("functions", [])) + len(base_analysis.get("classes", []))
        if total_items == 0:
            return 100.0
        
        documented_items = 0
        for func in base_analysis.get("functions", []):
            if func.get("docstring"):
                documented_items += 1
        
        for cls in base_analysis.get("classes", []):
            if cls.get("docstring"):
                documented_items += 1
        
        return round((documented_items / total_items) * 100, 2)
    
    def _calculate_exception_score(self, exceptions: Dict[str, Any]) -> float:
        """Calculate exception handling score."""
        total_handlers = len(exceptions.get("try_blocks", []))
        if total_handlers == 0:
            return 100.0
        
        bare_except_penalty = exceptions.get("bare_except", 0) * 0.5
        score = max(0, 100 - bare_except_penalty)
        return round(score, 2)
    
    def _calculate_import_score(self, imports: Dict[str, Any]) -> float:
        """Calculate import organization score."""
        total_imports = (
            len(imports.get("standard_library", [])) +
            len(imports.get("third_party", [])) +
            len(imports.get("local", [])) +
            len(imports.get("relative", []))
        )
        
        if total_imports == 0:
            return 100.0
        
        # Prefer organized imports (stdlib -> third-party -> local)
        organized_score = 100.0
        if len(imports.get("relative", [])) > total_imports * 0.5:
            organized_score -= 20  # Too many relative imports
        
        return round(organized_score, 2)