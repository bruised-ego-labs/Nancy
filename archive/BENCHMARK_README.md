# Nancy Three-Brain Architecture Benchmark

This benchmark demonstrates the superiority of Nancy's three-brain architecture over standard vector-only RAG systems for multidisciplinary engineering teams.

## Overview

The benchmark evaluates how well each system can serve the information needs of different engineering disciplines working on a complex IoT device project:

- **Systems Engineers**: Architecture decisions, requirements, constraints
- **Mechanical Engineers**: Design analysis, materials, thermal considerations  
- **Electrical Engineers**: Circuits, power management, EMC compliance
- **Firmware Engineers**: Software architecture, memory management, protocols
- **Industrial Designers**: User experience, ergonomics, aesthetics
- **Project Managers**: Decisions, timelines, budget, coordination

## What Makes Three-Brain Architecture Better?

### 1. Author Attribution & Accountability
Standard RAG can't tell you *who* wrote something or made a decision. Nancy's knowledge graph tracks authorship and relationships.

**Example Query:** "Who defined the thermal constraints for the enclosure?"
- **Three-Brain**: ✅ "Sarah Chen defined thermal constraints in thermal_constraints_doc.txt"
- **Standard RAG**: ❌ Returns text about thermal constraints but no author information

### 2. Metadata-Filtered Searches
Standard RAG can't filter by file dates, types, or other metadata. Nancy's analytical brain stores structured metadata.

**Example Query:** "Show me all documents from last month about power consumption"
- **Three-Brain**: ✅ Filters by date AND semantic content
- **Standard RAG**: ❌ Can only do semantic search, ignores timing

### 3. Cross-Disciplinary Relationships
Standard RAG can't find connections between documents. Nancy's knowledge graph tracks relationships.

**Example Query:** "What thermal issues affected Mike's electrical design?"
- **Three-Brain**: ✅ Finds connections between thermal analysis and electrical decisions
- **Standard RAG**: ❌ Treats documents as isolated text chunks

### 4. Complex Multi-Constraint Queries
Standard RAG struggles with queries requiring multiple types of information. Nancy orchestrates all three brains.

**Example Query:** "What decisions did Sarah Chen make in March that affected power consumption?"
- **Three-Brain**: ✅ Combines author (knowledge graph) + time (metadata) + topic (vector)
- **Standard RAG**: ❌ Can only do semantic matching on "power consumption"

## Benchmark Test Scenarios

The benchmark includes 14 realistic queries across 7 categories:

### Systems Engineering
- Power consumption requirements lookup
- Author attribution for constraints

### Mechanical Engineering  
- Recent CAD file and analysis retrieval
- Material selection research

### Electrical Engineering
- Document relationship discovery
- EMC testing approval tracking

### Firmware Engineering
- Memory requirement analysis
- Communication protocol research

### Industrial Design
- User feedback influence tracking
- Ergonomic study attribution

### Project Management
- Meeting decision tracking
- Budget constraint relationships

### Cross-Disciplinary (The Real Test)
- Complex multi-team dependency tracking
- Recent work across all disciplines

## Evaluation Metrics

The benchmark measures:

- **Precision@10**: How many retrieved documents are actually relevant
- **Recall@10**: How many relevant documents were successfully found
- **F1 Score**: Balanced precision/recall measure
- **Mean Reciprocal Rank**: Average position of first relevant result
- **Author Attribution Accuracy**: Percentage of queries where correct author was identified
- **Response Time**: Speed of query processing

## Running the Benchmark

### Prerequisites
1. Docker and Docker Compose installed
2. Python 3.9+ with required dependencies
3. Nancy services running (`docker-compose up -d --build`)

### Quick Start
```powershell
# Run the complete benchmark demonstration
.\test_benchmark_demo.ps1
```

### Manual Execution
```bash
# Start Nancy services
docker-compose up -d --build

# Run benchmark
python run_benchmark.py
```

## Expected Results

Based on the multidisciplinary nature of engineering teams, the three-brain architecture should significantly outperform standard RAG on:

1. **Author Attribution**: 100% vs 0% (standard RAG has no author info)
2. **Cross-Disciplinary Queries**: 50-80% improvement in F1 score
3. **Metadata Filtering**: 40-60% improvement in recall
4. **Relationship Discovery**: 60-90% improvement in precision

The biggest advantages appear when queries require:
- Finding WHO made decisions or created content
- Filtering by time, file type, or other metadata  
- Discovering connections between documents/people
- Complex queries combining multiple constraint types

## Real-World Impact

For engineering teams, this translates to:

- **Faster Decision Traceability**: "Who approved this design change?"
- **Better Cross-Team Coordination**: "What mechanical constraints affect electrical design?"
- **Improved Knowledge Continuity**: "What did the previous engineer document about this issue?"
- **Enhanced Project Management**: "What decisions were made in the last design review?"

## Test Data

The benchmark uses realistic engineering documents:
- System requirements specifications
- Thermal analysis reports
- Electrical design reviews
- EMC test results
- Voice of customer research
- Meeting transcripts
- Ergonomic studies

All documents include realistic author attribution and cross-references that mirror actual engineering project documentation.

## Extending the Benchmark

To test with your own data:

1. Add documents to `benchmark_test_data/` directory
2. Update the benchmark queries in `nancy-services/core/benchmark_framework.py`
3. Specify expected results and authors for new queries
4. Run the benchmark to see how Nancy performs on your specific use case

The framework is designed to be easily extensible for different industries and team structures beyond engineering.