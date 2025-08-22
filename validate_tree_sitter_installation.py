#!/usr/bin/env python3
"""
Comprehensive Tree-sitter Installation Validation Script for Nancy MCP Architecture

This script validates that all tree-sitter dependencies are properly installed
and can be used for codebase analysis in Nancy's MCP architecture.

Run this script inside the Nancy container or local environment to validate:
1. All tree-sitter language parsers are available
2. Parsing functionality works for each supported language
3. AST traversal and analysis capabilities are functional
4. Integration with codebase MCP server requirements

Usage:
    python3 validate_tree_sitter_installation.py

Expected Output:
    ✓ All tests pass - tree-sitter is ready for Nancy MCP codebase analysis
"""

import sys
import traceback
from typing import Dict, List, Tuple

def test_tree_sitter_imports() -> bool:
    """Test that all required tree-sitter modules can be imported."""
    print("Testing tree-sitter imports...")
    
    required_modules = [
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
    
    failed_imports = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"  OK {module}")
        except ImportError as e:
            print(f"  FAIL {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\nFAILED to import: {', '.join(failed_imports)}")
        return False
    
    print("SUCCESS: All tree-sitter modules imported successfully!")
    return True

def test_language_parsing() -> bool:
    """Test parsing functionality for each supported language."""
    print("\nTesting language parsing capabilities...")
    
    import tree_sitter
    import tree_sitter_python
    import tree_sitter_javascript
    import tree_sitter_java
    import tree_sitter_c
    import tree_sitter_cpp
    import tree_sitter_go
    import tree_sitter_rust
    import tree_sitter_php
    import tree_sitter_ruby
    import tree_sitter_typescript
    
    test_cases = [
        ('Python', tree_sitter_python.language(), b'''
def calculate_fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    @staticmethod
    def factorial(n):
        return 1 if n <= 1 else n * MathUtils.factorial(n-1)
'''),
        ('JavaScript', tree_sitter_javascript.language(), b'''
class Calculator {
    constructor() {
        this.history = [];
    }
    
    add(a, b) {
        const result = a + b;
        this.history.push(`${a} + ${b} = ${result}`);
        return result;
    }
    
    getHistory() {
        return this.history;
    }
}

const calc = new Calculator();
'''),
        ('Java', tree_sitter_java.language(), b'''
public class DatabaseConnection {
    private String connectionString;
    private boolean isConnected;
    
    public DatabaseConnection(String connectionString) {
        this.connectionString = connectionString;
        this.isConnected = false;
    }
    
    public boolean connect() {
        // Connection logic here
        this.isConnected = true;
        return true;
    }
    
    public void disconnect() {
        this.isConnected = false;
    }
}
'''),
        ('C', tree_sitter_c.language(), b'''
#include <stdio.h>
#include <stdlib.h>

typedef struct {
    int id;
    char name[50];
    float score;
} Student;

int compare_students(const void *a, const void *b) {
    Student *studentA = (Student *)a;
    Student *studentB = (Student *)b;
    return (studentA->score > studentB->score) - (studentA->score < studentB->score);
}

int main() {
    Student students[100];
    int count = 0;
    
    printf("Student Management System\\n");
    return 0;
}
'''),
        ('C++', tree_sitter_cpp.language(), b'''
#include <vector>
#include <algorithm>
#include <memory>

template<typename T>
class SmartArray {
private:
    std::vector<T> data;
    size_t capacity;

public:
    SmartArray(size_t initial_capacity = 10) : capacity(initial_capacity) {
        data.reserve(capacity);
    }
    
    void push_back(const T& value) {
        data.push_back(value);
    }
    
    T& operator[](size_t index) {
        return data[index];
    }
    
    size_t size() const {
        return data.size();
    }
};
'''),
        ('Go', tree_sitter_go.language(), b'''
package main

import (
    "fmt"
    "sync"
    "time"
)

type Worker struct {
    id       int
    jobChan  chan Job
    quitChan chan bool
    wg       *sync.WaitGroup
}

type Job struct {
    ID   int
    Data string
}

func (w *Worker) Start() {
    go func() {
        defer w.wg.Done()
        for {
            select {
            case job := <-w.jobChan:
                fmt.Printf("Worker %d processing job %d: %s\\n", w.id, job.ID, job.Data)
                time.Sleep(time.Millisecond * 100)
            case <-w.quitChan:
                return
            }
        }
    }()
}
'''),
        ('Rust', tree_sitter_rust.language(), b'''
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::thread;

#[derive(Debug, Clone)]
pub struct ThreadSafeCounter {
    count: Arc<Mutex<i32>>,
}

impl ThreadSafeCounter {
    pub fn new() -> Self {
        ThreadSafeCounter {
            count: Arc::new(Mutex::new(0)),
        }
    }
    
    pub fn increment(&self) -> Result<i32, Box<dyn std::error::Error>> {
        let mut count = self.count.lock()?;
        *count += 1;
        Ok(*count)
    }
    
    pub fn get_value(&self) -> Result<i32, Box<dyn std::error::Error>> {
        let count = self.count.lock()?;
        Ok(*count)
    }
}
'''),
        ('PHP', tree_sitter_php.language(), b'''<?php

namespace App\\Services;

use App\\Models\\User;
use App\\Interfaces\\UserRepositoryInterface;

class UserService {
    private UserRepositoryInterface $userRepository;
    
    public function __construct(UserRepositoryInterface $userRepository) {
        $this->userRepository = $userRepository;
    }
    
    public function createUser(array $userData): User {
        $user = new User();
        $user->setName($userData['name']);
        $user->setEmail($userData['email']);
        
        return $this->userRepository->save($user);
    }
    
    public function getUserById(int $id): ?User {
        return $this->userRepository->findById($id);
    }
}
'''),
        ('Ruby', tree_sitter_ruby.language(), b'''
class TaskManager
  attr_reader :tasks
  
  def initialize
    @tasks = []
    @completed_tasks = []
  end
  
  def add_task(title, description = "")
    task = {
      id: generate_id,
      title: title,
      description: description,
      created_at: Time.now,
      completed: false
    }
    @tasks << task
    task
  end
  
  def complete_task(task_id)
    task = @tasks.find { |t| t[:id] == task_id }
    return false unless task
    
    task[:completed] = true
    task[:completed_at] = Time.now
    @completed_tasks << @tasks.delete(task)
    true
  end
  
  private
  
  def generate_id
    Time.now.to_i + rand(1000)
  end
end
'''),
        ('TypeScript', tree_sitter_typescript.language(), b'''
interface DatabaseRecord {
    id: number;
    createdAt: Date;
    updatedAt: Date;
}

interface User extends DatabaseRecord {
    username: string;
    email: string;
    profile?: UserProfile;
}

interface UserProfile {
    firstName: string;
    lastName: string;
    avatar?: string;
}

class UserManager<T extends User> {
    private users: Map<number, T> = new Map();
    
    constructor(private readonly validator: (user: Partial<T>) => boolean) {}
    
    async createUser(userData: Omit<T, 'id' | 'createdAt' | 'updatedAt'>): Promise<T> {
        if (!this.validator(userData)) {
            throw new Error('Invalid user data');
        }
        
        const user: T = {
            ...userData,
            id: Date.now(),
            createdAt: new Date(),
            updatedAt: new Date()
        } as T;
        
        this.users.set(user.id, user);
        return user;
    }
    
    getUser(id: number): T | undefined {
        return this.users.get(id);
    }
}
''')
    ]
    
    failed_languages = []
    
    for language_name, language, code in test_cases:
        try:
            parser = tree_sitter.Parser()
            parser.set_language(language)
            tree = parser.parse(code)
            
            if tree.root_node.type in ['module', 'program', 'translation_unit', 'source_file']:
                print(f"  ✓ {language_name} parsing successful")
            else:
                print(f"  ⚠ {language_name} parsed but unexpected root node: {tree.root_node.type}")
        except Exception as e:
            print(f"  ✗ {language_name} parsing failed: {e}")
            failed_languages.append(language_name)
    
    if failed_languages:
        print(f"\n❌ Failed to parse: {', '.join(failed_languages)}")
        return False
    
    print("✅ All languages parsed successfully!")
    return True

def test_ast_analysis() -> bool:
    """Test advanced AST analysis capabilities required for codebase MCP server."""
    print("\nTesting AST analysis capabilities...")
    
    try:
        import tree_sitter
        import tree_sitter_python
        
        parser = tree_sitter.Parser()
        parser.set_language(tree_sitter_python.language())
        
        # Complex Python code for analysis
        code = b'''
import os
import sys
from typing import List, Dict, Optional

class CodeAnalyzer:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.analysis_results = {}
    
    def analyze_functions(self) -> List[Dict[str, str]]:
        """Extract function definitions and their metadata."""
        functions = []
        # Analysis logic here
        return functions
    
    def find_imports(self) -> List[str]:
        """Find all import statements."""
        imports = []
        # Import detection logic
        return imports
    
    def calculate_complexity(self, node) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1
        # Complexity calculation
        return complexity

def utility_function(param1: int, param2: str = "default") -> Optional[str]:
    if param1 > 0:
        return f"Result: {param2}"
    return None

# Global variable
GLOBAL_CONSTANT = "test_value"
'''
        
        tree = parser.parse(code)
        
        # Test 1: Find function definitions
        def find_functions(node):
            functions = []
            if node.type == 'function_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    functions.append({
                        'name': name_node.text.decode('utf-8'),
                        'start_line': node.start_point[0] + 1,
                        'end_line': node.end_point[0] + 1
                    })
            
            for child in node.children:
                functions.extend(find_functions(child))
            
            return functions
        
        functions = find_functions(tree.root_node)
        expected_functions = ['__init__', 'analyze_functions', 'find_imports', 'calculate_complexity', 'utility_function']
        found_function_names = [f['name'] for f in functions]
        
        if all(name in found_function_names for name in expected_functions):
            print(f"  ✓ Function extraction: Found {len(functions)} functions")
        else:
            missing = set(expected_functions) - set(found_function_names)
            print(f"  ✗ Function extraction: Missing {missing}")
            return False
        
        # Test 2: Find class definitions
        def find_classes(node):
            classes = []
            if node.type == 'class_definition':
                name_node = node.child_by_field_name('name')
                if name_node:
                    classes.append(name_node.text.decode('utf-8'))
            
            for child in node.children:
                classes.extend(find_classes(child))
            
            return classes
        
        classes = find_classes(tree.root_node)
        if 'CodeAnalyzer' in classes:
            print(f"  ✓ Class extraction: Found {len(classes)} classes")
        else:
            print(f"  ✗ Class extraction: CodeAnalyzer not found")
            return False
        
        # Test 3: Find import statements
        def find_imports(node):
            imports = []
            if node.type in ['import_statement', 'import_from_statement']:
                imports.append(node.text.decode('utf-8').strip())
            
            for child in node.children:
                imports.extend(find_imports(child))
            
            return imports
        
        imports = find_imports(tree.root_node)
        if len(imports) >= 3:  # Should find os, sys, typing imports
            print(f"  ✓ Import extraction: Found {len(imports)} imports")
        else:
            print(f"  ✗ Import extraction: Expected at least 3 imports, found {len(imports)}")
            return False
        
        print("✅ AST analysis capabilities working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ AST analysis test failed: {e}")
        traceback.print_exc()
        return False

def test_codebase_mcp_integration() -> bool:
    """Test specific requirements for Nancy's codebase MCP server."""
    print("\nTesting codebase MCP server integration requirements...")
    
    try:
        # Test that we can create language-specific parsers
        import tree_sitter
        import tree_sitter_python
        import tree_sitter_javascript
        import tree_sitter_java
        
        # Simulate the codebase MCP server's parser initialization
        parsers = {}
        
        language_configs = [
            ('python', tree_sitter_python.language(), ['.py']),
            ('javascript', tree_sitter_javascript.language(), ['.js', '.jsx']),
            ('java', tree_sitter_java.language(), ['.java'])
        ]
        
        for lang_name, language, extensions in language_configs:
            parser = tree_sitter.Parser()
            parser.set_language(language)
            parsers[lang_name] = {
                'parser': parser,
                'extensions': extensions
            }
            print(f"  ✓ {lang_name} parser initialized for extensions: {', '.join(extensions)}")
        
        # Test file extension mapping (as required by codebase MCP server)
        test_files = {
            'main.py': 'python',
            'app.js': 'javascript',
            'component.jsx': 'javascript', 
            'Application.java': 'java'
        }
        
        for filename, expected_lang in test_files.items():
            extension = '.' + filename.split('.')[-1]
            found_lang = None
            
            for lang_name, config in parsers.items():
                if extension in config['extensions']:
                    found_lang = lang_name
                    break
            
            if found_lang == expected_lang:
                print(f"  ✓ File mapping: {filename} → {found_lang}")
            else:
                print(f"  ✗ File mapping: {filename} → expected {expected_lang}, got {found_lang}")
                return False
        
        print("✅ Codebase MCP server integration requirements satisfied!")
        return True
        
    except Exception as e:
        print(f"❌ Codebase MCP integration test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all validation tests."""
    print("Nancy Tree-sitter Installation Validation")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_tree_sitter_imports),
        ("Language Parsing Tests", test_language_parsing),
        ("AST Analysis Tests", test_ast_analysis),
        ("Codebase MCP Integration Tests", test_codebase_mcp_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\nRunning {test_name}...")
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            traceback.print_exc()
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"{status} {test_name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("ALL TESTS PASSED!")
        print("Tree-sitter is properly installed and ready for Nancy MCP codebase analysis")
        print("\nNext steps:")
        print("1. Nancy's codebase MCP server can now parse multi-language codebases")
        print("2. AST analysis capabilities are fully functional")
        print("3. Integration with Nancy's MCP architecture is validated")
        return 0
    else:
        print("SOME TESTS FAILED!")
        print("Tree-sitter installation needs attention before using codebase MCP server")
        print("\nTroubleshooting:")
        print("1. Ensure all tree-sitter packages are installed: pip install -r requirements.txt")
        print("2. Check that build tools are available (gcc, g++, make)")
        print("3. Verify Docker container has proper dependencies")
        return 1

if __name__ == "__main__":
    sys.exit(main())