#!/usr/bin/env python3
"""
Gestionador mejorado para Neo4j con funcionalidades específicas para el sistema de recomendaciones
"""

from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Gestionador:
    def __init__(self, uri: str, user: str, password: str):
        """
        Inicializar conexión a Neo4j
        
        Args:
            uri: URI de conexión (ej: bolt://localhost:7687)
            user: Usuario de Neo4j
            password: Contraseña de Neo4j
        """
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verificar conexión
            with self.driver.session() as session:
                result = session.run("RETURN 'Conexión exitosa' as mensaje")
                logger.info(f"Neo4j: {result.single()['mensaje']}")
        except Exception as e:
            logger.error(f"Error conectando a Neo4j: {e}")
            raise ConnectionError(f"No se pudo conectar a Neo4j: {e}")
    
    def close(self):
        """Cerrar conexión a Neo4j"""
        if hasattr(self, 'driver') and self.driver:
            self.driver.close()
            logger.info("Conexión a Neo4j cerrada")
    
    def test_connection(self) -> bool:
        """Probar si la conexión a Neo4j está funcionando"""
        try:
            with self.driver.session() as session:
                session.run("RETURN 1 as test")
            return True
        except Exception as e:
            logger.error(f"Error en conexión: {e}")
            return False
    
    def get_database_info(self) -> Dict[str, Any]:
        """Obtener información general de la base de datos"""
        try:
            with self.driver.session() as session:
                # Obtener versión de Neo4j
                version_result = session.run("CALL dbms.components() YIELD name, versions")
                neo4j_info = version_result.data()
                
                # Contar nodos y relaciones
                nodes_result = session.run("MATCH (n) RETURN count(n) as total_nodes")
                total_nodes = nodes_result.single()["total_nodes"]
                
                rels_result = session.run("MATCH ()-[r]->() RETURN count(r) as total_relationships")
                total_relationships = rels_result.single()["total_relationships"]
                
                # Obtener etiquetas de nodos
                labels_result = session.run("CALL db.labels()")
                labels = [record["label"] for record in labels_result]
                
                # Obtener tipos de relaciones
                rel_types_result = session.run("CALL db.relationshipTypes()")
                relationship_types = [record["relationshipType"] for record in rel_types_result]
                
                return {
                    "neo4j_version": neo4j_info[0]["versions"][0] if neo4j_info else "Unknown",
                    "total_nodes": total_nodes,
                    "total_relationships": total_relationships,
                    "node_labels": labels,
                    "relationship_types": relationship_types,
                    "connection_status": "Connected"
                }
        except Exception as e:
            logger.error(f"Error obteniendo información de la base de datos: {e}")
            return {"connection_status": "Error", "error": str(e)}
    
    def get_cars_count(self) -> int:
        """Obtener número total de autos en la base de datos"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (a:Auto) RETURN count(a) as count")
                return result.single()["count"]
        except Exception as e:
            logger.error(f"Error contando autos: {e}")
            return 0
    
    def get_brands(self) -> List[str]:
        """Obtener lista de todas las marcas disponibles"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (m:Marca) RETURN m.nombre as nombre ORDER BY m.nombre")
                return [record["nombre"] for record in result]
        except Exception as e:
            logger.error(f"Error obteniendo marcas: {e}")
            return []
    
    def get_car_types(self) -> List[str]:
        """Obtener lista de todos los tipos de vehículo disponibles"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (t:Tipo) RETURN t.categoria as categoria ORDER BY t.categoria")
                return [record["categoria"] for record in result]
        except Exception as e:
            logger.error(f"Error obteniendo tipos: {e}")
            return []
    
    def get_fuel_types(self) -> List[str]:
        """Obtener lista de todos los tipos de combustible disponibles"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (c:Combustible) RETURN c.tipo as tipo ORDER BY c.tipo")
                return [record["tipo"] for record in result]
        except Exception as e:
            logger.error(f"Error obteniendo combustibles: {e}")
            return []
    
    def get_transmission_types(self) -> List[str]:
        """Obtener lista de todos los tipos de transmisión disponibles"""
        try:
            with self.driver.session() as session:
                result = session.run("MATCH (tr:Transmision) RETURN tr.tipo as tipo ORDER BY tr.tipo")
                return [record["tipo"] for record in result]
        except Exception as e:
            logger.error(f"Error obteniendo transmisiones: {e}")
            return []
    
    def get_price_range(self) -> Dict[str, float]:
        """Obtener rango de precios de los autos"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Auto) 
                    WHERE a.precio IS NOT NULL
                    RETURN min(a.precio) as min_price, max(a.precio) as max_price, avg(a.precio) as avg_price
                """)
                record = result.single()
                return {
                    "min_price": float(record["min_price"]) if record["min_price"] else 0.0,
                    "max_price": float(record["max_price"]) if record["max_price"] else 0.0,
                    "avg_price": float(record["avg_price"]) if record["avg_price"] else 0.0
                }
        except Exception as e:
            logger.error(f"Error obteniendo rango de precios: {e}")
            return {"min_price": 0.0, "max_price": 0.0, "avg_price": 0.0}
    
    def create_car(self, car_data: Dict[str, Any]) -> bool:
        """
        Crear un nuevo auto en la base de datos
        
        Args:
            car_data: Diccionario con datos del auto (id, modelo, año, precio, etc.)
        """
        try:
            with self.driver.session() as session:
                # Crear el nodo del auto
                session.run("""
                    CREATE (a:Auto {
                        id: $id,
                        modelo: $modelo,
                        año: $año,
                        precio: $precio
                    })
                """, **car_data)
                
                # Conectar con marca si existe
                if 'marca' in car_data:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MERGE (m:Marca {nombre: $marca})
                        MERGE (a)-[:ES_MARCA]->(m)
                    """, id=car_data['id'], marca=car_data['marca'])
                
                # Conectar con tipo si existe
                if 'tipo' in car_data:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MERGE (t:Tipo {categoria: $tipo})
                        MERGE (a)-[:ES_TIPO]->(t)
                    """, id=car_data['id'], tipo=car_data['tipo'])
                
                # Conectar con combustible si existe
                if 'combustible' in car_data:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MERGE (c:Combustible {tipo: $combustible})
                        MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                    """, id=car_data['id'], combustible=car_data['combustible'])
                
                # Conectar con transmisión si existe
                if 'transmision' in car_data:
                    session.run("""
                        MATCH (a:Auto {id: $id})
                        MERGE (tr:Transmision {tipo: $transmision})
                        MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                    """, id=car_data['id'], transmision=car_data['transmision'])
                
                logger.info(f"Auto creado exitosamente: {car_data.get('id', 'ID desconocido')}")
                return True
                
        except Exception as e:
            logger.error(f"Error creando auto: {e}")
            return False
    
    def search_cars(self, filters: Dict[str, Any] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Buscar autos con filtros opcionales
        
        Args:
            filters: Diccionario con filtros (marca, tipo, precio_min, precio_max, etc.)
            limit: Número máximo de resultados
        """
        try:
            # Construir query dinámicamente
            query_parts = ["MATCH (a:Auto)"]
            where_conditions = []
            parameters = {"limit": limit}
            
            if filters:
                # Filtro de marca
                if filters.get('marca'):
                    query_parts.append("MATCH (a)-[:ES_MARCA]->(m:Marca)")
                    where_conditions.append("m.nombre = $marca")
                    parameters['marca'] = filters['marca']
                
                # Filtro de tipo
                if filters.get('tipo'):
                    query_parts.append("MATCH (a)-[:ES_TIPO]->(t:Tipo)")
                    where_conditions.append("t.categoria = $tipo")
                    parameters['tipo'] = filters['tipo']
                
                # Filtro de precio mínimo
                if filters.get('precio_min'):
                    where_conditions.append("a.precio >= $precio_min")
                    parameters['precio_min'] = filters['precio_min']
                
                # Filtro de precio máximo
                if filters.get('precio_max'):
                    where_conditions.append("a.precio <= $precio_max")
                    parameters['precio_max'] = filters['precio_max']
                
                # Filtro de año mínimo
                if filters.get('año_min'):
                    where_conditions.append("a.año >= $año_min")
                    parameters['año_min'] = filters['año_min']
            
            # Agregar WHERE si hay condiciones
            if where_conditions:
                query_parts.append("WHERE " + " AND ".join(where_conditions))
            
            # Completar query
            query_parts.append("""
                OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
                OPTIONAL MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                OPTIONAL MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                RETURN a.id as id, a.modelo as modelo, a.año as año, a.precio as precio,
                       m.nombre as marca, t.categoria as tipo, 
                       c.tipo as combustible, tr.tipo as transmision
                ORDER BY a.precio ASC
                LIMIT $limit
            """)
            
            query = " ".join(query_parts)
            
            with self.driver.session() as session:
                result = session.run(query, parameters)
                cars = []
                
                for record in result:
                    car = {
                        'id': record['id'],
                        'modelo': record['modelo'],
                        'año': record['año'],
                        'precio': record['precio'],
                        'marca': record['marca'],
                        'tipo': record['tipo'],
                        'combustible': record['combustible'],
                        'transmision': record['transmision']
                    }
                    cars.append(car)
                
                return cars
                
        except Exception as e:
            logger.error(f"Error buscando autos: {e}")
            return []
    
    def delete_car(self, car_id: str) -> bool:
        """Eliminar un auto por su ID"""
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (a:Auto {id: $car_id})
                    DETACH DELETE a
                    RETURN count(a) as deleted
                """, car_id=car_id)
                
                deleted_count = result.single()["deleted"]
                if deleted_count > 0:
                    logger.info(f"Auto eliminado: {car_id}")
                    return True
                else:
                    logger.warning(f"No se encontró auto con ID: {car_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error eliminando auto: {e}")
            return False
    
    def update_car(self, car_id: str, updates: Dict[str, Any]) -> bool:
        """Actualizar un auto existente"""
        try:
            with self.driver.session() as session:
                # Construir query de actualización dinámicamente
                set_clauses = []
                parameters = {"car_id": car_id}
                
                for key, value in updates.items():
                    if key not in ['marca', 'tipo', 'combustible', 'transmision']:  # Estas requieren manejo especial
                        set_clauses.append(f"a.{key} = ${key}")
                        parameters[key] = value
                
                if set_clauses:
                    query = f"""
                        MATCH (a:Auto {{id: $car_id}})
                        SET {', '.join(set_clauses)}
                        RETURN a
                    """
                    session.run(query, parameters)
                
                logger.info(f"Auto actualizado: {car_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error actualizando auto: {e}")
            return False

def main():
    """Función principal para probar el gestionador"""
    # Configuración
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "proyectoNEO4J"
    
    try:
        # Crear conexión
        gestionador = Gestionador(URI, USER, PASSWORD)
        
        # Probar funcionalidades
        print("=== PRUEBA DEL GESTIONADOR ===")
        
        # Información de la base de datos
        db_info = gestionador.get_database_info()
        print(f"Neo4j Version: {db_info.get('neo4j_version', 'Unknown')}")
        print(f"Total de nodos: {db_info.get('total_nodes', 0)}")
        print(f"Total de relaciones: {db_info.get('total_relationships', 0)}")
        
        # Estadísticas
        print(f"\nTotal de autos: {gestionador.get_cars_count()}")
        print(f"Marcas disponibles: {len(gestionador.get_brands())}")
        print(f"Tipos disponibles: {len(gestionador.get_car_types())}")
        
        # Rango de precios
        price_range = gestionador.get_price_range()
        print(f"Precio mínimo: ${price_range['min_price']:,.2f}")
        print(f"Precio máximo: ${price_range['max_price']:,.2f}")
        print(f"Precio promedio: ${price_range['avg_price']:,.2f}")
        
        # Buscar algunos autos
        print("\n--- Autos Toyota ---")
        toyota_cars = gestionador.search_cars({"marca": "Toyota"}, limit=3)
        for car in toyota_cars:
            print(f"- {car['modelo']} {car['año']} - ${car['precio']:,}")
        
        print("\n✓ Todas las pruebas completadas exitosamente")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    finally:
        if 'gestionador' in locals():
            gestionador.close()

if __name__ == "__main__":
    main()