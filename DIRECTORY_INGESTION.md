# Nancy Directory Ingestion System

## Overview

Nancy's Directory Ingestion System transforms the platform from reactive file upload to proactive project intelligence monitoring. It provides hash-based change detection, automated file discovery, and seamless integration with Nancy's four-brain architecture.

## Architecture

### Phase 1: Periodic Re-ingestion (Current Implementation)
- **Directory Scanning**: Periodic scans of configured directories
- **Hash-based Change Detection**: SHA256 hashing to identify new/modified files
- **File State Management**: DuckDB-based tracking of file states
- **Batch Processing**: Efficient processing of changed files through four-brain pipeline

### Core Components

#### 1. AnalyticalBrain Extensions (`search.py`)
- **File State Schema**: Tracks file paths, hashes, timestamps, processing status
- **Directory Configuration**: Manages watched directories with patterns
- **Change Detection Logic**: Compares current vs stored file hashes
- **Statistics and Monitoring**: Comprehensive file processing metrics

#### 2. DirectoryIngestionService (`ingestion.py`)
- **Directory Scanning**: Recursive file discovery with pattern matching
- **Hash Calculation**: SHA256 content hashing for change detection
- **Four-brain Integration**: Routes discovered files through existing pipeline
- **Error Handling**: Robust error handling with detailed logging

#### 3. API Endpoints (`api/endpoints/directory.py`)
- **Scan Operations**: Manual and automated directory scanning
- **Processing Control**: Batch processing of pending files
- **Configuration Management**: Directory setup and monitoring
- **Status Reporting**: Real-time system status and statistics

## Key Features

### Hash-based Change Detection
```python
# Detect file changes using content hashing
needs_processing = analytical_brain.upsert_file_state(
    file_path, content_hash, last_modified, file_size, 
    directory_root, relative_path
)
```

### Pattern-based File Filtering
- **Include Patterns**: `*.txt,*.md,*.py,*.js,*.json,*.csv,*.xlsx`
- **Ignore Patterns**: `.git/*,node_modules/*,__pycache__/*,*.pyc`
- **Smart Matching**: Filename and path-based pattern matching

### Four-brain Architecture Integration
1. **Vector Brain**: Semantic embedding of discovered text files
2. **Analytical Brain**: Metadata storage and file state tracking
3. **Graph Brain**: Relationship extraction and author attribution
4. **Linguistic Brain**: Enhanced entity recognition and content analysis

## API Endpoints

### POST `/api/directory/scan`
Scan directory for files and detect changes.

**Parameters:**
- `directory_path`: Absolute path to directory
- `recursive`: Scan subdirectories (default: true)
- `file_patterns`: Include patterns (optional)
- `ignore_patterns`: Exclude patterns (optional)
- `author`: Author attribution for files

**Response:**
```json
{
  "directory_path": "/path/to/project",
  "total_files_discovered": 25,
  "new_files": 3,
  "changed_files": 2,
  "unchanged_files": 20,
  "files_to_process": 5,
  "scan_timestamp": "2025-01-15T10:30:00Z"
}
```

### POST `/api/directory/process`
Process pending files through four-brain architecture.

**Parameters:**
- `limit`: Maximum files to process (default: 50)
- `author`: Author attribution

**Response:**
```json
{
  "status": "processing_complete",
  "processed_files": 5,
  "successful": 4,
  "failed": 1,
  "success_rate": 0.8,
  "results": [...]
}
```

### POST `/api/directory/scan-and-process`
Combined operation: scan and process in one call.

**Parameters:**
- `directory_path`: Absolute path to directory
- `recursive`: Scan subdirectories
- `file_patterns`: Include patterns
- `ignore_patterns`: Exclude patterns
- `author`: Author attribution
- `process_limit`: Max files to process

### POST `/api/directory/config`
Add directory to monitoring configuration.

**Parameters:**
- `directory_path`: Directory to monitor
- `recursive`: Include subdirectories
- `file_patterns`: File inclusion patterns
- `ignore_patterns`: File exclusion patterns

### GET `/api/directory/status`
Get comprehensive system status.

**Response:**
```json
{
  "configured_directories": 2,
  "pending_files": 0,
  "file_statistics": {
    "total_files_tracked": 150,
    "processing_errors": 0,
    "status_distribution": [...]
  }
}
```

## Docker Integration

### Volume Mounts
```yaml
volumes:
  - ./data:/app/data                    # Nancy persistent data
  - ./project_docs:/app/project_docs    # Project documents
  - ./benchmark_data:/app/benchmark_data # Test data
```

### Environment Variables
- `CHROMA_HOST`: ChromaDB service host
- `NEO4J_URI`: Neo4j connection string
- `GEMINI_API_KEY`: API key for Linguistic Brain

## Usage Examples

### 1. Initial Project Setup
```bash
# Configure directory for monitoring
curl -X POST http://localhost:8000/api/directory/config \
  -d "directory_path=/app/project_docs" \
  -d "recursive=true" \
  -d "file_patterns=*.txt,*.md,*.py,*.js,*.json,*.csv"

# Perform initial scan and processing
curl -X POST http://localhost:8000/api/directory/scan-and-process \
  -d "directory_path=/app/project_docs" \
  -d "author=Initial Setup" \
  -d "process_limit=100"
```

### 2. Regular Monitoring
```bash
# Check status
curl http://localhost:8000/api/directory/status

# Process any pending changes
curl -X POST http://localhost:8000/api/directory/process \
  -d "limit=50" \
  -d "author=Daily Processing"
```

### 3. Project Updates
```bash
# Scan specific directory after code changes
curl -X POST http://localhost:8000/api/directory/scan \
  -d "directory_path=/app/project_docs/src" \
  -d "author=Developer Update"

# Process discovered changes
curl -X POST http://localhost:8000/api/directory/process \
  -d "limit=20"
```

## Testing

### PowerShell Test Suite
```powershell
# Run comprehensive test suite
.\test_directory_ingestion.ps1
```

### Python Test Suite
```bash
# Install dependencies
pip install requests

# Run detailed testing
python test_directory_ingestion.py
```

### Test Coverage
- API health checks
- Directory configuration
- File scanning and discovery
- Hash-based change detection
- Four-brain processing integration
- Error handling and recovery
- Performance monitoring

## Performance Characteristics

### Scanning Performance
- **Small Projects** (< 100 files): < 1 second
- **Medium Projects** (100-1000 files): 1-5 seconds
- **Large Projects** (1000+ files): 5-30 seconds

### Processing Performance
- **Text Files**: 50-100 files/minute through four-brain pipeline
- **Spreadsheets**: 10-20 files/minute (includes structure analysis)
- **Memory Usage**: Scales with file content size and embeddings

### Change Detection Efficiency
- **Hash Calculation**: O(n) where n = file size
- **Database Lookups**: O(log n) with indexed file paths
- **Overall**: Only processes changed files, not entire corpus

## Engineering Team Integration

### Project Structure Awareness
```
project_root/
├── docs/           # Documentation and specifications  
├── specs/          # Requirements and technical specs
├── src/            # Source code and components
├── test_results/   # Test data and validation results
├── config/         # Configuration and deployment files
└── archive/        # Historical and deprecated files
```

### Author Attribution
- Automatic detection from file metadata
- Manual specification via API parameters
- Team member association in Graph Brain
- Expertise mapping based on file content

### Workflow Integration
1. **Development**: Continuous monitoring of source directories
2. **Documentation**: Automatic ingestion of updated specs and docs  
3. **Testing**: Integration of test results and validation data
4. **Deployment**: Configuration and infrastructure documentation

## Troubleshooting

### Common Issues

**Q: Files not being discovered**
- Check directory path is absolute
- Verify file patterns match your file types
- Ensure ignore patterns aren't excluding files
- Check file permissions

**Q: Processing failures**
- Review error messages in processing results
- Verify file encoding (UTF-8 recommended)  
- Check disk space for DuckDB and ChromaDB
- Monitor memory usage during large batch processing

**Q: Change detection not working**
- Verify file timestamps are updating
- Check hash calculation isn't failing
- Review database connectivity
- Ensure sufficient disk space for state tracking

### Health Monitoring
```bash
# Check service health
curl http://localhost:8000/api/directory/health

# Get detailed status
curl http://localhost:8000/api/directory/status

# Review recent processing
curl http://localhost:8000/api/directory/status | jq .file_statistics.recent_processing
```

## Future Enhancements (Phase 2)

### Real-time Monitoring
- File system event monitoring (inotify/watchdog)
- Immediate change detection and processing
- WebSocket notifications for real-time updates

### Advanced Analytics
- Processing performance analytics
- Content quality metrics
- Team collaboration insights
- Document lifecycle tracking

### Enterprise Features
- Multi-project support
- Role-based access control
- Audit logging and compliance
- Distributed processing support

## Security Considerations

### File System Access
- Directory access requires proper permissions
- Sandboxing recommended for untrusted content
- Path traversal protection built-in

### Content Processing
- Files processed through existing Nancy security measures
- No execution of discovered scripts or binaries
- Content validation before four-brain ingestion

### Data Privacy
- File hashes stored for change detection only
- Original file paths preserved for reference
- User-configurable retention policies

## Contributing

### Code Organization
- **Core Logic**: `nancy-services/core/`
- **API Endpoints**: `nancy-services/api/endpoints/`
- **Tests**: `test_directory_ingestion.*`
- **Documentation**: `DIRECTORY_INGESTION.md`

### Development Workflow
1. Implement feature in core components
2. Add/update API endpoints  
3. Create comprehensive tests
4. Update documentation
5. Validate with four-brain architecture

For questions or contributions, see the main Nancy project documentation.