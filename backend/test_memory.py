#!/usr/bin/env python3
"""
Script para probar el manejo de memoria del sistema
Verifica que los límites de caché funcionen correctamente
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
    """Prueba el endpoint de estadísticas de caché"""
    print_section("📊 Estadísticas de Caché")
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
        print(f"❌ Error conectando al servidor: {e}")
        print("   Asegúrate de que el servidor esté corriendo en http://localhost:8080")
    return None

def test_clear_cache(clear_metrics=False):
    """Prueba el endpoint de limpieza de caché"""
    section_title = "🧹 Limpieza de Caché" + (" (incluyendo métricas)" if clear_metrics else "")
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
    """Hace múltiples requests para llenar los cachés"""
    print_section("🔄 Llenando Cachés con Múltiples Requests")
    
    questions = [
        "Show me the average price per product name",
        "List contracts grouped by province name",
        "Total quantity by product name",
        "Contracts by month and year",
    ]
    
    print(f"Haciendo {len(questions)} requests para llenar cachés...")
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
                print(f"     ✅ {data.get('total_rows', 0)} filas")
            else:
                print(f"     ❌ Error: {response.status_code}")
        except Exception as e:
            print(f"     ❌ Error: {e}")

def test_metrics_limit():
    """Verifica el límite de métricas"""
    print_section("📈 Verificando Límite de Métricas")
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        if response.status_code == 200:
            data = response.json()
            stats = data.get("stats", {})
            total = stats.get("total_requests", 0)
            print(f"Total de requests almacenados: {total}")
            print(f"Límite máximo: 1000")
            if total > 1000:
                print("⚠️  El límite se ha excedido (debería limpiarse automáticamente)")
            else:
                print(f"✅ Dentro del límite ({1000 - total} disponibles)")
        else:
            print(f"❌ Error: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("\n" + "=" * 60)
    print("  🧪 PRUEBA DE MANEJO DE MEMORIA")
    print("=" * 60)
    print("\nEste script prueba:")
    print("  1. Estadísticas de caché")
    print("  2. Limpieza de caché")
    print("  3. Llenado de cachés con múltiples requests")
    print("  4. Verificación de límites de métricas")
    
    # 1. Ver estadísticas iniciales
    initial_stats = test_cache_stats()
    
    # 2. Hacer múltiples requests para llenar cachés
    test_multiple_requests()
    
    # 3. Ver estadísticas después de llenar
    print("\n⏳ Esperando 2 segundos...")
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
    
    print_section("📋 Resumen")
    if initial_stats and final_stats:
        cache_stats = final_stats.get("cache_stats", {})
        print(f"Schemas en caché: {cache_stats.get('schema_cache_size', 0)}/{cache_stats.get('schema_cache_max', 0)}")
        print(f"Dimensiones en caché: {cache_stats.get('dimensions_cache_size', 0)}")
        print(f"Tablas 'no encontradas' en caché: {cache_stats.get('dimensions_not_found_cache_size', 0)}/{cache_stats.get('dimensions_not_found_cache_max', 0)}")
        
        metrics_stats = final_stats.get("metrics_stats", {})
        print(f"Métricas almacenadas: {metrics_stats.get('total_metrics', 0)}/{metrics_stats.get('max_metrics', 0)}")
    
    print("\n✅ Prueba completada")
    print("\n💡 Para probar manualmente:")
    print("   - GET  http://localhost:8080/cache/stats  (ver estadísticas)")
    print("   - POST http://localhost:8080/cache/clear  (limpiar cachés)")
    print("   - GET  http://localhost:8080/metrics    (ver métricas)")

if __name__ == "__main__":
    main()
