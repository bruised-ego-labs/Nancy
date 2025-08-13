#!/usr/bin/env python3
"""
Data Upload Script for Nancy and Baseline Systems

Uploads benchmark test data to both Nancy and baseline RAG systems
and measures ingestion performance.

Usage: python upload_benchmark_data.py
"""

import requests
import time
import json
import os
import glob
from datetime import datetime

def upload_to_system(system_name: str, base_url: str, test_data_dir: str = "benchmark_test_data") -> dict:
    """Upload test data to a system and measure performance"""
    print(f"📥 Uploading data to {system_name} ({base_url})...")
    
    if not os.path.exists(test_data_dir):
        print(f"❌ Test data directory '{test_data_dir}' not found!")
        return {"status": "error", "error": f"Directory {test_data_dir} not found"}
    
    test_files = glob.glob(os.path.join(test_data_dir, "*.txt"))
    if not test_files:
        print(f"❌ No .txt files found in '{test_data_dir}'!")
        return {"status": "error", "error": f"No test files found in {test_data_dir}"}
    
    print(f"   Found {len(test_files)} test files")
    
    start_time = time.time()
    successful_uploads = 0
    failed_uploads = []
    total_bytes = 0
    
    for file_path in test_files:
        filename = os.path.basename(file_path)
        try:
            print(f"   → Uploading {filename}...", end=" ", flush=True)
            
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = len(content.encode('utf-8'))
            total_bytes += file_size
            
            # Prepare upload
            files = {'file': (filename, content, 'text/plain')}
            data = {'author': 'Benchmark Test User'}
            
            # Upload
            upload_start = time.time()
            response = requests.post(
                f"{base_url}/api/ingest",
                files=files,
                data=data,
                timeout=120
            )
            upload_time = time.time() - upload_start
            
            if response.status_code == 200:
                successful_uploads += 1
                print(f"✓ ({file_size} bytes, {upload_time:.1f}s)")
            else:
                failed_uploads.append({
                    "filename": filename,
                    "error": f"HTTP {response.status_code}: {response.text[:100]}"
                })
                print(f"✗ HTTP {response.status_code}")
                
        except Exception as e:
            failed_uploads.append({
                "filename": filename, 
                "error": str(e)
            })
            print(f"✗ Error: {str(e)[:50]}")
    
    total_time = time.time() - start_time
    upload_speed = (total_bytes / (1024 * 1024)) / total_time if total_time > 0 else 0
    
    result = {
        "status": "completed",
        "system": system_name,
        "total_files": len(test_files),
        "successful_uploads": successful_uploads,
        "failed_uploads": len(failed_uploads),
        "total_bytes": total_bytes,
        "total_time": total_time,
        "upload_speed_mbps": upload_speed,
        "errors": failed_uploads
    }
    
    print(f"   📊 Results: {successful_uploads}/{len(test_files)} files uploaded")
    print(f"      Total: {total_bytes / 1024:.1f} KB in {total_time:.1f}s")
    print(f"      Speed: {upload_speed:.2f} MB/s")
    
    return result

def main():
    """Upload data to both systems"""
    print("🚀 Starting Data Upload to Nancy and Baseline Systems")
    print("=" * 60)
    
    # System URLs
    nancy_url = "http://localhost:8000"
    baseline_url = "http://localhost:8002"
    
    # Check system health first
    print("\n1. Checking system health...")
    try:
        nancy_health = requests.get(f"{nancy_url}/health", timeout=10)
        nancy_status = "✓ Healthy" if nancy_health.status_code == 200 else f"✗ HTTP {nancy_health.status_code}"
    except Exception as e:
        nancy_status = f"✗ Error: {e}"
    
    try:
        baseline_health = requests.get(f"{baseline_url}/health", timeout=10)
        baseline_status = "✓ Healthy" if baseline_health.status_code == 200 else f"✗ HTTP {baseline_health.status_code}"
    except Exception as e:
        baseline_status = f"✗ Error: {e}"
    
    print(f"   Nancy Four-Brain: {nancy_status}")
    print(f"   Baseline RAG: {baseline_status}")
    
    # Upload to both systems
    print("\n2. Uploading data...")
    nancy_result = upload_to_system("Nancy Four-Brain", nancy_url)
    print()
    baseline_result = upload_to_system("Baseline RAG", baseline_url)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 UPLOAD SUMMARY")
    print("=" * 60)
    
    if nancy_result['status'] == 'completed':
        print(f"Nancy Four-Brain:")
        print(f"  Files: {nancy_result['successful_uploads']}/{nancy_result['total_files']}")
        print(f"  Time: {nancy_result['total_time']:.1f}s")
        print(f"  Speed: {nancy_result['upload_speed_mbps']:.2f} MB/s")
    else:
        print(f"Nancy Four-Brain: {nancy_result.get('error', 'Failed')}")
    
    print()
    if baseline_result['status'] == 'completed':
        print(f"Baseline RAG:")
        print(f"  Files: {baseline_result['successful_uploads']}/{baseline_result['total_files']}")
        print(f"  Time: {baseline_result['total_time']:.1f}s") 
        print(f"  Speed: {baseline_result['upload_speed_mbps']:.2f} MB/s")
    else:
        print(f"Baseline RAG: {baseline_result.get('error', 'Failed')}")
    
    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"upload_results_{timestamp}.json"
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "nancy": nancy_result,
        "baseline": baseline_result
    }
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nDetailed results saved to: {filename}")
    
    # Recommendations
    print(f"\n💡 Next Steps:")
    print(f"   1. Wait 30 seconds for systems to process uploaded data")
    print(f"   2. Run benchmark queries: python comprehensive_benchmark_with_metrics.py")
    print(f"   3. Or run existing benchmark: python run_comprehensive_comparison.py")
    
    return results

if __name__ == "__main__":
    main()