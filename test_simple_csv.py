#!/usr/bin/env python3
"""
Simple test for spreadsheet ingestion using requests to the Nancy API.
"""

import requests
import json
import time

def create_simple_csv():
    """Create a simple CSV for testing."""
    csv_content = """Name,Role,Department,Experience_Years
Alice Thompson,Lead Engineer,Thermal,8
Bob Chen,Senior Engineer,Power,6
Carol Davis,Principal Engineer,Mechanical,12
David Kim,Staff Engineer,Electrical,10
Eve Rodriguez,Senior Engineer,Software,7"""
    
    with open('simple_test.csv', 'w') as f:
        f.write(csv_content)
    
    return 'simple_test.csv'

def test_ingestion():
    """Test CSV ingestion through Nancy API."""
    print("Testing Nancy's spreadsheet ingestion via API...")
    
    # Create test file
    filename = create_simple_csv()
    print(f"Created test file: {filename}")
    
    # Wait for Nancy to be ready
    print("Waiting for Nancy API to be ready...")
    for i in range(30):
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("+ Nancy API is ready")
                break
        except requests.exceptions.RequestException:
            pass
        time.sleep(2)
        print(f"  Waiting... ({i+1}/30)")
    else:
        print("✗ Nancy API not responding after 60 seconds")
        return False
    
    # Test file upload
    try:
        with open(filename, 'rb') as f:
            files = {'file': (filename, f, 'text/csv')}
            data = {'author': 'Test Engineer'}
            
            response = requests.post(
                "http://localhost:8000/api/ingest",
                files=files,
                data=data,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            print("✓ CSV file ingested successfully!")
            print(f"  Doc ID: {result.get('doc_id', 'N/A')}")
            print(f"  Status: {result.get('status', 'N/A')}")
            
            if 'sheets_processed' in result:
                print(f"  Sheets processed: {result['sheets_processed']}")
                print(f"  Total rows: {result['total_rows']}")
                print(f"  Total columns: {result['total_columns']}")
            
            return True
        else:
            print(f"✗ Ingestion failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Error during ingestion: {str(e)}")
        return False

def test_query():
    """Test querying the ingested spreadsheet data."""
    print("\nTesting query capabilities...")
    
    queries = [
        "Who are the engineers in the dataset?",
        "What departments are represented?",
        "Who has the most experience?"
    ]
    
    for query in queries:
        try:
            response = requests.post(
                "http://localhost:8000/api/query",
                json={"query": query},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Query: '{query}'")
                print(f"  Answer: {result.get('answer', 'No answer')[:100]}...")
            else:
                print(f"✗ Query failed: {query}")
                print(f"  Status: {response.status_code}")
                
        except Exception as e:
            print(f"✗ Query error: {str(e)}")

if __name__ == "__main__":
    success = test_ingestion()
    if success:
        test_query()
    
    # Cleanup
    import os
    try:
        os.remove('simple_test.csv')
        print("\nCleaned up test file")
    except:
        pass