#!/usr/bin/env python3
"""
Script para configurar la base de datos Neo4j con el esquema completo
y poblarla con datos de ejemplo para el sistema de recomendaciones de autos
"""

from neo4j import GraphDatabase
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jSetup:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Limpiar toda la base de datos"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Base de datos limpiada")
    
    def create_constraints(self):
        """Crear índices y restricciones para mejor rendimiento"""
        constraints = [
            "CREATE CONSTRAINT auto_id IF NOT EXISTS FOR (a:Auto) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT marca_nombre IF NOT EXISTS FOR (m:Marca) REQUIRE m.nombre IS UNIQUE",
            "CREATE CONSTRAINT tipo_categoria IF NOT EXISTS FOR (t:Tipo) REQUIRE t.categoria IS UNIQUE",
            "CREATE CONSTRAINT combustible_tipo IF NOT EXISTS FOR (c:Combustible) REQUIRE c.tipo IS UNIQUE",
            "CREATE CONSTRAINT transmision_tipo IF NOT EXISTS FOR (tr:Transmision) REQUIRE tr.tipo IS UNIQUE",
            "CREATE INDEX auto_precio IF NOT EXISTS FOR (a:Auto) ON (a.precio)",
            "CREATE INDEX auto_año IF NOT EXISTS FOR (a:Auto) ON (a.año)"
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Creada restricción: {constraint.split()[1]}")
                except Exception as e:
                    logger.warning(f"Restricción ya existe o error: {e}")
    
    def create_brands(self):
        """Crear nodos de marcas"""
        brands = [
            "Toyota", "Honda", "Ford", "BMW", "Mercedes-Benz", "Audi", 
            "Volkswagen", "Nissan", "Hyundai", "Kia", "Mazda", "Subaru",
            "Chevrolet", "Tesla", "Lexus", "Porsche", "Ferrari", "Lamborghini",
            "Jaguar", "Land Rover", "Volvo", "Peugeot", "Renault", "Mitsubishi"
        ]
        
        with self.driver.session() as session:
            for brand in brands:
                session.run(
                    "MERGE (m:Marca {nombre: $nombre})",
                    nombre=brand
                )
            logger.info(f"Creadas {len(brands)} marcas")
    
    def create_types(self):
        """Crear nodos de tipos de vehículo"""
        types = [
            "Sedán", "SUV", "Hatchback", "Pickup", "Coupé", "Convertible",
            "Van", "Wagon", "Crossover", "Minivan", "Deportivo", "Lujo"
        ]
        
        with self.driver.session() as session:
            for vehicle_type in types:
                session.run(
                    "MERGE (t:Tipo {categoria: $categoria})",
                    categoria=vehicle_type
                )
            logger.info(f"Creados {len(types)} tipos de vehículo")
    
    def create_fuels(self):
        """Crear nodos de tipos de combustible"""
        fuels = ["Gasolina", "Diésel", "Eléctrico", "Híbrido", "Gas Natural"]
        
        with self.driver.session() as session:
            for fuel in fuels:
                session.run(
                    "MERGE (c:Combustible {tipo: $tipo})",
                    tipo=fuel
                )
            logger.info(f"Creados {len(fuels)} tipos de combustible")
    
    def create_transmissions(self):
        """Crear nodos de transmisiones"""
        transmissions = ["Automática", "Manual", "Semiautomática"]
        
        with self.driver.session() as session:
            for transmission in transmissions:
                session.run(
                    "MERGE (tr:Transmision {tipo: $tipo})",
                    tipo=transmission
                )
            logger.info(f"Creadas {len(transmissions)} transmisiones")
    
    def create_cars(self):
        """Crear nodos de autos con datos realistas"""
        cars_data = [
            # Toyota
            {"id": "car_1", "modelo": "Corolla", "año": 2024, "precio": 25000, "marca": "Toyota", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_2", "modelo": "Camry", "año": 2024, "precio": 30000, "marca": "Toyota", "tipo": "Sedán", "combustible": "Híbrido", "transmision": "Automática"},
            {"id": "car_3", "modelo": "RAV4", "año": 2024, "precio": 35000, "marca": "Toyota", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_4", "modelo": "Highlander", "año": 2024, "precio": 40000, "marca": "Toyota", "tipo": "SUV", "combustible": "Híbrido", "transmision": "Automática"},
            
            # Honda
            {"id": "car_5", "modelo": "Civic", "año": 2024, "precio": 27000, "marca": "Honda", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Manual"},
            {"id": "car_6", "modelo": "Accord", "año": 2024, "precio": 32000, "marca": "Honda", "tipo": "Sedán", "combustible": "Híbrido", "transmision": "Automática"},
            {"id": "car_7", "modelo": "CR-V", "año": 2024, "precio": 36000, "marca": "Honda", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_8", "modelo": "Pilot", "año": 2024, "precio": 42000, "marca": "Honda", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            
            # BMW
            {"id": "car_9", "modelo": "3 Series", "año": 2024, "precio": 45000, "marca": "BMW", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_10", "modelo": "5 Series", "año": 2024, "precio": 55000, "marca": "BMW", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_11", "modelo": "X3", "año": 2024, "precio": 50000, "marca": "BMW", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_12", "modelo": "X5", "año": 2024, "precio": 65000, "marca": "BMW", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            
            # Tesla
            {"id": "car_13", "modelo": "Model 3", "año": 2024, "precio": 42000, "marca": "Tesla", "tipo": "Sedán", "combustible": "Eléctrico", "transmision": "Automática"},
            {"id": "car_14", "modelo": "Model S", "año": 2024, "precio": 75000, "marca": "Tesla", "tipo": "Sedán", "combustible": "Eléctrico", "transmision": "Automática"},
            {"id": "car_15", "modelo": "Model Y", "año": 2024, "precio": 48000, "marca": "Tesla", "tipo": "SUV", "combustible": "Eléctrico", "transmision": "Automática"},
            {"id": "car_16", "modelo": "Model X", "año": 2024, "precio": 85000, "marca": "Tesla", "tipo": "SUV", "combustible": "Eléctrico", "transmision": "Automática"},
            
            # Ford
            {"id": "car_17", "modelo": "Fusion", "año": 2024, "precio": 28000, "marca": "Ford", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_18", "modelo": "Mustang", "año": 2024, "precio": 38000, "marca": "Ford", "tipo": "Coupé", "combustible": "Gasolina", "transmision": "Manual"},
            {"id": "car_19", "modelo": "Explorer", "año": 2024, "precio": 40000, "marca": "Ford", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_20", "modelo": "F-150", "año": 2024, "precio": 45000, "marca": "Ford", "tipo": "Pickup", "combustible": "Gasolina", "transmision": "Automática"},
            
            # Autos económicos
            {"id": "car_21", "modelo": "Elantra", "año": 2024, "precio": 22000, "marca": "Hyundai", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Manual"},
            {"id": "car_22", "modelo": "Tucson", "año": 2024, "precio": 28000, "marca": "Hyundai", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_23", "modelo": "Forte", "año": 2024, "precio": 20000, "marca": "Kia", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Manual"},
            {"id": "car_24", "modelo": "Sportage", "año": 2024, "precio": 26000, "marca": "Kia", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            
            # Autos de lujo
            {"id": "car_25", "modelo": "C-Class", "año": 2024, "precio": 48000, "marca": "Mercedes-Benz", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_26", "modelo": "GLC", "año": 2024, "precio": 55000, "marca": "Mercedes-Benz", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_27", "modelo": "A4", "año": 2024, "precio": 42000, "marca": "Audi", "tipo": "Sedán", "combustible": "Gasolina", "transmision": "Automática"},
            {"id": "car_28", "modelo": "Q5", "año": 2024, "precio": 50000, "marca": "Audi", "tipo": "SUV", "combustible": "Gasolina", "transmision": "Automática"},
        ]
        
        with self.driver.session() as session:
            for car in cars_data:
                # Crear el auto
                session.run("""
                    CREATE (a:Auto {
                        id: $id,
                        modelo: $modelo,
                        año: $año,
                        precio: $precio
                    })
                """, **car)
                
                # Conectar con marca
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (m:Marca {nombre: $marca})
                    MERGE (a)-[:ES_MARCA]->(m)
                """, id=car["id"], marca=car["marca"])
                
                # Conectar con tipo
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (t:Tipo {categoria: $tipo})
                    MERGE (a)-[:ES_TIPO]->(t)
                """, id=car["id"], tipo=car["tipo"])
                
                # Conectar con combustible
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (c:Combustible {tipo: $combustible})
                    MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                """, id=car["id"], combustible=car["combustible"])
                
                # Conectar con transmisión
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (tr:Transmision {tipo: $transmision})
                    MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                """, id=car["id"], transmision=car["transmision"])
        
        logger.info(f"Creados {len(cars_data)} autos con sus relaciones")
    
    def add_car_features(self):
        """Agregar características adicionales a los autos"""
        features_data = [
            {"car_id": "car_1", "features": ["Aire acondicionado", "Radio AM/FM", "Bluetooth", "Cámara trasera"]},
            {"car_id": "car_2", "features": ["Aire acondicionado", "Sistema de navegación", "Bluetooth", "Sensores de estacionamiento", "Pantalla táctil"]},
            {"car_id": "car_13", "features": ["Piloto automático", "Pantalla táctil 15\"", "Supercargador", "Actualización OTA"]},
            {"car_id": "car_18", "features": ["Motor V8", "Asientos deportivos", "Sistema de escape deportivo", "Llantas de aleación"]},
            {"car_id": "car_25", "features": ["Asientos de cuero", "Techo panorámico", "Sistema de sonido premium", "Asistente de estacionamiento"]},
        ]
        
        with self.driver.session() as session:
            for feature_data in features_data:
                session.run("""
                    MATCH (a:Auto {id: $car_id})
                    SET a.caracteristicas = $features
                """, car_id=feature_data["car_id"], features=feature_data["features"])
        
        logger.info("Agregadas características a los autos")
    
    def setup_complete_database(self):
        """Configurar completamente la base de datos"""
        logger.info("Iniciando configuración de base de datos Neo4j...")
        
        # Limpiar base de datos existente
        self.clear_database()
        
        # Crear restricciones e índices
        self.create_constraints()
        
        # Crear nodos base
        self.create_brands()
        self.create_types()
        self.create_fuels()
        self.create_transmissions()
        
        # Crear autos y sus relaciones
        self.create_cars()
        self.add_car_features()
        
        logger.info("¡Configuración de base de datos completada!")
        
        # Mostrar estadísticas
        self.show_database_stats()
    
    def show_database_stats(self):
        """Mostrar estadísticas de la base de datos"""
        with self.driver.session() as session:
            # Contar nodos
            stats = {}
            labels = ["Auto", "Marca", "Tipo", "Combustible", "Transmision"]
            
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                stats[label] = result.single()["count"]
            
            # Contar relaciones
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats["Relaciones"] = rel_result.single()["count"]
            
            logger.info("=== ESTADÍSTICAS DE LA BASE DE DATOS ===")
            for key, value in stats.items():
                logger.info(f"{key}: {value}")
            logger.info("========================================")

def main():
    # Configuración de conexión
    URI = "bolt://localhost:7687"  # Cambiar puerto de 7474 a 7687 (puerto por defecto para bolt)
    USER = "neo4j"
    PASSWORD = "proyectoNEO4J"
    
    # Configurar base de datos
    setup = Neo4jSetup(URI, USER, PASSWORD)
    
    try:
        # Probar conexión
        with setup.driver.session() as session:
            result = session.run("RETURN 'Conexión exitosa' as mensaje")
            logger.info(result.single()["mensaje"])
        
        # Configurar base de datos completa
        setup.setup_complete_database()
        
    except Exception as e:
        logger.error(f"Error durante la configuración: {e}")
        logger.error("Verifica que Neo4j esté ejecutándose y las credenciales sean correctas")
    
    finally:
        setup.close()

if __name__ == "__main__":
    main()