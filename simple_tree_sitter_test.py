#!/usr/bin/env python3
"""
Simple Tree-sitter Test for Nancy MCP Architecture
Tests basic tree-sitter functionality without Unicode characters for Windows compatibility.
"""

import sys

def test_imports():
    """Test importing all required tree-sitter modules."""
    print("Testing tree-sitter imports...")
    
    modules = [
        'tree_sitter',
        'tree_sitter_python',
        'tree_sitter_javascript', 
        'tree_sitter_c',
        'tree_sitter_cpp',
        'tree_sitter_java',
        'tree_sitter_go',
        'tree_sitter_rust',
        'tree_sitter_php',
        'tree_sitter_ruby',
        'tree_sitter_typescript'
    ]
    
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  OK: {module}")
        except ImportError as e:
            print(f"  FAIL: {module} - {e}")
            failed.append(module)
    
    if failed:
        print(f"\nFailed imports: {', '.join(failed)}")
        return False
    
    print("All imports successful!")
    return True

def test_parsing():
    """Test basic parsing for key languages."""
    print("\nTesting basic parsing...")
    
    try:
        import tree_sitter
        import tree_sitter_python
        import tree_sitter_javascript
        import tree_sitter_java
        
        # Test Python
        python_parser = tree_sitter.Parser()
        python_parser.set_language(tree_sitter_python.language())
        python_code = b'def hello(): pass'
        tree = python_parser.parse(python_code)
        print(f"  OK: Python parsing - {tree.root_node.type}")
        
        # Test JavaScript
        js_parser = tree_sitter.Parser()
        js_parser.set_language(tree_sitter_javascript.language())
        js_code = b'function hello() { return true; }'
        tree = js_parser.parse(js_code)
        print(f"  OK: JavaScript parsing - {tree.root_node.type}")
        
        # Test Java
        java_parser = tree_sitter.Parser()
        java_parser.set_language(tree_sitter_java.language())
        java_code = b'public class Test { public static void main(String[] args) {} }'
        tree = java_parser.parse(java_code)
        print(f"  OK: Java parsing - {tree.root_node.type}")
        
        print("Basic parsing successful!")
        return True
        
    except Exception as e:
        print(f"  FAIL: Parsing test failed - {e}")
        return False

def test_ast_traversal():
    """Test AST traversal capabilities."""
    print("\nTesting AST traversal...")
    
    try:
        import tree_sitter
        import tree_sitter_python
        
        parser = tree_sitter.Parser()
        parser.set_language(tree_sitter_python.language())
        
        code = b'''
def function1():
    pass

def function2():
    return 42

class MyClass:
    def method1(self):
        pass
'''
        
        tree = parser.parse(code)
        
        # Find function definitions
        def find_functions(node):
            functions = []
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    functions.append(name_node.text.decode('utf-8'))
            
            for child in node.children:
                functions.extend(find_functions(child))
            
            return functions
        
        functions = find_functions(tree.root_node)
        print(f"  OK: Found functions: {functions}")
        
        if len(functions) >= 3:  # function1, function2, method1
            print("AST traversal successful!")
            return True
        else:
            print(f"  FAIL: Expected at least 3 functions, found {len(functions)}")
            return False
            
    except Exception as e:
        print(f"  FAIL: AST traversal failed - {e}")
        return False

def main():
    """Run all tests."""
    print("Nancy Tree-sitter Installation Test")
    print("=" * 50)
    
    tests = [
        ("Import Test", test_imports),
        ("Parsing Test", test_parsing),
        ("AST Traversal Test", test_ast_traversal)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"CRASH: {test_name} - {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("SUCCESS: All tests passed!")
        print("Tree-sitter is ready for Nancy MCP codebase analysis.")
        print("\nCapabilities verified:")
        print("- Multi-language parsing support")
        print("- AST analysis and traversal")
        print("- Codebase MCP server integration ready")
        return 0
    else:
        print("FAILURE: Some tests failed!")
        print("Check tree-sitter installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())