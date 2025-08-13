#!/usr/bin/env python3
"""
Benchmark Runner for Nancy Three-Brain Architecture
Demonstrates the benefits of multi-database RAG over standard vector-only RAG
"""

import os
import sys
import json
from datetime import datetime

# Add the nancy-services directory to Python path
nancy_services_path = os.path.join(os.path.dirname(__file__), 'nancy-services')
sys.path.insert(0, nancy_services_path)

from core.benchmark_framework import MultidisciplinaryBenchmark

def setup_test_data():
    """Ensure test data is ingested into the three-brain system"""
    from core.ingestion import IngestionService
    
    ingestion = IngestionService()
    test_data_dir = "benchmark_test_data"
    
    # Test documents with their authors (representing different team members)
    test_files = [
        ("system_requirements_v2.txt", "Sarah Chen"),
        ("thermal_constraints_doc.txt", "Sarah Chen"), 
        ("electrical_review_meeting.txt", "Mike Rodriguez"),
        ("emc_test_results.txt", "Mike Rodriguez"),
        ("voice_of_customer.txt", "Lisa Park"),
        ("march_design_review_transcript.txt", "Jennifer Adams"),
        ("ergonomic_analysis.txt", "Lisa Park")
    ]
    
    print("Setting up test data...")
    ingestion_results = []
    
    for filename, author in test_files:
        filepath = os.path.join(test_data_dir, filename)
        
        if os.path.exists(filepath):
            print(f"Ingesting {filename} by {author}...")
            
            with open(filepath, 'rb') as f:
                content = f.read()
            
            result = ingestion.ingest_file(filename, content, author)
            ingestion_results.append(result)
            
            if "error" in result:
                print(f"Error ingesting {filename}: {result['error']}")
            else:
                print(f"Successfully ingested {filename}")
        else:
            print(f"Warning: {filepath} not found")
    
    print(f"Ingested {len([r for r in ingestion_results if 'error' not in r])} documents successfully")
    return ingestion_results

def run_benchmark():
    """Execute the comprehensive benchmark comparison"""
    print("\n" + "="*60)
    print("NANCY THREE-BRAIN ARCHITECTURE BENCHMARK")
    print("Multidisciplinary Engineering Team Evaluation")
    print("="*60)
    
    # Setup test data
    setup_results = setup_test_data()
    
    # Initialize and run benchmark
    benchmark = MultidisciplinaryBenchmark()
    
    print("\nRunning comprehensive benchmark...")
    print("This will test both Three-Brain and Standard RAG systems")
    print("-" * 60)
    
    results = benchmark.run_full_benchmark()
    
    # Save results with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_filename = f"benchmark_results_{timestamp}.json"
    
    benchmark.save_results(results, results_filename)
    
    return results, results_filename

def print_summary_report(results):
    """Print a formatted summary of benchmark results"""
    print("\n" + "="*60)
    print("BENCHMARK RESULTS SUMMARY")
    print("="*60)
    
    tb_metrics = results['three_brain_metrics']
    sr_metrics = results['standard_rag_metrics']
    
    print(f"\nOVERALL PERFORMANCE COMPARISON")
    print("-" * 40)
    print(f"{'Metric':<25} {'Three-Brain':<12} {'Standard RAG':<12} {'Improvement'}")
    print("-" * 65)
    
    # Calculate improvements
    precision_imp = ((tb_metrics['avg_precision'] - sr_metrics['avg_precision']) / sr_metrics['avg_precision'] * 100) if sr_metrics['avg_precision'] > 0 else 0
    recall_imp = ((tb_metrics['avg_recall'] - sr_metrics['avg_recall']) / sr_metrics['avg_recall'] * 100) if sr_metrics['avg_recall'] > 0 else 0
    f1_imp = ((tb_metrics['avg_f1'] - sr_metrics['avg_f1']) / sr_metrics['avg_f1'] * 100) if sr_metrics['avg_f1'] > 0 else 0
    mrr_imp = ((tb_metrics['avg_mrr'] - sr_metrics['avg_mrr']) / sr_metrics['avg_mrr'] * 100) if sr_metrics['avg_mrr'] > 0 else 0
    
    print(f"{'Precision@10':<25} {tb_metrics['avg_precision']:<12.3f} {sr_metrics['avg_precision']:<12.3f} {precision_imp:+.1f}%")
    print(f"{'Recall@10':<25} {tb_metrics['avg_recall']:<12.3f} {sr_metrics['avg_recall']:<12.3f} {recall_imp:+.1f}%")
    print(f"{'F1 Score':<25} {tb_metrics['avg_f1']:<12.3f} {sr_metrics['avg_f1']:<12.3f} {f1_imp:+.1f}%")
    print(f"{'Mean Reciprocal Rank':<25} {tb_metrics['avg_mrr']:<12.3f} {sr_metrics['avg_mrr']:<12.3f} {mrr_imp:+.1f}%")
    print(f"{'Author Attribution':<25} {tb_metrics['author_attribution_accuracy']:<12.3f} {'N/A':<12} {tb_metrics['author_attribution_accuracy']*100:.1f}%")
    
    print(f"\nDISCIPLINE-SPECIFIC ANALYSIS")
    print("-" * 40)
    
    discipline_results = results['discipline_analysis']
    
    for discipline, data in discipline_results.items():
        if discipline == 'cross_disciplinary':
            discipline_name = "Cross-Disciplinary"
        else:
            discipline_name = discipline.replace('_', ' ').title()
        
        print(f"\n{discipline_name}:")
        tb_f1 = data['three_brain']['avg_f1']
        sr_f1 = data['standard_rag']['avg_f1']
        improvement = data['improvement_factors']['f1_improvement'] * 100 if 'f1_improvement' in data['improvement_factors'] else 0
        
        print(f"  F1 Score: {tb_f1:.3f} vs {sr_f1:.3f} ({improvement:+.1f}% improvement)")
        
        if 'author_attribution_advantage' in data['improvement_factors']:
            auth_adv = data['improvement_factors']['author_attribution_advantage'] * 100
            print(f"  Author Attribution: {auth_adv:.1f}% success rate")
    
    print(f"\nKEY INSIGHTS")
    print("-" * 40)
    print("• Three-Brain architecture excels at queries requiring:")
    print("  - Author attribution and accountability tracking")
    print("  - Cross-disciplinary relationship discovery")
    print("  - Metadata-filtered searches (time, file type, etc.)")
    print("  - Complex queries combining semantic + structured data")
    print()
    print("• Standard RAG limitations:")
    print("  - No author/relationship information")
    print("  - Cannot filter by metadata")
    print("  - Limited context beyond text similarity")
    print("  - Poor performance on accountability questions")

def main():
    """Main benchmark execution"""
    try:
        results, filename = run_benchmark()
        print_summary_report(results)
        
        print(f"\nDetailed results saved to: {filename}")
        print("\nBenchmark completed successfully!")
        
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())