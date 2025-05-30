#!/usr/bin/env python3
"""
Sistema de recomendaciones de autos usando Neo4j
Conecta con la base de datos y genera recomendaciones basadas en las preferencias del usuario
"""

from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarRecommender:
    def __init__(self, uri: str, user: str, password: str):
        """Inicializar conexión a Neo4j"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verificar conexión
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Conexión exitosa a Neo4j")
        except Exception as e:
            logger.error(f"Error conectando a Neo4j: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def parse_budget_range(self, budget_str: str) -> tuple:
        """Convertir string de presupuesto a rango numérico"""
        try:
            if budget_str == "100000+":
                return (100000, float('inf'))
            elif "-" in budget_str:
                min_val, max_val = budget_str.split("-")
                return (int(min_val), int(max_val))
            else:
                # Si es un número simple, usar como máximo
                return (0, int(budget_str))
        except Exception as e:
            logger.warning(f"Error parseando presupuesto '{budget_str}': {e}")
            return (0, float('inf'))
    
    def normalize_preferences(self, brands=None, budget=None, fuel=None, types=None, transmission=None):
        """Normalizar y validar las preferencias del usuario"""
        # Normalizar marcas
        if brands:
            if isinstance(brands, dict):
                # Si viene como dict de grupos, tomar todos los valores
                brands = list(brands.values())
            elif isinstance(brands, str):
                brands = [brands]
        
        # Normalizar presupuesto
        if budget:
            min_price, max_price = self.parse_budget_range(budget)
        else:
            min_price, max_price = 0, float('inf')
        
        # Normalizar combustible
        if fuel:
            if isinstance(fuel, list):
                fuel = fuel[0] if fuel else None
            # Mapear nombres comunes
            fuel_mapping = {
                'gasolina': 'Gasolina',
                'gas': 'Gasolina',
                'diesel': 'Diésel',
                'electrico': 'Eléctrico',
                'electric': 'Eléctrico',
                'hibrido': 'Híbrido',
                'hybrid': 'Híbrido'
            }
            fuel = fuel_mapping.get(fuel.lower() if fuel else None, fuel)
        
        # Normalizar tipos
        if types:
            if isinstance(types, str):
                types = [types]
            # Mapear nombres comunes
            type_mapping = {
                'sedan': 'Sedán',
                'suv': 'SUV',
                'hatchback': 'Hatchback',
                'pickup': 'Pickup',
                'coupe': 'Coupé',
                'convertible': 'Convertible'
            }
            types = [type_mapping.get(t.lower(), t) for t in types]
        
        # Normalizar transmisión
        if transmission:
            if isinstance(transmission, list):
                transmission = transmission[0] if transmission else None
            # Mapear nombres comunes
            trans_mapping = {
                'automatic': 'Automática',
                'automatica': 'Automática',
                'manual': 'Manual',
                'semiautomatic': 'Semiautomática',
                'semiautomatica': 'Semiautomática'
            }
            transmission = trans_mapping.get(transmission.lower() if transmission else None, transmission)
        
        return {
            'brands': brands,
            'min_price': min_price,
            'max_price': max_price,
            'fuel': fuel,
            'types': types,
            'transmission': transmission
        }
    
    def build_recommendation_query(self, preferences: Dict) -> tuple:
        """Construir consulta Cypher dinámica basada en preferencias"""
        query_parts = ["MATCH (a:Auto)"]
        where_conditions = []
        parameters = {}
        
        # Filtro de presupuesto (siempre aplicar)
        where_conditions.append("a.precio >= $min_price AND a.precio <= $max_price")
        parameters['min_price'] = preferences['min_price']
        parameters['max_price'] = preferences['max_price']
        
        # Filtro de marca
        if preferences['brands']:
            query_parts.append("MATCH (a)-[:ES_MARCA]->(m:Marca)")
            where_conditions.append("m.nombre IN $brands")
            parameters['brands'] = preferences['brands']
        
        # Filtro de combustible
        if preferences['fuel']:
            query_parts.append("MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)")
            where_conditions.append("c.tipo = $fuel")
            parameters['fuel'] = preferences['fuel']
        
        # Filtro de tipo
        if preferences['types']:
            query_parts.append("MATCH (a)-[:ES_TIPO]->(t:Tipo)")
            where_conditions.append("t.categoria IN $types")
            parameters['types'] = preferences['types']
        
        # Filtro de transmisión
        if preferences['transmission']:
            query_parts.append("MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)")
            where_conditions.append("tr.tipo = $transmission")
            parameters['transmission'] = preferences['transmission']
        
        # Construir query completa
        if where_conditions:
            query_parts.append("WHERE " + " AND ".join(where_conditions))
        
        # Obtener datos relacionados
        query_parts.append("""
            OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
            OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
            OPTIONAL MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            OPTIONAL MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            RETURN a.id as id, a.modelo as modelo, a.año as año, a.precio as precio,
                   a.caracteristicas as caracteristicas,
                   m.nombre as marca, t.categoria as tipo, 
                   c.tipo as combustible, tr.tipo as transmision
            ORDER BY a.precio ASC
            LIMIT 20
        """)
        
        query = " ".join(query_parts)
        return query, parameters
    
    def execute_recommendation_query(self, query: str, parameters: Dict) -> List[Dict]:
        """Ejecutar consulta de recomendaciones"""
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters)
                recommendations = []
                
                for record in result:
                    car_data = {
                        'id': record['id'],
                        'name': f"{record['marca']} {record['modelo']} {record['año']}" if record['marca'] else f"{record['modelo']} {record['año']}",
                        'model': record['modelo'],
                        'brand': record['marca'] or 'Marca no especificada',
                        'year': record['año'],
                        'price': float(record['precio']) if record['precio'] else 0,
                        'type': record['tipo'] or 'Tipo no especificado',
                        'fuel': record['combustible'] or 'Combustible no especificado',
                        'transmission': record['transmision'] or 'Transmisión no especificada',
                        'features': record['caracteristicas'] or [],
                        'image': None  # Placeholder para imágenes futuras
                    }
                    recommendations.append(car_data)
                
                return recommendations
                
        except Exception as e:
            logger.error(f"Error ejecutando consulta de recomendaciones: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            return []
    
    def add_similarity_score(self, recommendations: List[Dict], preferences: Dict) -> List[Dict]:
        """Agregar puntuación de similitud basada en preferencias"""
        for car in recommendations:
            score = 0
            
            # Puntuación por rango de precio (mayor score para precios más bajos dentro del rango)
            if preferences['max_price'] != float('inf'):
                price_ratio = car['price'] / preferences['max_price']
                score += (1 - price_ratio) * 30  # Hasta 30 puntos por precio
            
            # Bonificación por marca preferida
            if preferences['brands'] and car['brand'] in preferences['brands']:
                score += 25
            
            # Bonificación por tipo preferido
            if preferences['types'] and car['type'] in preferences['types']:
                score += 20
            
            # Bonificación por combustible preferido
            if preferences['fuel'] and car['fuel'] == preferences['fuel']:
                score += 15
            
            # Bonificación por transmisión preferida
            if preferences['transmission'] and car['transmission'] == preferences['transmission']:
                score += 10
            
            # Bonificación por características
            if car['features']:
                score += len(car['features']) * 2
            
            car['similarity_score'] = round(score, 2)
        
        # Ordenar por puntuación de similitud (descendente)
        recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return recommendations
    
    def get_recommendations(self, brands=None, budget=None, fuel=None, types=None, transmission=None) -> List[Dict]:
        """
        Obtener recomendaciones de autos basadas en preferencias del usuario
        
        Args:
            brands: Lista de marcas preferidas o dict de grupos
            budget: Rango de presupuesto (ej: "15000-30000", "100000+")
            fuel: Tipo de combustible preferido
            types: Lista de tipos de vehículo preferidos
            transmission: Tipo de transmisión preferida
        
        Returns:
            Lista de diccionarios con recomendaciones de autos
        """
        try:
            # Log de entrada para debugging
            logger.info("=== GENERANDO RECOMENDACIONES ===")
            logger.info(f"Brands: {brands}")
            logger.info(f"Budget: {budget}")
            logger.info(f"Fuel: {fuel}")
            logger.info(f"Types: {types}")
            logger.info(f"Transmission: {transmission}")
            
            # Normalizar preferencias
            preferences = self.normalize_preferences(brands, budget, fuel, types, transmission)
            logger.info(f"Preferencias normalizadas: {preferences}")
            
            # Construir y ejecutar consulta
            query, parameters = self.build_recommendation_query(preferences)
            logger.info(f"Query generada: {query}")
            logger.info(f"Parámetros: {parameters}")
            
            # Ejecutar consulta
            recommendations = self.execute_recommendation_query(query, parameters)
            logger.info(f"Encontradas {len(recommendations)} recomendaciones iniciales")
            
            # Agregar puntuación de similitud
            if recommendations:
                recommendations = self.add_similarity_score(recommendations, preferences)
                logger.info(f"Recomendaciones ordenadas por similitud")
            
            # Limitar a máximo 10 recomendaciones
            recommendations = recommendations[:10]
            
            logger.info(f"Devolviendo {len(recommendations)} recomendaciones finales")
            return recommendations
            
        except Exception as e:
            logger.error(f"Error general en get_recommendations: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas de la base de datos"""
        try:
            with self.driver.session() as session:
                stats = {}
                
                # Contar autos por marca
                result = session.run("""
                    MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
                    RETURN m.nombre as marca, count(a) as cantidad
                    ORDER BY cantidad DESC
                """)
                stats['cars_by_brand'] = [dict(record) for record in result]
                
                # Contar autos por tipo
                result = session.run("""
                    MATCH (a:Auto)-[:ES_TIPO]->(t:Tipo)
                    RETURN t.categoria as tipo, count(a) as cantidad
                    ORDER BY cantidad DESC
                """)
                stats['cars_by_type'] = [dict(record) for record in result]
                
                # Rango de precios
                result = session.run("""
                    MATCH (a:Auto)
                    RETURN min(a.precio) as precio_min, max(a.precio) as precio_max, avg(a.precio) as precio_promedio
                """)
                price_stats = result.single()
                stats['price_range'] = {
                    'min': price_stats['precio_min'],
                    'max': price_stats['precio_max'],
                    'average': round(price_stats['precio_promedio'], 2)
                }
                
                # Total de autos
                result = session.run("MATCH (a:Auto) RETURN count(a) as total")
                stats['total_cars'] = result.single()['total']
                
                return stats
                
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}

# Instancia global del recomendador
_recommender_instance = None

def get_recommender_instance():
    """Obtener instancia singleton del recomendador"""
    global _recommender_instance
    if _recommender_instance is None:
        # Configuración de conexión
        URI = "bolt://localhost:7687"  # Puerto correcto para bolt
        USER = "neo4j"
        PASSWORD = "proyectoNEO4J"
        
        try:
            _recommender_instance = CarRecommender(URI, USER, PASSWORD)
        except Exception as e:
            logger.error(f"No se pudo crear instancia del recomendador: {e}")
            _recommender_instance = None
    
    return _recommender_instance

def get_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None):
    """
    Función principal para obtener recomendaciones (compatibilidad con Flask)
    
    Esta función es llamada directamente desde app.py
    """
    recommender = get_recommender_instance()
    
    if recommender is None:
        logger.error("No hay conexión a Neo4j disponible")
        # Devolver datos de ejemplo si no hay conexión
        return get_fallback_recommendations(brands, budget, fuel, types, transmission)
    
    try:
        return recommender.get_recommendations(brands, budget, fuel, types, transmission)
    except Exception as e:
        logger.error(f"Error en get_recommendations: {e}")
        return get_fallback_recommendations(brands, budget, fuel, types, transmission)

def get_fallback_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None):
    """Recomendaciones de respaldo cuando Neo4j no está disponible"""
    logger.warning("Usando recomendaciones de respaldo")
    
    # Datos de ejemplo basados en las preferencias
    fallback_cars = [
        {
            "id": "fallback_1",
            "name": "Toyota Corolla 2024",
            "model": "Corolla",
            "brand": "Toyota",
            "year": 2024,
            "price": 25000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Aire acondicionado", "Radio AM/FM", "Bluetooth", "Cámara trasera"],
            "similarity_score": 85.0,
            "image": None
        },
        {
            "id": "fallback_2",
            "name": "Honda Civic 2024",
            "model": "Civic",
            "brand": "Honda",
            "year": 2024,
            "price": 27000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Manual",
            "features": ["Pantalla táctil", "Sistema de navegación", "Bluetooth", "Control crucero"],
            "similarity_score": 80.0,
            "image": None
        },
        {
            "id": "fallback_3",
            "name": "Tesla Model 3 2024",
            "model": "Model 3",
            "brand": "Tesla",
            "year": 2024,
            "price": 42000,
            "type": "Sedán",
            "fuel": "Eléctrico",
            "transmission": "Automática",
            "features": ["Piloto automático", "Pantalla táctil 15\"", "Supercargador", "Actualización OTA"],
            "similarity_score": 75.0,
            "image": None
        }
    ]
    
    # Filtrar datos de ejemplo basados en preferencias básicas
    filtered_cars = []
    
    for car in fallback_cars:
        include_car = True
        
        # Filtro básico por marca
        if brands:
            brand_list = brands if isinstance(brands, list) else list(brands.values()) if isinstance(brands, dict) else [brands]
            if car["brand"] not in brand_list:
                include_car = False
        
        # Filtro básico por tipo
        if types and isinstance(types, list):
            if car["type"] not in types:
                include_car = False
        
        # Filtro básico por combustible
        if fuel and isinstance(fuel, str):
            if car["fuel"].lower() != fuel.lower():
                include_car = False
        
        if include_car:
            filtered_cars.append(car)
    
    # Si no hay autos filtrados, devolver todos los de ejemplo
    return filtered_cars if filtered_cars else fallback_cars

def get_database_statistics():
    """Obtener estadísticas de la base de datos"""
    recommender = get_recommender_instance()
    if recommender:
        return recommender.get_statistics()
    return {}

def test_connection():
    """Probar conexión a Neo4j"""
    try:
        recommender = get_recommender_instance()
        if recommender:
            logger.info("✓ Conexión a Neo4j exitosa")
            return True
        else:
            logger.error("✗ No se pudo conectar a Neo4j")
            return False
    except Exception as e:
        logger.error(f"✗ Error probando conexión: {e}")
        return False

# Función para limpiar recursos al cerrar la aplicación
def cleanup():
    """Limpiar recursos del recomendador"""
    global _recommender_instance
    if _recommender_instance:
        _recommender_instance.close()
        _recommender_instance = None

# Registrar función de limpieza
import atexit
atexit.register(cleanup)

if __name__ == "__main__":
    # Script de prueba
    print("=== PRUEBA DEL SISTEMA DE RECOMENDACIONES ===")
    
    # Probar conexión
    if test_connection():
        print("✓ Conexión exitosa")
        
        # Probar recomendaciones
        print("\n--- Prueba 1: Autos Toyota económicos ---")
        recommendations = get_recommendations(
            brands=["Toyota"],
            budget="15000-30000",
            fuel="Gasolina",
            types=["Sedán"],
            transmission="Automática"
        )
        
        for i, car in enumerate(recommendations[:3], 1):
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')}")
        
        print("\n--- Prueba 2: Autos eléctricos premium ---")
        recommendations = get_recommendations(
            brands=["Tesla"],
            budget="50000-100000",
            fuel="Eléctrico",
            types=["Sedán", "SUV"],
            transmission="Automática"
        )
        
        for i, car in enumerate(recommendations[:3], 1):
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')}")
        
        # Mostrar estadísticas
        print("\n--- Estadísticas de la base de datos ---")
        stats = get_database_statistics()
        if stats:
            print(f"Total de autos: {stats.get('total_cars', 'N/A')}")
            print(f"Rango de precios: ${stats.get('price_range', {}).get('min', 'N/A'):,} - ${stats.get('price_range', {}).get('max', 'N/A'):,}")
            print(f"Precio promedio: ${stats.get('price_range', {}).get('average', 'N/A'):,}")
        
    else:
        print("✗ No se pudo conectar a Neo4j")
        print("Asegúrate de que:")
        print("1. Neo4j Desktop esté ejecutándose")
        print("2. La base de datos esté activa")
        print("3. Las credenciales sean correctas")
        print("4. El puerto 7687 esté disponible")