#!/usr/bin/env python3
"""
Direct test of the textify_spreadsheet function to ensure it works correctly
before testing the full baseline RAG system.
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Add the baseline-rag directory to the path so we can import the function
sys.path.append(str(Path(__file__).parent / "baseline-rag"))

def test_textify_function():
    """Test the textify_spreadsheet function directly"""
    
    print("Testing textify_spreadsheet function")
    print("=" * 40)
    
    # Import the functions from main.py
    try:
        from main import textify_spreadsheet, _convert_dataframe_to_sentences
        print("Successfully imported textify functions")
    except ImportError as e:
        print(f"Failed to import functions: {e}")
        return False
    
    # Test with component_requirements.csv
    csv_file = Path("benchmark_data/component_requirements.csv")
    
    if not csv_file.exists():
        print(f"Test file {csv_file} not found")
        return False
    
    print(f"\nTesting with {csv_file.name}...")
    
    try:
        sentences = textify_spreadsheet(csv_file)
        
        print(f"Generated {len(sentences)} sentences from spreadsheet")
        print("\nFirst 5 sentences:")
        for i, sentence in enumerate(sentences[:5], 1):
            print(f"{i}. {sentence}")
        
        print(f"\nLast 3 sentences:")
        for i, sentence in enumerate(sentences[-3:], len(sentences) - 2):
            print(f"{i}. {sentence}")
        
        # Test that sentences contain expected content
        content_text = " ".join(sentences).lower()
        
        expected_terms = [
            "comp-001", "primary cpu", "sarah chen", "performance", 
            "temperature", "thermal", "comp-003", "radio"
        ]
        
        found_terms = []
        for term in expected_terms:
            if term in content_text:
                found_terms.append(term)
        
        print(f"\nContent validation:")
        print(f"Expected terms found: {len(found_terms)}/{len(expected_terms)}")
        print(f"Found terms: {found_terms}")
        
        if len(found_terms) >= len(expected_terms) * 0.7:  # 70% threshold
            print("Content validation passed")
            return True
        else:
            print("Content validation failed - too few expected terms found")
            return False
            
    except Exception as e:
        print(f"Error testing textify function: {e}")
        return False

if __name__ == "__main__":
    success = test_textify_function()
    if success:
        print("\nTextify function test successful!")
    else:
        print("\nTextify function test failed!")