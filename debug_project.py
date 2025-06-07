#!/usr/bin/env python3
"""
Script de diagnóstico para verificar la estructura del proyecto
"""

import os
import sys
from pathlib import Path

def check_project_structure():
    """Verificar la estructura del proyecto"""
    print("🔍 DIAGNÓSTICO DEL PROYECTO")
    print("=" * 50)
    
    # Directorio actual
    current_dir = os.getcwd()
    print(f"📁 Directorio actual: {current_dir}")
    
    # Archivos en directorio actual
    print(f"\n📄 Archivos en directorio actual:")
    for item in os.listdir(current_dir):
        if os.path.isfile(item):
            print(f"  ✓ {item}")
        else:
            print(f"  📁 {item}/")
    
    # Verificar archivos críticos
    critical_files = [
        "enhanced_database_setup.py",
        "setup_intelligent_system.py",
        "app/app.py",
        "app/recommender_minimal.py",
        "app/recommender.py"
    ]
    
    print(f"\n🔍 Verificando archivos críticos:")
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - NO ENCONTRADO")
    
    # Verificar directorio app
    app_dir = "app"
    if os.path.exists(app_dir):
        print(f"\n📁 Contenido del directorio {app_dir}:")
        for item in os.listdir(app_dir):
            item_path = os.path.join(app_dir, item)
            if os.path.isfile(item_path):
                print(f"  ✓ {item}")
            else:
                print(f"  📁 {item}/")
        
        # Verificar subdirectorios
        for subdir in ["static", "templates"]:
            subdir_path = os.path.join(app_dir, subdir)
            if os.path.exists(subdir_path):
                print(f"\n📁 Contenido de {subdir_path}:")
                for item in os.listdir(subdir_path):
                    print(f"    ✓ {item}")
            else:
                print(f"  ❌ {subdir_path} - NO ENCONTRADO")
    else:
        print(f"\n❌ Directorio {app_dir} no encontrado")
    
    # Verificar Python y librerías
    print(f"\n🐍 Información de Python:")
    print(f"  Versión: {sys.version}")
    print(f"  Ejecutable: {sys.executable}")
    
    # Verificar librerías necesarias
    required_libs = ["flask", "neo4j", "flask_cors"]
    print(f"\n📚 Verificando librerías:")
    for lib in required_libs:
        try:
            __import__(lib)
            print(f"  ✅ {lib}")
        except ImportError:
            print(f"  ❌ {lib} - NO INSTALADO")
    
    print(f"\n" + "=" * 50)

def create_missing_directories():
    """Crear directorios faltantes"""
    print("🛠️ CREANDO DIRECTORIOS FALTANTES")
    print("=" * 50)
    
    directories = [
        "app",
        "app/static",
        "app/static/js",
        "app/static/css",
        "app/templates"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"  ✅ Creado: {directory}")
        else:
            print(f"  ✓ Existe: {directory}")

def check_neo4j_connection():
    """Verificar conexión a Neo4j"""
    print("🔗 VERIFICANDO CONEXIÓN A NEO4J")
    print("=" * 50)
    
    try:
        from neo4j import GraphDatabase
        
        configs = [
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
        ]
        
        for config in configs:
            try:
                driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
                with driver.session() as session:
                    session.run("RETURN 1")
                print(f"  ✅ Conexión exitosa con password: {config['password']}")
                driver.close()
                return True
            except Exception as e:
                print(f"  ❌ Fallo con password {config['password']}: {e}")
        
        print("  ❌ No se pudo conectar a Neo4j")
        return False
        
    except ImportError:
        print("  ❌ Librería neo4j no instalada")
        return False

def generate_recommendations():
    """Probar generación de recomendaciones"""
    print("🎯 PROBANDO SISTEMA DE RECOMENDACIONES")
    print("=" * 50)
    
    try:
        # Intentar importar el sistema de recomendaciones
        sys.path.append('app')
        
        try:
            from recommender_minimal import get_recommendations
            print("  ✅ Importado recommender_minimal")
        except ImportError:
            try:
                from recommender import get_recommendations
                print("  ✅ Importado recommender")
            except ImportError:
                print("  ❌ No se encontró sistema de recomendaciones")
                return False
        
        # Probar recomendaciones
        recommendations = get_recommendations(
            brands=["Toyota"],
            budget="20000-50000",
            fuel=["Gasolina"],
            types=["Sedán"],
            transmission=["Automática"],
            gender="masculino",
            age_range="26-35"
        )
        
        print(f"  ✅ Generadas {len(recommendations)} recomendaciones")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"    {i}. {rec.get('name', 'N/A')} - ${rec.get('price', 0):,}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error probando recomendaciones: {e}")
        return False

def main():
    """Función principal de diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO DEL PROYECTO")
    print("=" * 60)
    
    # Verificar estructura
    check_project_structure()
    
    print("\n")
    # Crear directorios faltantes
    create_missing_directories()
    
    print("\n")
    # Verificar Neo4j
    neo4j_ok = check_neo4j_connection()
    
    print("\n")
    # Probar recomendaciones
    recommender_ok = generate_recommendations()
    
    print("\n" + "=" * 60)
    print("📋 RESUMEN:")
    print(f"  🔗 Neo4j: {'✅ OK' if neo4j_ok else '❌ PROBLEMA'}")
    print(f"  🎯 Recomendaciones: {'✅ OK' if recommender_ok else '❌ PROBLEMA'}")
    
    if neo4j_ok and recommender_ok:
        print("\n🎉 ¡TODO ESTÁ LISTO!")
        print("Ejecuta: cd app && python app.py")
    else:
        print("\n🔧 PASOS PARA RESOLVER:")
        if not neo4j_ok:
            print("1. Inicia Neo4j Desktop")
            print("2. Verifica la password de la base de datos")
            print("3. Ejecuta: python enhanced_database_setup.py")
        if not recommender_ok:
            print("4. Verifica que recommender_minimal.py esté en app/")
            print("5. Instala librerías: pip install flask neo4j flask-cors")

if __name__ == "__main__":
    main()