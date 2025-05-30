#!/usr/bin/env python3
"""
Script para migrar datos locales a Neo4j AuraDB
"""

from neo4j import GraphDatabase

# CREDENCIALES DE AURADB
AURA_URI = "neo4j+s://f792028e.databases.neo4j.io"
AURA_USER = "neo4j"
AURA_PASSWORD = "ZFYZYFluMttP9RdkFXkxRbNmGwxd7f74f2Q4u-XiHuA"

# TU BASE LOCAL (prueba diferentes contraseñas)
LOCAL_CONFIGS = [
    {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
    {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
    {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "neo4j"},
]

def test_aura_connection():
    """Probar conexión a AuraDB"""
    print("🔗 Probando conexión a AuraDB...")
    try:
        driver = GraphDatabase.driver(AURA_URI, auth=(AURA_USER, AURA_PASSWORD))
        with driver.session() as session:
            result = session.run("RETURN 'Conexión exitosa a AuraDB' as mensaje")
            message = result.single()["mensaje"]
            print(f"   ✅ {message}")
        driver.close()
        return True
    except Exception as e:
        print(f"   ❌ Error conectando a AuraDB: {e}")
        return False

def find_local_database():
    """Encontrar tu base de datos local"""
    print("🔍 Buscando tu base de datos local...")
    
    for config in LOCAL_CONFIGS:
        try:
            print(f"   Probando: {config['password']}")
            driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
            
            with driver.session() as session:
                result = session.run("MATCH (a:Auto) RETURN count(a) as total")
                total = result.single()["total"]
                
                if total > 0:
                    print(f"   ✅ Encontrada! {total} autos en la base local")
                    driver.close()
                    return config
                else:
                    print(f"   ⚠️ Conecta pero sin autos")
            
            driver.close()
            
        except Exception as e:
            print(f"   ❌ Error con {config['password']}: {e}")
    
    return None

def export_from_local(config):
    """Obtener todos los datos de tu base local"""
    print("📤 Exportando datos de tu base local...")
    
    driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
    
    with driver.session() as session:
        # Obtener todos los autos con sus relaciones
        result = session.run("""
            MATCH (a:Auto)
            OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
            OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
            OPTIONAL MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            OPTIONAL MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            RETURN a.id as id, a.modelo as modelo, a.año as año, 
                   a.precio as precio, a.caracteristicas as caracteristicas,
                   m.nombre as marca, t.categoria as tipo, 
                   c.tipo as combustible, tr.tipo as transmision
            ORDER BY a.id
        """)
        
        cars = []
        for record in result:
            car = {
                'id': record['id'],
                'modelo': record['modelo'],
                'año': record['año'],
                'precio': record['precio'],
                'caracteristicas': record['caracteristicas'] or [],
                'marca': record['marca'],
                'tipo': record['tipo'],
                'combustible': record['combustible'],
                'transmision': record['transmision']
            }
            cars.append(car)
        
        # Obtener marcas únicas
        brands_result = session.run("MATCH (m:Marca) RETURN DISTINCT m.nombre as nombre ORDER BY m.nombre")
        brands = [record['nombre'] for record in brands_result]
        
        # Obtener tipos únicos
        types_result = session.run("MATCH (t:Tipo) RETURN DISTINCT t.categoria as categoria ORDER BY t.categoria")
        types = [record['categoria'] for record in types_result]
        
        # Obtener combustibles únicos
        fuels_result = session.run("MATCH (c:Combustible) RETURN DISTINCT c.tipo as tipo ORDER BY c.tipo")
        fuels = [record['tipo'] for record in fuels_result]
        
        # Obtener transmisiones únicas
        trans_result = session.run("MATCH (tr:Transmision) RETURN DISTINCT tr.tipo as tipo ORDER BY tr.tipo")
        transmissions = [record['tipo'] for record in trans_result]
        
        print(f"   ✅ Exportados:")
        print(f"      🚗 {len(cars)} autos")
        print(f"      🏷️ {len(brands)} marcas: {', '.join(brands[:5])}{'...' if len(brands) > 5 else ''}")
        print(f"      📦 {len(types)} tipos: {', '.join(types)}")
        print(f"      ⛽ {len(fuels)} combustibles: {', '.join(fuels)}")
        print(f"      ⚙️ {len(transmissions)} transmisiones: {', '.join(transmissions)}")
        
        driver.close()
        return {
            'cars': cars,
            'brands': brands,
            'types': types,
            'fuels': fuels,
            'transmissions': transmissions
        }

def import_to_aura(data):
    """Importar datos a AuraDB"""
    print("📥 Importando datos a AuraDB...")
    
    driver = GraphDatabase.driver(AURA_URI, auth=(AURA_USER, AURA_PASSWORD))
    
    try:
        with driver.session() as session:
            # Limpiar AuraDB
            session.run("MATCH (n) DETACH DELETE n")
            print("   🧹 AuraDB limpiada")
            
            # Crear marcas
            for brand in data['brands']:
                session.run("CREATE (m:Marca {nombre: $nombre})", nombre=brand)
            print(f"   🏷️ Creadas {len(data['brands'])} marcas")
            
            # Crear tipos
            for vehicle_type in data['types']:
                session.run("CREATE (t:Tipo {categoria: $categoria})", categoria=vehicle_type)
            print(f"   📦 Creados {len(data['types'])} tipos")
            
            # Crear combustibles
            for fuel in data['fuels']:
                session.run("CREATE (c:Combustible {tipo: $tipo})", tipo=fuel)
            print(f"   ⛽ Creados {len(data['fuels'])} combustibles")
            
            # Crear transmisiones
            for transmission in data['transmissions']:
                session.run("CREATE (tr:Transmision {tipo: $tipo})", tipo=transmission)
            print(f"   ⚙️ Creadas {len(data['transmissions'])} transmisiones")
            
            # Crear autos con progreso
            print(f"   🚗 Creando {len(data['cars'])} autos...")
            for i, car in enumerate(data['cars'], 1):
                if i % 10 == 0 or i == len(data['cars']):
                    print(f"      Progreso: {i}/{len(data['cars'])} autos")
                
                # Crear auto
                session.run("""
                    CREATE (a:Auto {
                        id: $id,
                        modelo: $modelo,
                        año: $año,
                        precio: $precio,
                        caracteristicas: $caracteristicas
                    })
                """, **car)
                
                # Crear relaciones
                if car['marca']:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MATCH (m:Marca {nombre: $marca})
                        MERGE (a)-[:ES_MARCA]->(m)
                    """, id=car['id'], marca=car['marca'])
                
                if car['tipo']:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MATCH (t:Tipo {categoria: $tipo})
                        MERGE (a)-[:ES_TIPO]->(t)
                    """, id=car['id'], tipo=car['tipo'])
                
                if car['combustible']:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MATCH (c:Combustible {tipo: $combustible})
                        MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                    """, id=car['id'], combustible=car['combustible'])
                
                if car['transmision']:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MATCH (tr:Transmision {tipo: $transmision})
                        MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                    """, id=car['id'], transmision=car['transmision'])
            
            # Verificar resultado final
            result = session.run("""
                MATCH (a:Auto) 
                OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                RETURN count(a) as total_autos, count(DISTINCT m.nombre) as marcas_conectadas
            """)
            stats = result.single()
            
            print(f"   ✅ Verificación final:")
            print(f"      🚗 {stats['total_autos']} autos importados")
            print(f"      🔗 {stats['marcas_conectadas']} marcas conectadas")
            
    finally:
        driver.close()

def test_aura_queries():
    """Probar que las consultas funcionen en AuraDB"""
    print("🧪 Probando consultas en AuraDB...")
    
    driver = GraphDatabase.driver(AURA_URI, auth=(AURA_USER, AURA_PASSWORD))
    
    try:
        with driver.session() as session:
            # Prueba 1: Contar autos por marca
            result = session.run("""
                MATCH (a:Auto)-[:ES_MARCA]->(m:Marca {nombre: 'Toyota'})
                RETURN count(a) as total
            """)
            toyota_count = result.single()["total"]
            print(f"   📊 Autos Toyota: {toyota_count}")
            
            # Prueba 2: Consulta compleja como la del sistema
            result = session.run("""
                MATCH (a:Auto)
                WHERE a.precio >= 20000 AND a.precio <= 50000
                OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
                RETURN a.modelo as modelo, a.precio as precio, 
                       m.nombre as marca, t.categoria as tipo
                LIMIT 3
            """)
            
            print("   🎯 Muestra de consulta:")
            for record in result:
                print(f"      - {record['marca']} {record['modelo']} (${record['precio']:,}) - {record['tipo']}")
            
            print("   ✅ Consultas funcionando correctamente")
            
    finally:
        driver.close()

def main():
    print("🚀 MIGRACIÓN A NEO4J AURADB")
    print("=" * 60)
    print("🎯 Migrando tu base de datos a la nube...")
    print()
    
    try:
        # Paso 1: Verificar AuraDB
        if not test_aura_connection():
            print("❌ No se puede conectar a AuraDB. Verifica las credenciales.")
            return
        
        # Paso 2: Encontrar base local
        local_config = find_local_database()
        if not local_config:
            print("❌ No se encontró tu base de datos local.")
            print("💡 Asegúrate de que Neo4j Desktop esté corriendo y tu base activa.")
            return
        
        # Paso 3: Exportar datos
        data = export_from_local(local_config)
        if not data['cars']:
            print("❌ No se encontraron autos para migrar.")
            return
        
        # Paso 4: Importar a AuraDB
        import_to_aura(data)
        
        # Paso 5: Verificar funcionamiento
        test_aura_queries()
        
        print("\n" + "=" * 60)
        print("🎉 ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
        print("=" * 60)
        print("✅ Tu base de datos ya está en la nube")
        print("✅ Accesible desde cualquier lugar")
        print("✅ Cero configuración para usuarios")
        print()
        print("🔄 SIGUIENTE PASO:")
        print("Ejecuta: python update_code_for_aura.py")
        print("(Para actualizar tu código y usar AuraDB)")
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 Si el problema persiste:")
        print("1. Verifica que Neo4j Desktop esté corriendo")
        print("2. Verifica que tu base local tenga datos")
        print("3. Verifica las credenciales de AuraDB")

if __name__ == "__main__":
    main()