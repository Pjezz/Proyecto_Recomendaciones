#!/usr/bin/env python3
"""
Script para diagnosticar problemas con las recomendaciones
"""

from neo4j import GraphDatabase
import json

def test_neo4j_connection():
    """Probar conexión y contenido de Neo4j"""
    print("=== DIAGNÓSTICO DE NEO4J ===\n")
    
    configs = [
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
    ]
    
    for config in configs:
        try:
            print(f"Probando: {config['uri']} con {config['user']}/{config['password']}")
            driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
            
            with driver.session() as session:
                # Verificar conexión
                result = session.run("RETURN 'Conectado' as status")
                print(f"✓ {result.single()['status']}")
                
                # Contar nodos por tipo
                print("\n--- Contenido de la base de datos ---")
                
                labels = ["Auto", "Marca", "Tipo", "Combustible", "Transmision"]
                for label in labels:
                    count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                    count = count_result.single()["count"]
                    print(f"{label}: {count} nodos")
                
                # Mostrar algunos autos de ejemplo
                print("\n--- Autos disponibles (primeros 5) ---")
                cars_result = session.run("""
                    MATCH (a:Auto)
                    OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                    OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
                    OPTIONAL MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                    OPTIONAL MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                    RETURN a.modelo as modelo, a.precio as precio,
                           m.nombre as marca, t.categoria as tipo,
                           c.tipo as combustible, tr.tipo as transmision
                    LIMIT 5
                """)
                
                for i, record in enumerate(cars_result, 1):
                    print(f"{i}. {record['marca']} {record['modelo']} - ${record['precio']:,}")
                    print(f"   Tipo: {record['tipo']}, Combustible: {record['combustible']}, Transmisión: {record['transmision']}")
                
                # Mostrar marcas disponibles
                print("\n--- Marcas disponibles ---")
                brands_result = session.run("MATCH (m:Marca) RETURN m.nombre as nombre ORDER BY m.nombre")
                brands = [record["nombre"] for record in brands_result]
                print(f"Marcas: {', '.join(brands)}")
                
                # Mostrar tipos disponibles
                print("\n--- Tipos disponibles ---")
                types_result = session.run("MATCH (t:Tipo) RETURN t.categoria as categoria ORDER BY t.categoria")
                types = [record["categoria"] for record in types_result]
                print(f"Tipos: {', '.join(types)}")
                
                # Mostrar combustibles disponibles
                print("\n--- Combustibles disponibles ---")
                fuels_result = session.run("MATCH (c:Combustible) RETURN c.tipo as tipo ORDER BY c.tipo")
                fuels = [record["tipo"] for record in fuels_result]
                print(f"Combustibles: {', '.join(fuels)}")
                
                # Mostrar transmisiones disponibles
                print("\n--- Transmisiones disponibles ---")
                trans_result = session.run("MATCH (tr:Transmision) RETURN tr.tipo as tipo ORDER BY tr.tipo")
                transmissions = [record["tipo"] for record in trans_result]
                print(f"Transmisiones: {', '.join(transmissions)}")
                
            driver.close()
            return True, config
            
        except Exception as e:
            print(f"✗ Error: {e}")
            continue
    
    return False, None

def test_recommendation_function():
    """Probar la función de recomendaciones directamente"""
    print("\n=== PROBANDO FUNCIÓN DE RECOMENDACIONES ===\n")
    
    try:
        # Intentar importar la función
        try:
            from recommender_minimal import get_recommendations
            print("✓ Importado recommender_minimal.get_recommendations")
        except:
            from recommender import get_recommendations
            print("✓ Importado recommender.get_recommendations")
        
        # Prueba 1: Sin filtros
        print("\n--- Prueba 1: Sin filtros ---")
        recs1 = get_recommendations()
        print(f"Resultado: {len(recs1)} recomendaciones")
        if recs1:
            print(f"Primera recomendación: {recs1[0]['name']} - ${recs1[0]['price']:,}")
        
        # Prueba 2: Solo presupuesto
        print("\n--- Prueba 2: Presupuesto 20000-40000 ---")
        recs2 = get_recommendations(budget="20000-40000")
        print(f"Resultado: {len(recs2)} recomendaciones")
        for rec in recs2[:3]:
            print(f"- {rec['name']} - ${rec['price']:,}")
        
        # Prueba 3: Marca específica
        print("\n--- Prueba 3: Marca Toyota ---")
        recs3 = get_recommendations(brands=["Toyota"])
        print(f"Resultado: {len(recs3)} recomendaciones")
        for rec in recs3[:3]:
            print(f"- {rec['name']} - ${rec['price']:,}")
        
        # Prueba 4: Combinación típica de usuario
        print("\n--- Prueba 4: Combinación típica ---")
        recs4 = get_recommendations(
            brands=["Toyota", "Honda"],
            budget="25000-50000",
            fuel="Gasolina",
            types=["Sedán"],
            transmission="Automática"
        )
        print(f"Resultado: {len(recs4)} recomendaciones")
        for rec in recs4[:3]:
            print(f"- {rec['name']} - ${rec['price']:,}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error en función de recomendaciones: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_flask_endpoint():
    """Probar el endpoint de Flask"""
    print("\n=== PROBANDO ENDPOINT DE FLASK ===\n")
    
    try:
        import requests
        
        # Probar endpoint de debug
        try:
            response = requests.get("http://localhost:5000/api/debug/session", timeout=5)
            print(f"✓ Endpoint debug funciona: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Datos de sesión: {data}")
        except Exception as e:
            print(f"✗ No se puede conectar a Flask: {e}")
            print("Asegúrate de que Flask esté corriendo (python app.py)")
            return False
        
        # Simular datos de sesión y probar recomendaciones
        try:
            response = requests.get("http://localhost:5000/api/recommendations", timeout=10)
            print(f"Endpoint recomendaciones: {response.status_code}")
            
            if response.status_code == 200:
                recommendations = response.json()
                print(f"✓ Recibidas {len(recommendations)} recomendaciones")
                if recommendations:
                    print(f"Primera: {recommendations[0].get('name', 'Sin nombre')}")
            else:
                print(f"✗ Error en endpoint: {response.text}")
                
        except Exception as e:
            print(f"✗ Error probando endpoint: {e}")
        
        return True
        
    except ImportError:
        print("⚠️ requests no instalado, no se puede probar Flask")
        print("Instala con: pip install requests")
        return False

def simulate_user_preferences():
    """Simular las preferencias típicas de un usuario"""
    print("\n=== SIMULANDO PREFERENCIAS DE USUARIO ===\n")
    
    # Ejemplos de lo que podría enviar el frontend
    test_cases = [
        {
            "name": "Usuario básico",
            "brands": {"1": "Toyota", "2": "Honda"},
            "budget": "25000-50000",
            "fuel": "gasolina",
            "types": ["sedan"],
            "transmission": "automatic"
        },
        {
            "name": "Usuario premium",
            "brands": {"1": "BMW", "2": "Mercedes"},
            "budget": "50000-100000",
            "fuel": "gasolina",
            "types": ["suv"],
            "transmission": "automatica"
        },
        {
            "name": "Usuario eco",
            "brands": {"1": "Tesla", "2": "Toyota"},
            "budget": "30000-60000",
            "fuel": "electrico",
            "types": ["sedan", "suv"],
            "transmission": "automatica"
        }
    ]
    
    try:
        from recommender_minimal import get_recommendations
    except:
        from recommender import get_recommendations
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        print(f"Preferencias: {test_case}")
        
        recs = get_recommendations(
            brands=test_case["brands"],
            budget=test_case["budget"],
            fuel=test_case["fuel"],
            types=test_case["types"],
            transmission=test_case["transmission"]
        )
        
        print(f"Resultado: {len(recs)} recomendaciones")
        for i, rec in enumerate(recs[:2], 1):
            print(f"{i}. {rec['name']} - ${rec['price']:,}")

def main():
    print("🔍 Diagnóstico completo del sistema de recomendaciones\n")
    
    # 1. Verificar Neo4j
    neo4j_ok, config = test_neo4j_connection()
    
    if not neo4j_ok:
        print("\n❌ Neo4j no está funcionando. Verifica:")
        print("1. Neo4j Desktop está corriendo")
        print("2. Tu base de datos está ACTIVE")
        print("3. La contraseña es correcta")
        return
    
    # 2. Probar función de recomendaciones
    if not test_recommendation_function():
        print("\n❌ La función de recomendaciones tiene problemas")
        return
    
    # 3. Simular casos de uso
    simulate_user_preferences()
    
    # 4. Probar Flask (si está corriendo)
    print("\n" + "="*50)
    print("Para probar Flask:")
    print("1. Ejecuta 'python app.py' en otra terminal")
    print("2. Ve a http://localhost:5000")
    print("3. Completa el flujo de preferencias")
    print("="*50)

if __name__ == "__main__":
    main()