#!/usr/bin/env python3
"""
Simple test for Nancy Spreadsheet MCP Server components
Tests processor and Knowledge Packet generation without Unicode issues.
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime
import json

# Add MCP server to path
sys.path.append(str(Path(__file__).parent / "mcp-servers" / "spreadsheet"))

from processor import SpreadsheetProcessor
from server import NancyKnowledgePacket


def create_test_data():
    """Create test spreadsheet data."""
    print("Creating test data...")
    
    # Create test directory
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    # Create engineering test data
    data = {
        'Component_ID': ['COMP_001', 'COMP_002', 'COMP_003'],
        'Component_Name': ['Thermal Sensor', 'Pressure Valve', 'Power Supply'],
        'Temperature_C': [85.2, 42.1, 75.8],
        'Max_Pressure_PSI': [150.0, 500.0, 0.0],
        'Test_Status': ['PASS', 'PASS', 'FAIL'],
        'Cost_USD': [45.20, 120.50, 89.75],
        'Engineering_Domain': ['Thermal', 'Mechanical', 'Electrical']
    }
    
    df = pd.DataFrame(data)
    
    # Save as Excel
    excel_file = test_dir / "test_components.xlsx"
    df.to_excel(excel_file, index=False, engine='openpyxl')
    
    # Save as CSV
    csv_file = test_dir / "test_components.csv"
    df.to_csv(csv_file, index=False)
    
    print(f"Created Excel file: {excel_file}")
    print(f"Created CSV file: {csv_file}")
    
    return str(excel_file), str(csv_file)


def test_processor():
    """Test the spreadsheet processor."""
    print("\nTesting SpreadsheetProcessor...")
    
    processor = SpreadsheetProcessor()
    excel_file, csv_file = create_test_data()
    
    # Test Excel processing
    print("Testing Excel processing...")
    with open(excel_file, 'rb') as f:
        content = f.read()
    
    result = processor.process_spreadsheet(
        Path(excel_file).name, content, "Test Author"
    )
    
    if "error" in result:
        print(f"ERROR: {result['error']}")
        return False
    
    print("SUCCESS: Excel processing completed")
    print(f"  Sheets processed: {result.get('sheets_processed', [])}")
    print(f"  Total rows: {result.get('total_rows', 0)}")
    print(f"  Total columns: {result.get('total_columns', 0)}")
    
    # Check content structure
    content = result.get("content", {})
    vector_data = content.get("vector_data", {})
    analytical_data = content.get("analytical_data", {})
    graph_data = content.get("graph_data", {})
    
    print(f"  Vector chunks: {len(vector_data.get('chunks', []))}")
    print(f"  Analytical tables: {len(analytical_data.get('table_data', []))}")
    print(f"  Graph entities: {len(graph_data.get('entities', []))}")
    
    # Test CSV processing
    print("\nTesting CSV processing...")
    with open(csv_file, 'rb') as f:
        csv_content = f.read()
    
    csv_result = processor.process_spreadsheet(
        Path(csv_file).name, csv_content, "Test Author"
    )
    
    if "error" in csv_result:
        print(f"ERROR: {csv_result['error']}")
        return False
    
    print("SUCCESS: CSV processing completed")
    return True, result


def test_knowledge_packet(processed_data):
    """Test Knowledge Packet generation."""
    print("\nTesting Knowledge Packet generation...")
    
    filename = "test_components.xlsx"
    
    try:
        packet = NancyKnowledgePacket.create_from_spreadsheet_data(
            filename, processed_data
        )
        
        print("SUCCESS: Knowledge Packet created")
        print(f"  Packet ID: {packet['packet_id'][:16]}...")
        print(f"  Source: {packet['source']['mcp_server']}")
        print(f"  Content type: {packet['source']['content_type']}")
        print(f"  Priority brain: {packet['processing_hints'].get('priority_brain')}")
        
        # Validate structure
        required_fields = [
            "packet_version", "packet_id", "timestamp", "source",
            "metadata", "content", "processing_hints", "quality_metrics"
        ]
        
        missing = [field for field in required_fields if field not in packet]
        if missing:
            print(f"ERROR: Missing fields: {missing}")
            return False
        
        print("SUCCESS: Knowledge Packet structure valid")
        return True, packet
        
    except Exception as e:
        print(f"ERROR: Knowledge Packet generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("Nancy Spreadsheet MCP Server Simple Test")
    print("=" * 50)
    
    # Test processor
    processor_result = test_processor()
    if not processor_result:
        print("\nFAILED: Processor test failed")
        return
    
    success, processed_data = processor_result
    if not success:
        print("\nFAILED: Processor returned invalid data")
        return
    
    # Test Knowledge Packet
    packet_result = test_knowledge_packet(processed_data)
    if not packet_result:
        print("\nFAILED: Knowledge Packet test failed")
        return
    
    success, packet = packet_result
    if not success:
        print("\nFAILED: Knowledge Packet generation failed")
        return
    
    # Save test results
    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "test_status": "PASSED",
        "processor_test": "PASSED",
        "knowledge_packet_test": "PASSED",
        "sample_packet_id": packet["packet_id"],
        "sample_content_summary": {
            "vector_chunks": len(packet["content"].get("vector_data", {}).get("chunks", [])),
            "analytical_tables": len(packet["content"].get("analytical_data", {}).get("table_data", [])),
            "graph_entities": len(packet["content"].get("graph_data", {}).get("entities", []))
        }
    }
    
    results_file = Path(__file__).parent / f"mcp_simple_test_results_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n" + "=" * 50)
    print("ALL TESTS PASSED!")
    print("=" * 50)
    print(f"Spreadsheet MCP Server is functional")
    print(f"Results saved to: {results_file}")


if __name__ == "__main__":
    main()