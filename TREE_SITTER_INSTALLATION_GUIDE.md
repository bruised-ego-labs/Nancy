# Tree-sitter Installation Guide for Nancy MCP Architecture

This guide documents the complete tree-sitter dependencies installation for Nancy's codebase MCP server functionality.

## Overview

Tree-sitter provides fast, incremental parsing for multiple programming languages, enabling Nancy's codebase MCP server to perform sophisticated AST analysis across different codebases.

## Supported Languages

The following programming languages are now fully supported in Nancy's containerized environment:

- **Python** (.py)
- **JavaScript/JSX** (.js, .jsx) 
- **TypeScript** (.ts, .tsx)
- **Java** (.java)
- **C** (.c, .h)
- **C++** (.cpp, .hpp, .cc, .cxx)
- **Go** (.go)
- **Rust** (.rs)
- **PHP** (.php)
- **Ruby** (.rb)

## Installation Details

### 1. Requirements.txt Updates

The following tree-sitter dependencies have been added to `nancy-services/requirements.txt`:

```
# Code analysis and repository integration
tree-sitter>=0.21.0
tree-sitter-python>=0.21.0
tree-sitter-javascript>=0.21.0
tree-sitter-c>=0.21.0
tree-sitter-cpp>=0.21.0
tree-sitter-java>=0.21.0
tree-sitter-go>=0.21.0
tree-sitter-rust>=0.21.0
tree-sitter-php>=0.21.0
tree-sitter-ruby>=0.21.0
tree-sitter-typescript>=0.21.0
GitPython>=3.1.40
```

### 2. Docker Configuration Updates

The Nancy services Dockerfile has been updated to include build tools required for tree-sitter compilation:

```dockerfile
# Install Python 3, pip, and build tools for tree-sitter compilation
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    gcc \
    g++ \
    make \
    git \
    && rm -rf /var/lib/apt/lists/*
```

### 3. Build Process

Tree-sitter languages are compiled during the Docker build process with proper caching for optimal performance.

## Validation

### Automated Testing

Two validation scripts are provided:

1. **comprehensive validation**: `validate_tree_sitter_installation.py`
   - Full test suite with detailed language parsing tests
   - AST analysis capabilities verification
   - MCP integration requirements validation

2. **Simple validation**: `simple_tree_sitter_test.py`
   - Basic import and parsing tests
   - Windows-compatible (no Unicode)
   - Quick validation of core functionality

### Manual Validation

To manually validate tree-sitter installation in the Nancy container:

```bash
# Start Nancy services
docker-compose up -d

# Test basic imports
docker exec nancy-api-1 python3 -c "
import tree_sitter
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_java
print('Tree-sitter imports successful!')
"

# Test parsing functionality
docker exec nancy-api-1 python3 -c "
import tree_sitter
import tree_sitter_python

parser = tree_sitter.Parser()
parser.set_language(tree_sitter_python.language())
tree = parser.parse(b'def hello(): pass')
print(f'Python parsing successful: {tree.root_node.type}')
"
```

### Expected Results

Successful installation should show:
- All language modules import without errors
- Parser initialization works for each language
- AST parsing produces expected node types
- Tree traversal and analysis functions correctly

## Codebase MCP Server Integration

### Language Detection

The codebase MCP server uses file extensions to determine the appropriate parser:

```python
LANGUAGE_MAPPINGS = {
    '.py': 'python',
    '.js': 'javascript', 
    '.jsx': 'javascript',
    '.ts': 'typescript',
    '.tsx': 'typescript', 
    '.java': 'java',
    '.c': 'c',
    '.h': 'c',
    '.cpp': 'cpp',
    '.hpp': 'cpp',
    '.cc': 'cpp',
    '.cxx': 'cpp',
    '.go': 'go',
    '.rs': 'rust',
    '.php': 'php',
    '.rb': 'ruby'
}
```

### AST Analysis Capabilities

Tree-sitter enables the following analysis features:

- **Function/Method Detection**: Extract function signatures and locations
- **Class/Interface Analysis**: Identify class hierarchies and structures
- **Import/Dependency Mapping**: Track module dependencies
- **Symbol Resolution**: Find variable and function usage
- **Structural Metrics**: Calculate complexity and code metrics
- **Change Analysis**: Detect structural changes in code

### Performance Characteristics

- **Incremental Parsing**: Only re-parse changed code sections
- **Memory Efficient**: Optimized for large codebases
- **Fast Execution**: ONNX-optimized parsing performance
- **Concurrent Processing**: Multi-language parsing in parallel

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure container is built with latest requirements.txt
   - Verify build tools are available in container
   - Check that all dependencies compiled successfully

2. **Parsing Failures**
   - Validate code syntax is correct for target language
   - Check parser language matches file content
   - Ensure tree-sitter version compatibility

3. **Memory Issues**
   - Large files may require increased container memory
   - Consider chunking for very large codebases
   - Monitor resource usage during analysis

### Build Troubleshooting

If tree-sitter dependencies fail to install:

```bash
# Rebuild with verbose output
docker-compose build --no-cache api

# Check build logs for compilation errors
docker-compose logs api

# Verify system dependencies in container
docker exec nancy-api-1 gcc --version
docker exec nancy-api-1 make --version
```

### Runtime Troubleshooting

If parsing fails at runtime:

```bash
# Test individual language parsers
docker exec nancy-api-1 python3 /app/simple_tree_sitter_test.py

# Check specific language availability
docker exec nancy-api-1 python3 -c "
import tree_sitter_python
print('Python parser available')
"

# Verify parser can handle target code
docker exec nancy-api-1 python3 -c "
import tree_sitter
import tree_sitter_python
parser = tree_sitter.Parser()
parser.set_language(tree_sitter_python.language())
# Test with your specific code here
"
```

## Testing Integration with Codebase MCP Server

To test integration with Nancy's codebase MCP server:

1. **Start Nancy Services**:
   ```bash
   docker-compose up -d
   ```

2. **Test MCP Server Access**:
   ```bash
   # This would test actual MCP server functionality
   python test_codebase_mcp.py
   ```

3. **Validate Multi-language Analysis**:
   - Upload code files in different languages
   - Verify AST analysis works for each language
   - Check that cross-language references are detected

## Performance Optimization

### Memory Management
- Tree-sitter parsers are memory-efficient
- Reuse parser instances when possible
- Clear parse trees after analysis to free memory

### Caching Strategy
- Cache parsed ASTs for unchanged files
- Use file modification times for cache invalidation
- Implement LRU eviction for memory management

### Batch Processing
- Process multiple files in parallel
- Group files by language for parser efficiency
- Use streaming for very large codebases

## Future Enhancements

Potential improvements to tree-sitter integration:

1. **Additional Languages**: Add support for more languages as needed
2. **Custom Queries**: Implement language-specific query patterns
3. **Incremental Updates**: Real-time parsing for file changes
4. **Error Recovery**: Improved handling of malformed code
5. **Performance Metrics**: Detailed analysis timing and resource usage

## Conclusion

Tree-sitter dependencies are now fully integrated into Nancy's MCP architecture, enabling sophisticated multi-language codebase analysis. The installation is containerized for consistency and includes comprehensive validation tools.

The codebase MCP server can now:
- Parse and analyze code in 11 programming languages
- Perform deep AST analysis and traversal
- Extract structural information and metrics
- Support real-time code intelligence features

For any issues or questions, refer to the troubleshooting section or test with the provided validation scripts.