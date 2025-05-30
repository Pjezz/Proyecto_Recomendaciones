#!/usr/bin/env python3
"""
Configuración simplificada para Neo4j (compatible con Python 3.13)
"""

from neo4j import GraphDatabase

class Neo4jSetup:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Limpiar base de datos"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Base de datos limpiada")
    
    def create_sample_data(self):
        """Crear datos de ejemplo simplificados"""
        with self.driver.session() as session:
            # Crear marcas
            brands = ["Toyota", "Honda", "BMW", "Tesla", "Ford"]
            for brand in brands:
                session.run("MERGE (m:Marca {nombre: $nombre})", nombre=brand)
            
            # Crear tipos
            types = ["Sedán", "SUV", "Hatchback", "Pickup", "Coupé"]
            for vehicle_type in types:
                session.run("MERGE (t:Tipo {categoria: $categoria})", categoria=vehicle_type)
            
            # Crear combustibles
            fuels = ["Gasolina", "Diésel", "Eléctrico", "Híbrido"]
            for fuel in fuels:
                session.run("MERGE (c:Combustible {tipo: $tipo})", tipo=fuel)
            
            # Crear transmisiones
            transmissions = ["Automática", "Manual"]
            for transmission in transmissions:
                session.run("MERGE (tr:Transmision {tipo: $tipo})", tipo=transmission)
            
            print("Creados nodos base")
    
    def create_cars(self):
        """Crear autos de ejemplo"""
        cars_data = [
            {"id": "car_1", "modelo": "Corolla", "año": 2024, "precio": 25000, "marca": "Toyota", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_2", "modelo": "Camry", "año": 2024, "precio": 32000, "marca": "Toyota", "tipo": "Sedán", "combustible": "Híbrido", "transmision": "Automática"},
            {"id": "car_3", "modelo": "RAV4", "año": 2024, "precio": 35000, "marca": "Toyota", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            
            {"id": "car_4", "modelo": "Civic", "año": 2024, "precio": 27000, "marca": "Honda", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Manual"},
            {"id": "car_5", "modelo": "Accord", "año": 2024, "precio": 31000, "marca": "Honda", "tipo": "Sedán", "combustible": "Híbrido", "transmision": "Automática"},
            {"id": "car_6", "modelo": "CR-V", "año": 2024, "precio": 36000, "marca": "Honda", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            
            {"id": "car_7", "modelo": "3 Series", "año": 2024, "precio": 45000, "marca": "BMW", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_8", "modelo": "X3", "año": 2024, "precio": 52000, "marca": "BMW", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            
            {"id": "car_9", "modelo": "Model 3", "año": 2024, "precio": 42000, "marca": "Tesla", "tipo": "Sedán", "combustible": "Eléctrico", "transmision": "Automática"},
            {"id": "car_10", "modelo": "Model Y", "año": 2024, "precio": 48000, "marca": "Tesla", "tipo": "SUV", "combustible": "Eléctrico", "transmision": "Automática"},
            
            {"id": "car_11", "modelo": "Mustang", "año": 2024, "precio": 38000, "marca": "Ford", "tipo": "Coupé", "combustible": "Gasolina", "transmision": "Manual"},
            {"id": "car_12", "modelo": "F-150", "año": 2024, "precio": 45000, "marca": "Ford", "tipo": "Pickup", "combustible": "Gasolina", "transmision": "Automática"},
        ]
        
        with self.driver.session() as session:
            for car in cars_data:
                # Crear auto
                session.run("""
                    CREATE (a:Auto {
                        id: $id,
                        modelo: $modelo,
                        año: $año,
                        precio: $precio
                    })
                """, **car)
                
                # Conectar relaciones
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (m:Marca {nombre: $marca})
                    MERGE (a)-[:ES_MARCA]->(m)
                """, id=car["id"], marca=car["marca"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (t:Tipo {categoria: $tipo})
                    MERGE (a)-[:ES_TIPO]->(t)
                """, id=car["id"], tipo=car["tipo"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (c:Combustible {tipo: $combustible})
                    MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                """, id=car["id"], combustible=car["combustible"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (tr:Transmision {tipo: $transmision})
                    MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                """, id=car["id"], transmision=car["transmision"])
        
        print(f"Creados {len(cars_data)} autos")
    
    def setup_database(self):
        """Configurar base de datos completa"""
        print("Configurando base de datos...")
        self.clear_database()
        self.create_sample_data()
        self.create_cars()
        print("¡Configuración completada!")

def test_connections():
    """Probar diferentes configuraciones de conexión"""
    configs = [
        # Configuración específica con tu contraseña
        {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
    ]
    
    for i, config in enumerate(configs, 1):
        print(f"\n{i}. Probando: {config['uri']} con {config['user']}/{config['password']}")
        try:
            setup = Neo4jSetup(config["uri"], config["user"], config["password"])
            
            # Probar consulta simple
            with setup.driver.session() as session:
                result = session.run("RETURN 'Conexión exitosa' as mensaje")
                print(f"   ✓ {result.single()['mensaje']}")
                
                # Configurar base de datos
                setup.setup_database()
                setup.close()
                
                print(f"\n🎉 ¡CONFIGURACIÓN EXITOSA!")
                print(f"Usa esta configuración:")
                print(f"URI = \"{config['uri']}\"")
                print(f"USER = \"{config['user']}\"")
                print(f"PASSWORD = \"{config['password']}\"")
                return True
                
        except Exception as e:
            print(f"   ✗ Error: {e}")
            
    print("\n❌ No se pudo conectar con ninguna configuración")
    return False

def main():
    print("=== CONFIGURACIÓN SIMPLIFICADA DE NEO4J ===")
    
    if not test_connections():
        print("\n🚨 INSTRUCCIONES PARA RESOLVER:")
        print("\n1. Abre Neo4j Desktop")
        print("2. Asegúrate de que tu base de datos esté ACTIVE")
        print("3. Haz clic en 'Open' para abrir Neo4j Browser")
        print("4. En el browser, ejecuta: :server status")
        print("5. Verifica el puerto Bolt (debe ser 7687)")
        print("\n6. Si la contraseña es incorrecta:")
        print("   - En Neo4j Desktop: tu DB → ... → Manage → Settings")
        print("   - Busca 'Change Password' o crea nueva DB")
        print("\n7. Alternativa: Crear nueva base de datos")
        print("   - Neo4j Desktop → New → Create Local Database")
        print("   - Nombre: RecomendacionesAutos")
        print("   - Contraseña: proyectoNEO4J")

if __name__ == "__main__":
    main()