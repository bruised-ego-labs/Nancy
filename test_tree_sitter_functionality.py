#!/usr/bin/env python3
"""
Test script to validate tree-sitter functionality in Nancy container.
This tests that tree-sitter can successfully parse code in multiple languages.
"""

import tree_sitter
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_java
import tree_sitter_c
import tree_sitter_cpp
import tree_sitter_go
import tree_sitter_rust

def test_language_parsing():
    """Test that tree-sitter can parse code samples in various languages."""
    
    # Test Python parsing
    try:
        python_parser = tree_sitter.Parser()
        python_parser.set_language(tree_sitter_python.language())
        
        python_code = b"""
def hello_world(name):
    print(f"Hello, {name}!")
    return True
"""
        tree = python_parser.parse(python_code)
        print(f"✓ Python parsing successful: {tree.root_node.type}")
    except Exception as e:
        print(f"✗ Python parsing failed: {e}")
        return False
    
    # Test JavaScript parsing
    try:
        js_parser = tree_sitter.Parser()
        js_parser.set_language(tree_sitter_javascript.language())
        
        js_code = b"""
function calculateSum(a, b) {
    const result = a + b;
    return result;
}
"""
        tree = js_parser.parse(js_code)
        print(f"✓ JavaScript parsing successful: {tree.root_node.type}")
    except Exception as e:
        print(f"✗ JavaScript parsing failed: {e}")
        return False
    
    # Test Java parsing
    try:
        java_parser = tree_sitter.Parser()
        java_parser.set_language(tree_sitter_java.language())
        
        java_code = b"""
public class TestClass {
    public static void main(String[] args) {
        System.out.println("Hello World");
    }
}
"""
        tree = java_parser.parse(java_code)
        print(f"✓ Java parsing successful: {tree.root_node.type}")
    except Exception as e:
        print(f"✗ Java parsing failed: {e}")
        return False
    
    # Test C parsing
    try:
        c_parser = tree_sitter.Parser()
        c_parser.set_language(tree_sitter_c.language())
        
        c_code = b"""
#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
"""
        tree = c_parser.parse(c_code)
        print(f"✓ C parsing successful: {tree.root_node.type}")
    except Exception as e:
        print(f"✗ C parsing failed: {e}")
        return False
    
    # Test Go parsing
    try:
        go_parser = tree_sitter.Parser()
        go_parser.set_language(tree_sitter_go.language())
        
        go_code = b"""
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
"""
        tree = go_parser.parse(go_code)
        print(f"✓ Go parsing successful: {tree.root_node.type}")
    except Exception as e:
        print(f"✗ Go parsing failed: {e}")
        return False
    
    return True

def test_ast_traversal():
    """Test AST traversal capabilities."""
    try:
        parser = tree_sitter.Parser()
        parser.set_language(tree_sitter_python.language())
        
        code = b"""
class Calculator:
    def add(self, a, b):
        return a + b
    
    def multiply(self, a, b):
        return a * b
"""
        tree = parser.parse(code)
        
        # Find all function definitions
        def find_functions(node):
            functions = []
            if node.type == 'function_definition':
                func_name_node = node.child_by_field_name('name')
                if func_name_node:
                    functions.append(func_name_node.text.decode('utf-8'))
            
            for child in node.children:
                functions.extend(find_functions(child))
            
            return functions
        
        functions = find_functions(tree.root_node)
        print(f"✓ AST traversal successful. Found functions: {functions}")
        return len(functions) > 0
        
    except Exception as e:
        print(f"✗ AST traversal failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing tree-sitter functionality...")
    print("=" * 50)
    
    parsing_success = test_language_parsing()
    ast_success = test_ast_traversal()
    
    print("=" * 50)
    if parsing_success and ast_success:
        print("✓ All tree-sitter tests passed! Codebase MCP server should work correctly.")
        exit(0)
    else:
        print("✗ Some tree-sitter tests failed. Please check the installation.")
        exit(1)