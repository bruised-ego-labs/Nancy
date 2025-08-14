#!/usr/bin/env python3
"""
Test script for comprehensive spreadsheet processing in Nancy's Four-Brain architecture.
Tests CSV, Excel files with multiple sheets, and verifies all four brains receive data.
"""

import requests
import json
import time
import os

# Configuration
NANCY_API_URL = "http://localhost:8000"
TEST_FILES = [
    {
        "filename": "thermal_test_results.csv",
        "author": "Alice Johnson",
        "description": "Thermal testing data with temperature measurements and compliance status"
    },
    {
        "filename": "mechanical_analysis.csv", 
        "author": "Bob Smith",
        "description": "Mechanical stress analysis with materials and cost data"
    },
    {
        "filename": "project_dashboard.xlsx",
        "author": "Project Manager",
        "description": "Multi-sheet Excel file with component status, test results, and requirements"
    }
]

def test_file_ingestion(filename, author, description):
    """Test ingestion of a spreadsheet file."""
    print(f"\n{'='*60}")
    print(f"Testing ingestion of: {filename}")
    print(f"Author: {author}")
    print(f"Description: {description}")
    print(f"{'='*60}")
    
    # Read file
    file_path = f"test_data/{filename}"
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, 'application/octet-stream')}
            data = {'author': author}
            
            print(f"Uploading {filename} to Nancy API...")
            response = requests.post(f"{NANCY_API_URL}/api/ingest", files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS: {filename} ingested successfully!")
                print(f"   Doc ID: {result.get('doc_id', 'N/A')}")
                print(f"   Status: {result.get('status', 'N/A')}")
                print(f"   File Type: {result.get('file_type', 'N/A')}")
                
                # Additional details for spreadsheets
                if result.get('sheets_processed'):
                    print(f"   Sheets Processed: {result.get('sheets_processed', 0)}")
                    print(f"   Total Rows: {result.get('total_rows', 0)}")
                    print(f"   Total Columns: {result.get('total_columns', 0)}")
                    if result.get('processed_sheet_names'):
                        print(f"   Sheet Names: {', '.join(result['processed_sheet_names'])}")
                
                return True
            else:
                print(f"FAILED: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"ERROR: Exception during ingestion: {e}")
        return False

def test_query_capabilities():
    """Test querying capabilities across all four brains."""
    print(f"\n{'='*60}")
    print("Testing Query Capabilities Across Four Brains")
    print(f"{'='*60}")
    
    # Test queries that should leverage different brains
    test_queries = [
        {
            "query": "What thermal tests were performed and what were the results?",
            "expected_brain": "Vector + Analytical",
            "description": "Should find thermal test data and provide structured results"
        },
        {
            "query": "Who are the engineers responsible for thermal testing?",
            "expected_brain": "Graph + Vector", 
            "description": "Should identify people and their relationships to thermal work"
        },
        {
            "query": "Show me components that failed thermal requirements",
            "expected_brain": "Analytical + Vector",
            "description": "Should filter structured data for failed components"
        },
        {
            "query": "What is the relationship between cost and material type?",
            "expected_brain": "Analytical + Graph",
            "description": "Should analyze correlations in spreadsheet data"
        },
        {
            "query": "Which test categories have the highest pass rates?",
            "expected_brain": "Analytical",
            "description": "Should calculate statistics from test summary data"
        }
    ]
    
    for i, test_case in enumerate(test_queries, 1):
        print(f"\n--- Query Test {i} ---")
        print(f"Query: {test_case['query']}")
        print(f"Expected Brain(s): {test_case['expected_brain']}")
        print(f"Description: {test_case['description']}")
        
        try:
            payload = {"query": test_case["query"]}
            response = requests.post(f"{NANCY_API_URL}/api/query", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print(f"Response received:")
                print(f"   Brain Used: {result.get('brain_used', 'Unknown')}")
                print(f"   Response: {result.get('response', 'No response')[:200]}...")
                
                if result.get('metadata'):
                    print(f"   Metadata: {result['metadata']}")
                    
            else:
                print(f"Query failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Query error: {e}")
        
        time.sleep(1)  # Brief delay between queries

def verify_data_storage():
    """Verify data was stored correctly in all brains."""
    print(f"\n{'='*60}")
    print("Verifying Data Storage Across Four Brains")
    print(f"{'='*60}")
    
    # Test basic health and storage verification
    try:
        response = requests.get(f"{NANCY_API_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print("Nancy API Health Check:")
            for brain, status in health.items():
                print(f"   {brain}: {status}")
        else:
            print(f"Health check failed: {response.status_code}")
            
    except Exception as e:
        print(f"Health check error: {e}")
    
    # Test a simple query to verify basic functionality
    try:
        payload = {"query": "What files have been ingested?"}
        response = requests.post(f"{NANCY_API_URL}/api/query", json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nBasic query successful:")
            print(f"   Response: {result.get('response', 'No response')[:300]}...")
        else:
            print(f"Basic query failed: {response.status_code}")
            
    except Exception as e:
        print(f"Basic query error: {e}")

def main():
    """Main test execution."""
    print("Nancy Four-Brain Spreadsheet Processing Test")
    print("=" * 60)
    
    # Test file ingestion
    success_count = 0
    for test_file in TEST_FILES:
        if test_file_ingestion(**test_file):
            success_count += 1
        time.sleep(2)  # Allow processing time between files
    
    print(f"\n{'='*60}")
    print(f"Ingestion Results: {success_count}/{len(TEST_FILES)} files processed successfully")
    print(f"{'='*60}")
    
    if success_count > 0:
        # Allow time for all processing to complete
        print("Waiting 5 seconds for processing to complete...")
        time.sleep(5)
        
        # Test querying capabilities
        test_query_capabilities()
        
        # Verify data storage
        verify_data_storage()
    else:
        print("No files were successfully ingested. Skipping query tests.")
    
    print(f"\n{'='*60}")
    print("Test Complete!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()