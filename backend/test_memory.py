#!/usr/bin/env python3
"""
Script to test system memory management
Verifies that cache limits work correctly
"""
import sys
import os
import requests
import json

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

BASE_URL = "http://localhost:8080"

def print_section(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def test_cache_stats():
    """Tests the cache statistics endpoint"""
    print_section("📊 Cache Statistics")
    try:
        response = requests.get(f"{BASE_URL}/cache/stats")
        if response.status_code == 200:
            stats = response.json()
            print(json.dumps(stats, indent=2))
            return stats
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("   Make sure the server is running at http://localhost:8080")
    return None

def test_clear_cache(clear_metrics=False):
    """Tests the cache cleanup endpoint"""
    section_title = "🧹 Cache Cleanup" + (" (including metrics)" if clear_metrics else "")
    print_section(section_title)
    try:
        url = f"{BASE_URL}/cache/clear"
        if clear_metrics:
            url += "?clear_metrics=true"
        response = requests.post(url)
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Error: {e}")
    return None

def test_multiple_requests():
    """Makes multiple requests to fill the caches"""
    print_section("🔄 Filling Caches with Multiple Requests")
    
    questions = [
        "Show me the average price per product name",
        "List contracts grouped by province name",
        "Total quantity by product name",
        "Contracts by month and year",
    ]
    
    print(f"Making {len(questions)} requests to fill caches...")
    for i, question in enumerate(questions, 1):
        try:
            print(f"  [{i}/{len(questions)}] {question[:50]}...")
            response = requests.post(
                f"{BASE_URL}/ask",
                json={"question": question},
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                print(f"     ✅ {data.get('total_rows', 0)} rows")
            else:
                print(f"     ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"     ❌ Error: {e}")

def test_metrics_limit():
    """Verifies the metrics limit"""
    print_section("📈 Verifying Metrics Limit")
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        if response.status_code == 200:
            data = response.json()
            stats = data.get("stats", {})
            total = stats.get("total_requests", 0)
            print(f"Total stored requests: {total}")
            print(f"Maximum limit: 1000")
            if total > 1000:
                print("⚠️  Limit has been exceeded (should be cleaned automatically)")
            else:
                print(f"✅ Within limit ({1000 - total} available)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "=" * 60)
    print("  🧪 MEMORY MANAGEMENT TEST")
    print("=" * 60)
    print("\nThis script tests:")
    print("  1. Cache statistics")
    print("  2. Cache cleanup")
    print("  3. Filling caches with multiple requests")
    print("  4. Metrics limit verification")
    
    # 1. Ver estadísticas iniciales
    initial_stats = test_cache_stats()
    
    # 2. Hacer múltiples requests para llenar cachés
    test_multiple_requests()
    
    # 3. Ver estadísticas después de llenar
    print("\n⏳ Waiting 2 seconds...")
    import time
    time.sleep(2)
    after_stats = test_cache_stats()
    
    # 4. Verificar métricas
    test_metrics_limit()
    
    # 5. Limpiar cachés (sin métricas)
    test_clear_cache(clear_metrics=False)
    
    # 6. Ver estadísticas después de limpiar cachés
    after_clear_stats = test_cache_stats()
    
    # 7. Limpiar cachés incluyendo métricas
    test_clear_cache(clear_metrics=True)
    
    # 8. Ver estadísticas finales
    final_stats = test_cache_stats()
    
    print_section("📋 Summary")
    if initial_stats and final_stats:
        cache_stats = final_stats.get("cache_stats", {})
        print(f"Cached schemas: {cache_stats.get('schema_cache_size', 0)}/{cache_stats.get('schema_cache_max', 0)}")
        print(f"Cached dimensions: {cache_stats.get('dimensions_cache_size', 0)}")
        print(f"'Not found' tables in cache: {cache_stats.get('dimensions_not_found_cache_size', 0)}/{cache_stats.get('dimensions_not_found_cache_max', 0)}")
        
        metrics_stats = final_stats.get("metrics_stats", {})
        print(f"Stored metrics: {metrics_stats.get('total_metrics', 0)}/{metrics_stats.get('max_metrics', 0)}")
    
    print("\n✅ Test completed")
    print("\n💡 To test manually:")
    print("   - GET  http://localhost:8080/cache/stats  (view statistics)")
    print("   - POST http://localhost:8080/cache/clear  (clear caches)")
    print("   - GET  http://localhost:8080/metrics    (view metrics)")

if __name__ == "__main__":
    main()
