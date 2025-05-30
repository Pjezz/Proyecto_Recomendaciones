#!/usr/bin/env python3
"""
Script para diagnosticar y resolver problemas de conexión con Neo4j
"""

from neo4j import GraphDatabase
import socket

def test_port(host, port):
    """Probar si un puerto está abierto"""
    try:
        socket.create_connection((host, port), timeout=5)
        return True
    except:
        return False

def test_neo4j_connection():
    """Probar diferentes configuraciones de conexión a Neo4j"""
    
    print("=== DIAGNÓSTICO DE CONEXIÓN NEO4J ===\n")
    
    # Puertos comunes de Neo4j
    ports_to_test = [7687, 7474, 11003, 11005]
    
    print("1. Probando puertos:")
    for port in ports_to_test:
        is_open = test_port("localhost", port)
        status = "✓ ABIERTO" if is_open else "✗ CERRADO"
        print(f"   Puerto {port}: {status}")
    
    print("\n2. Probando configuraciones de conexión:")
    
    # Configuraciones comunes
    configs = [
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "neo4j"},
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "password"},
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "admin"},
        {"uri": "neo4j://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
        {"uri": "bolt://localhost:11003", "user": "neo4j", "password": "proyectoNEO4J"},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n   Configuración {i}:")
        print(f"   URI: {config['uri']}")
        print(f"   Usuario: {config['user']}")
        print(f"   Contraseña: {config['password']}")
        
        try:
            driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
            
            with driver.session() as session:
                result = session.run("RETURN 'Conexión exitosa' as mensaje")
                message = result.single()["mensaje"]
                print(f"   Resultado: ✓ {message}")
                
                # Si la conexión es exitosa, obtener más información
                version_result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version")
                for record in version_result:
                    print(f"   Neo4j: {record['name']} {record['version']}")
                
                driver.close()
                print(f"\n🎉 ¡CONEXIÓN EXITOSA!")
                print(f"📝 Usa esta configuración en tu código:")
                print(f"    URI = \"{config['uri']}\"")
                print(f"    USER = \"{config['user']}\"")
                print(f"    PASSWORD = \"{config['password']}\"")
                return config
                
        except Exception as e:
            error_msg = str(e)
            if "authentication failure" in error_msg.lower():
                print("   Resultado: ✗ Credenciales incorrectas")
            elif "connection refused" in error_msg.lower():
                print("   Resultado: ✗ No se puede conectar (puerto cerrado)")
            elif "unable to retrieve routing information" in error_msg.lower():
                print("   Resultado: ✗ Protocolo incorrecto (prueba bolt:// en lugar de neo4j://)")
            else:
                print(f"   Resultado: ✗ Error: {error_msg}")
    
    print("\n❌ No se pudo establecer conexión con ninguna configuración")
    return None

def get_neo4j_info_from_browser():
    """Instrucciones para obtener información desde Neo4j Browser"""
    print("\n=== CÓMO OBTENER INFORMACIÓN DE NEO4J DESKTOP ===")
    print("\n1. Abre Neo4j Desktop")
    print("2. Busca tu base de datos y haz clic en 'Open'")
    print("3. En Neo4j Browser, ejecuta estos comandos:")
    print("\n   :server status")
    print("   (Te mostrará información del servidor)")
    print("\n   :server connect")
    print("   (Te mostrará detalles de conexión)")
    print("\n   CALL dbms.components() YIELD name, versions")
    print("   (Te mostrará versión de Neo4j)")
    print("\n4. Busca información como:")
    print("   - Bolt URL (usualmente bolt://localhost:7687)")
    print("   - Usuario (por defecto: neo4j)")
    print("   - Contraseña (la que configuraste)")

def reset_neo4j_password():
    """Instrucciones para resetear la contraseña de Neo4j"""
    print("\n=== CÓMO RESETEAR LA CONTRASEÑA DE NEO4J ===")
    print("\n📋 Método 1 - Desde Neo4j Desktop:")
    print("1. Abre Neo4j Desktop")
    print("2. Ve a tu base de datos")
    print("3. Haz clic en los 3 puntos (...) junto a 'Open'")
    print("4. Selecciona 'Manage'")
    print("5. Ve a la pestaña 'Settings'")
    print("6. Busca 'Reset Database' o 'Change Password'")
    
    print("\n📋 Método 2 - Crear nueva base de datos:")
    print("1. En Neo4j Desktop, haz clic en 'New'")
    print("2. Selecciona 'Create a Local Database'")
    print("3. Ponle un nombre (ej: 'RecomendacionesAutos')")
    print("4. Establece contraseña: 'proyectoNEO4J'")
    print("5. Haz clic en 'Create'")
    print("6. Inicia la base de datos")
    
    print("\n📋 Método 3 - Desde línea de comandos:")
    print("1. Detén Neo4j")
    print("2. Ve a la carpeta de instalación de Neo4j")
    print("3. Ejecuta: bin/neo4j-admin set-initial-password proyectoNEO4J")
    print("4. Reinicia Neo4j")

def main():
    print("🔍 Diagnóstico de conexión Neo4j\n")
    
    # Probar conexiones
    successful_config = test_neo4j_connection()
    
    if not successful_config:
        print("\n🚨 No se pudo conectar. Aquí hay algunas soluciones:\n")
        
        # Mostrar información sobre cómo obtener datos de Neo4j
        get_neo4j_info_from_browser()
        
        # Mostrar cómo resetear contraseña
        reset_neo4j_password()
        
        print("\n💡 SOLUCIONES COMUNES:")
        print("\n1. Verifica que Neo4j Desktop esté corriendo:")
        print("   - Abre Neo4j Desktop")
        print("   - Asegúrate de que tu base de datos tenga estado 'ACTIVE'")
        print("   - Si dice 'STOPPED', haz clic en 'Start'")
        
        print("\n2. Verifica el puerto:")
        print("   - El puerto por defecto para Bolt es 7687")
        print("   - En Neo4j Browser ejecuta: :server status")
        
        print("\n3. Verifica las credenciales:")
        print("   - Usuario por defecto: neo4j")
        print("   - Contraseña: la que configuraste al crear la DB")
        
        print("\n4. Si nada funciona, crea una nueva base de datos:")
        print("   - En Neo4j Desktop: New → Create a Local Database")
        print("   - Nombre: RecomendacionesAutos")
        print("   - Contraseña: proyectoNEO4J")

if __name__ == "__main__":
    main()