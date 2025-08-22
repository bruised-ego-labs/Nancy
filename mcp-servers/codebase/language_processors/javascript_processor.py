#!/usr/bin/env python3
"""
JavaScript/TypeScript Language Processor for Nancy Codebase MCP Server
Enhanced JavaScript and TypeScript analysis including module dependencies,
React patterns, and modern JS feature detection.
"""

from tree_sitter import Node
from typing import Dict, Any, List, Optional, Set
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


class JavaScriptProcessor:
    """
    Enhanced JavaScript/TypeScript processor with modern JS patterns and React support.
    """
    
    def __init__(self):
        self.module_patterns = {}
        self.react_patterns = {}
        logger.debug("JavaScriptProcessor initialized")
    
    def analyze_modules(self, root_node: Node, content: str) -> Dict[str, Any]:
        """
        Analyze ES6+ module imports and exports with dependency mapping.
        """
        modules = {
            "imports": {
                "es6_imports": [],
                "commonjs_require": [],
                "dynamic_imports": [],
                "type_only_imports": []
            },
            "exports": {
                "named_exports": [],
                "default_exports": [],
                "re_exports": []
            },
            "dependency_graph": {},
            "module_type": "unknown"
        }
        
        def traverse_for_modules(node):
            if node.type == "import_statement":
                import_info = self._parse_import_statement(node, content)
                if import_info["import_type"] == "type_only":
                    modules["imports"]["type_only_imports"].append(import_info)
                else:
                    modules["imports"]["es6_imports"].append(import_info)
                    
            elif node.type == "call_expression":
                # Check for require() calls
                if self._is_require_call(node, content):
                    require_info = self._parse_require_call(node, content)
                    modules["imports"]["commonjs_require"].append(require_info)
                elif self._is_dynamic_import(node, content):
                    dynamic_info = self._parse_dynamic_import(node, content)
                    modules["imports"]["dynamic_imports"].append(dynamic_info)
                    
            elif node.type == "export_statement":
                export_info = self._parse_export_statement(node, content)
                if export_info["export_type"] == "default":
                    modules["exports"]["default_exports"].append(export_info)
                elif export_info["export_type"] == "re_export":
                    modules["exports"]["re_exports"].append(export_info)
                else:
                    modules["exports"]["named_exports"].append(export_info)
            
            for child in node.children:
                traverse_for_modules(child)
        
        traverse_for_modules(root_node)
        
        # Determine module type
        has_es6_syntax = (
            len(modules["imports"]["es6_imports"]) > 0 or
            len(modules["exports"]["named_exports"]) > 0 or
            len(modules["exports"]["default_exports"]) > 0
        )
        has_commonjs = len(modules["imports"]["commonjs_require"]) > 0
        
        if has_es6_syntax and not has_commonjs:
            modules["module_type"] = "es6"
        elif has_commonjs and not has_es6_syntax:
            modules["module_type"] = "commonjs"
        elif has_es6_syntax and has_commonjs:
            modules["module_type"] = "mixed"
        
        return modules
    
    def analyze_react_patterns(self, root_node: Node, content: str) -> Dict[str, Any]:
        """
        Analyze React-specific patterns including components, hooks, and JSX.
        """
        react = {
            "components": {
                "function_components": [],
                "class_components": [],
                "arrow_function_components": []
            },
            "hooks": {
                "built_in_hooks": [],
                "custom_hooks": []
            },
            "jsx_elements": [],
            "props_usage": [],
            "state_management": [],
            "is_react_file": False
        }
        
        # Check if file uses React
        react_imports = self._find_react_imports(root_node, content)
        react["is_react_file"] = len(react_imports) > 0
        
        if not react["is_react_file"]:
            return react
        
        def traverse_for_react(node):
            # Function components
            if node.type == "function_declaration":
                if self._is_react_component(node, content):
                    comp_info = self._parse_react_component(node, content, "function")
                    react["components"]["function_components"].append(comp_info)
            
            # Class components
            elif node.type == "class_declaration":
                if self._extends_react_component(node, content):
                    comp_info = self._parse_react_component(node, content, "class")
                    react["components"]["class_components"].append(comp_info)
            
            # Arrow function components
            elif node.type == "variable_declarator":
                if self._is_arrow_component(node, content):
                    comp_info = self._parse_react_component(node, content, "arrow")
                    react["components"]["arrow_function_components"].append(comp_info)
            
            # Hook usage
            elif node.type == "call_expression":
                hook_info = self._analyze_hook_call(node, content)
                if hook_info:
                    if hook_info["is_built_in"]:
                        react["hooks"]["built_in_hooks"].append(hook_info)
                    else:
                        react["hooks"]["custom_hooks"].append(hook_info)
            
            # JSX elements
            elif node.type == "jsx_element":
                jsx_info = self._parse_jsx_element(node, content)
                react["jsx_elements"].append(jsx_info)
            
            for child in node.children:
                traverse_for_react(child)
        
        traverse_for_react(root_node)
        return react
    
    def analyze_modern_js_features(self, root_node: Node, content: str) -> Dict[str, Any]:
        """
        Analyze modern JavaScript features usage.
        """
        features = {
            "es6_features": {
                "arrow_functions": [],
                "template_literals": [],
                "destructuring": [],
                "spread_operator": [],
                "default_parameters": [],
                "rest_parameters": []
            },
            "async_patterns": {
                "async_functions": [],
                "await_expressions": [],
                "promises": []
            },
            "classes": {
                "class_declarations": [],
                "method_definitions": [],
                "getters_setters": []
            },
            "feature_usage_score": 0.0
        }
        
        def traverse_for_features(node):
            # Arrow functions
            if node.type == "arrow_function":
                features["es6_features"]["arrow_functions"].append({
                    "line": node.start_point[0] + 1,
                    "is_async": "async" in content[node.start_byte:node.end_byte]
                })
            
            # Template literals
            elif node.type == "template_string":
                features["es6_features"]["template_literals"].append({
                    "line": node.start_point[0] + 1,
                    "has_expressions": "${" in content[node.start_byte:node.end_byte]
                })
            
            # Destructuring
            elif node.type in ["object_pattern", "array_pattern"]:
                features["es6_features"]["destructuring"].append({
                    "line": node.start_point[0] + 1,
                    "type": "object" if node.type == "object_pattern" else "array"
                })
            
            # Spread operator
            elif node.type == "spread_element":
                features["es6_features"]["spread_operator"].append({
                    "line": node.start_point[0] + 1,
                    "context": "spread"
                })
            
            # Async functions
            elif node.type == "function_declaration" and "async" in content[node.start_byte:node.end_byte]:
                func_name = self._get_function_name(node, content)
                features["async_patterns"]["async_functions"].append({
                    "name": func_name,
                    "line": node.start_point[0] + 1
                })
            
            # Await expressions
            elif node.type == "await_expression":
                features["async_patterns"]["await_expressions"].append({
                    "line": node.start_point[0] + 1,
                    "expression": content[node.start_byte:node.end_byte]
                })
            
            # Classes
            elif node.type == "class_declaration":
                class_name = self._get_class_name(node, content)
                features["classes"]["class_declarations"].append({
                    "name": class_name,
                    "line": node.start_point[0] + 1,
                    "extends": self._get_class_extends(node, content)
                })
            
            for child in node.children:
                traverse_for_features(child)
        
        traverse_for_features(root_node)
        
        # Calculate feature usage score
        total_features = sum(len(category) for category in features["es6_features"].values())
        total_features += sum(len(category) for category in features["async_patterns"].values())
        
        if total_features > 0:
            features["feature_usage_score"] = min(100.0, total_features * 5)
        
        return features
    
    def analyze_typescript_features(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Analyze TypeScript-specific features if applicable.
        """
        is_typescript = Path(file_path).suffix.lower() in ['.ts', '.tsx']
        
        features = {
            "is_typescript": is_typescript,
            "interfaces": [],
            "types": [],
            "enums": [],
            "generics": [],
            "decorators": [],
            "type_annotations": [],
            "type_coverage_score": 0.0
        }
        
        if not is_typescript:
            return features
        
        def traverse_for_ts(node):
            # Interfaces
            if node.type == "interface_declaration":
                interface_info = self._parse_interface(node, content)
                features["interfaces"].append(interface_info)
            
            # Type aliases
            elif node.type == "type_alias_declaration":
                type_info = self._parse_type_alias(node, content)
                features["types"].append(type_info)
            
            # Enums
            elif node.type == "enum_declaration":
                enum_info = self._parse_enum(node, content)
                features["enums"].append(enum_info)
            
            # Decorators
            elif node.type == "decorator":
                decorator_info = self._parse_decorator(node, content)
                features["decorators"].append(decorator_info)
            
            for child in node.children:
                traverse_for_ts(child)
        
        traverse_for_ts(root_node)
        return features
    
    def enhanced_analyze(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """
        Perform enhanced JavaScript/TypeScript analysis.
        """
        try:
            # Base analysis
            base_result = self._basic_js_analysis(root_node, content, file_path)
            
            # Enhanced analyses
            modules = self.analyze_modules(root_node, content)
            react = self.analyze_react_patterns(root_node, content)
            modern_features = self.analyze_modern_js_features(root_node, content)
            typescript = self.analyze_typescript_features(root_node, content, file_path)
            
            # Combine results
            enhanced_result = {
                **base_result,
                "modules": modules,
                "react_patterns": react,
                "modern_js_features": modern_features,
                "typescript_features": typescript,
                "code_quality_metrics": self._calculate_js_quality_metrics(
                    base_result, modules, react, modern_features, typescript
                )
            }
            
            return enhanced_result
            
        except Exception as e:
            logger.error(f"Enhanced JavaScript analysis failed for {file_path}: {e}")
            return {"error": f"Analysis failed: {e}", "language": "javascript"}
    
    # Helper methods for parsing specific constructs
    def _parse_import_statement(self, node: Node, content: str) -> Dict[str, Any]:
        """Parse ES6 import statement."""
        import_text = content[node.start_byte:node.end_byte]
        
        # Basic import parsing - would need more sophisticated logic for full support
        return {
            "line": node.start_point[0] + 1,
            "statement": import_text,
            "import_type": "type_only" if "type" in import_text else "value",
            "source": self._extract_import_source(import_text)
        }
    
    def _extract_import_source(self, import_text: str) -> str:
        """Extract source module from import statement."""
        # Simple regex to extract from/source
        match = re.search(r"from\s+['\"]([^'\"]+)['\"]", import_text)
        if match:
            return match.group(1)
        return "unknown"
    
    def _is_require_call(self, node: Node, content: str) -> bool:
        """Check if node is a require() call."""
        call_text = content[node.start_byte:node.end_byte]
        return "require(" in call_text
    
    def _is_dynamic_import(self, node: Node, content: str) -> bool:
        """Check if node is a dynamic import() call."""
        call_text = content[node.start_byte:node.end_byte]
        return "import(" in call_text
    
    def _basic_js_analysis(self, root_node: Node, content: str, file_path: str) -> Dict[str, Any]:
        """Basic JavaScript analysis (similar to original implementation)."""
        functions = []
        classes = []
        variables = []
        
        def traverse_node(node):
            if node.type == "function_declaration":
                func_name = self._get_function_name(node, content)
                if func_name:
                    functions.append({
                        "name": func_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "type": "function_declaration",
                        "is_async": "async" in content[node.start_byte:node.end_byte]
                    })
            
            elif node.type == "class_declaration":
                class_name = self._get_class_name(node, content)
                if class_name:
                    classes.append({
                        "name": class_name,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "methods": []
                    })
            
            for child in node.children:
                traverse_node(child)
        
        traverse_node(root_node)
        
        return {
            "language": "javascript",
            "functions": functions,
            "classes": classes,
            "variables": variables,
            "total_lines": len(content.split('\n'))
        }
    
    def _get_function_name(self, node: Node, content: str) -> Optional[str]:
        """Extract function name from function node."""
        for child in node.children:
            if child.type == "identifier":
                return content[child.start_byte:child.end_byte]
        return None
    
    def _get_class_name(self, node: Node, content: str) -> Optional[str]:
        """Extract class name from class node."""
        for child in node.children:
            if child.type == "identifier":
                return content[child.start_byte:child.end_byte]
        return None
    
    def _calculate_js_quality_metrics(self, base_result: Dict[str, Any], 
                                    modules: Dict[str, Any], react: Dict[str, Any],
                                    modern_features: Dict[str, Any], 
                                    typescript: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate JavaScript-specific quality metrics."""
        return {
            "module_organization": modules.get("module_type", "unknown"),
            "modern_js_usage": modern_features.get("feature_usage_score", 0),
            "react_component_count": (
                len(react["components"]["function_components"]) +
                len(react["components"]["class_components"]) +
                len(react["components"]["arrow_function_components"])
            ),
            "typescript_coverage": typescript.get("type_coverage_score", 0) if typescript.get("is_typescript") else 0,
            "async_adoption": len(modern_features["async_patterns"]["async_functions"]) > 0,
            "overall_score": 0.0  # To be calculated based on above metrics
        }
    
    # Placeholder methods for React analysis (would need full implementation)
    def _find_react_imports(self, root_node: Node, content: str) -> List[Dict[str, Any]]:
        """Find React-related imports."""
        # Simplified - would need proper parsing
        if "react" in content.lower():
            return [{"type": "react", "found": True}]
        return []
    
    def _is_react_component(self, node: Node, content: str) -> bool:
        """Check if function is a React component."""
        # Simplified check - would need JSX analysis
        func_content = content[node.start_byte:node.end_byte]
        return "return" in func_content and ("<" in func_content or "jsx" in func_content.lower())
    
    def _parse_react_component(self, node: Node, content: str, comp_type: str) -> Dict[str, Any]:
        """Parse React component details."""
        return {
            "name": self._get_function_name(node, content) or "anonymous",
            "type": comp_type,
            "line": node.start_point[0] + 1,
            "has_jsx": True  # Simplified
        }
    
    # Additional placeholder methods would be implemented for complete functionality
    def _extends_react_component(self, node: Node, content: str) -> bool:
        return "extends" in content[node.start_byte:node.end_byte] and "Component" in content[node.start_byte:node.end_byte]
    
    def _is_arrow_component(self, node: Node, content: str) -> bool:
        return "=>" in content[node.start_byte:node.end_byte]
    
    def _analyze_hook_call(self, node: Node, content: str) -> Optional[Dict[str, Any]]:
        call_text = content[node.start_byte:node.end_byte]
        if "use" in call_text and call_text.startswith("use"):
            return {"name": call_text.split("(")[0], "is_built_in": call_text.startswith(("useState", "useEffect", "useContext"))}
        return None
    
    def _parse_jsx_element(self, node: Node, content: str) -> Dict[str, Any]:
        return {"line": node.start_point[0] + 1, "element": content[node.start_byte:node.end_byte][:50]}
    
    def _get_class_extends(self, node: Node, content: str) -> Optional[str]:
        if "extends" in content[node.start_byte:node.end_byte]:
            return "Component"  # Simplified
        return None
    
    # TypeScript parsing methods (simplified)
    def _parse_interface(self, node: Node, content: str) -> Dict[str, Any]:
        return {"name": "Interface", "line": node.start_point[0] + 1}
    
    def _parse_type_alias(self, node: Node, content: str) -> Dict[str, Any]:
        return {"name": "Type", "line": node.start_point[0] + 1}
    
    def _parse_enum(self, node: Node, content: str) -> Dict[str, Any]:
        return {"name": "Enum", "line": node.start_point[0] + 1}
    
    def _parse_decorator(self, node: Node, content: str) -> Dict[str, Any]:
        return {"name": "Decorator", "line": node.start_point[0] + 1}
    
    def _parse_require_call(self, node: Node, content: str) -> Dict[str, Any]:
        return {"line": node.start_point[0] + 1, "module": "unknown"}
    
    def _parse_dynamic_import(self, node: Node, content: str) -> Dict[str, Any]:
        return {"line": node.start_point[0] + 1, "module": "unknown"}
    
    def _parse_export_statement(self, node: Node, content: str) -> Dict[str, Any]:
        export_text = content[node.start_byte:node.end_byte]
        return {
            "line": node.start_point[0] + 1,
            "export_type": "default" if "default" in export_text else "named",
            "statement": export_text
        }