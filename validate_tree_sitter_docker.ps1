# Tree-sitter Docker Validation Script
# Validates that tree-sitter is properly installed in Nancy's Docker container

Write-Host "Tree-sitter Docker Validation for Nancy MCP Architecture" -ForegroundColor Green
Write-Host "=" * 60

# Check if Docker is running
try {
    docker version | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Docker is not running or not available" -ForegroundColor Red
    exit 1
}

# Check if Nancy API container is available
$containerStatus = docker-compose ps api --format json | ConvertFrom-Json
if ($containerStatus.State -eq "running") {
    Write-Host "✓ Nancy API container is running" -ForegroundColor Green
} else {
    Write-Host "⚠ Nancy API container is not running. Starting..." -ForegroundColor Yellow
    docker-compose up -d api
    Start-Sleep 10
    
    $containerStatus = docker-compose ps api --format json | ConvertFrom-Json
    if ($containerStatus.State -eq "running") {
        Write-Host "✓ Nancy API container started successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to start Nancy API container" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nTesting tree-sitter imports..." -ForegroundColor Cyan

# Test tree-sitter imports
$importTest = @"
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
print('SUCCESS: All tree-sitter modules imported')
"@

try {
    $result = docker exec nancy-api-1 python3 -c $importTest
    if ($result -eq "SUCCESS: All tree-sitter modules imported") {
        Write-Host "✓ All tree-sitter modules imported successfully" -ForegroundColor Green
    } else {
        Write-Host "✗ Tree-sitter import test failed" -ForegroundColor Red
        Write-Host "Output: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Failed to run import test in container" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nTesting basic parsing functionality..." -ForegroundColor Cyan

# Test basic parsing
$parseTest = @"
import tree_sitter
import tree_sitter_python
import tree_sitter_javascript

# Test Python parsing
python_parser = tree_sitter.Parser()
python_parser.set_language(tree_sitter_python.language())
python_tree = python_parser.parse(b'def hello(): pass')
print(f'Python: {python_tree.root_node.type}')

# Test JavaScript parsing  
js_parser = tree_sitter.Parser()
js_parser.set_language(tree_sitter_javascript.language())
js_tree = js_parser.parse(b'function test() { return true; }')
print(f'JavaScript: {js_tree.root_node.type}')

print('SUCCESS: Basic parsing tests completed')
"@

try {
    $result = docker exec nancy-api-1 python3 -c $parseTest
    if ($result -like "*SUCCESS: Basic parsing tests completed*") {
        Write-Host "✓ Basic parsing functionality verified" -ForegroundColor Green
        Write-Host "Parse results:" -ForegroundColor Gray
        $result.Split("`n") | ForEach-Object { 
            if ($_ -and $_ -ne "SUCCESS: Basic parsing tests completed") {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "✗ Parsing test failed" -ForegroundColor Red
        Write-Host "Output: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Failed to run parsing test in container" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nTesting AST analysis capabilities..." -ForegroundColor Cyan

# Test AST analysis
$astTest = @"
import tree_sitter
import tree_sitter_python

parser = tree_sitter.Parser()
parser.set_language(tree_sitter_python.language())

code = b'''
def function1():
    pass

class TestClass:
    def method1(self):
        return 42
'''

tree = parser.parse(code)

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
print(f'Found functions: {functions}')
print('SUCCESS: AST analysis working')
"@

try {
    $result = docker exec nancy-api-1 python3 -c $astTest
    if ($result -like "*SUCCESS: AST analysis working*") {
        Write-Host "✓ AST analysis capabilities verified" -ForegroundColor Green
        $result.Split("`n") | ForEach-Object { 
            if ($_ -and $_ -ne "SUCCESS: AST analysis working") {
                Write-Host "  $_" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "✗ AST analysis test failed" -ForegroundColor Red
        Write-Host "Output: $result" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Failed to run AST analysis test in container" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n" + "=" * 60
Write-Host "VALIDATION COMPLETE" -ForegroundColor Green -BackgroundColor Black
Write-Host "=" * 60

Write-Host "✓ Tree-sitter installation validated successfully" -ForegroundColor Green
Write-Host "✓ All required language parsers are available" -ForegroundColor Green  
Write-Host "✓ Basic parsing functionality works correctly" -ForegroundColor Green
Write-Host "✓ AST analysis capabilities are functional" -ForegroundColor Green

Write-Host "`nNancy's codebase MCP server is ready for multi-language analysis!" -ForegroundColor Yellow

Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Test codebase MCP server with actual code repositories" -ForegroundColor White
Write-Host "2. Verify integration with Nancy's MCP architecture" -ForegroundColor White  
Write-Host "3. Run comprehensive benchmarks if needed" -ForegroundColor White

exit 0