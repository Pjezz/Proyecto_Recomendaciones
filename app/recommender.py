#!/usr/bin/env python3
"""
Sistema de recomendaciones de autos usando Neo4j
Conecta con la base de datos y genera recomendaciones basadas en las preferencias del usuario
Incluye personalización demográfica por género y edad
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
    
    def apply_demographic_scoring(self, recommendations: List[Dict], gender: str, age_range: str) -> List[Dict]:
        """Aplicar personalización demográfica según género y edad"""
        
        # Definir grupos de edad
        age_group = self.get_age_group(age_range)
        
        logger.info(f"Aplicando scoring demográfico: género={gender}, edad_grupo={age_group}")
        
        for car in recommendations:
            demographic_bonus = 0
            car_type = car.get('type', '').lower()
            car_brand = car.get('brand', '').lower()
            car_name = car.get('name', '').lower()
            features_text = str(car.get('features', [])).lower()
            
            # Lógica para mujeres
            if gender == 'femenino':
                if age_group == 'young':  # 18-25: igual que hombres jóvenes
                    if car_type in ['coupé', 'convertible'] or any(sport_word in car_name for sport_word in ['sport', 'gt', 'turbo']):
                        demographic_bonus += 5
                        logger.debug(f"Bonus joven femenino deportivo: +5 para {car['name']}")
                        
                elif age_group == 'reproductive':  # 26-45: preferencia familiar
                    if car_type in ['suv']:
                        demographic_bonus += 15
                        logger.debug(f"Bonus reproductivo femenino SUV: +15 para {car['name']}")
                    elif car_type == 'sedán':
                        demographic_bonus += 10
                        logger.debug(f"Bonus reproductivo femenino sedán: +10 para {car['name']}")
                    # Bonus por características familiares
                    if any(family_word in features_text for family_word in ['familia', 'seguridad', 'espacio', 'asientos']):
                        demographic_bonus += 8
                        logger.debug(f"Bonus características familiares: +8 para {car['name']}")
                        
                elif age_group == 'mature':  # 46+: comfort y luxury
                    if any(luxury_brand in car_brand for luxury_brand in ['mercedes', 'bmw', 'audi', 'lexus']):
                        demographic_bonus += 12
                        logger.debug(f"Bonus marca premium mujer madura: +12 para {car['name']}")
            
            # Lógica para hombres
            elif gender == 'masculino':
                if age_group == 'young':  # 18-25: deportivos
                    if car_type in ['coupé', 'convertible'] or any(sport_word in car_name for sport_word in ['sport', 'gt', 'turbo']):
                        demographic_bonus += 8
                        logger.debug(f"Bonus joven masculino deportivo: +8 para {car['name']}")
                        
                elif age_group == 'mature':  # 46+: comfort y luxury
                    if any(luxury_brand in car_brand for luxury_brand in ['mercedes', 'bmw', 'audi', 'lexus']):
                        demographic_bonus += 12
                        logger.debug(f"Bonus marca premium hombre maduro: +12 para {car['name']}")
            
            # Para todos: bonificación por características de comfort en edad madura
            if age_group == 'mature':
                comfort_features = ['cuero', 'premium', 'lujo', 'confort', 'leather', 'luxury']
                for feature in comfort_features:
                    if feature in features_text:
                        demographic_bonus += 3
                        logger.debug(f"Bonus comfort maduro: +3 para {car['name']}")
                        break
            
            # Aplicar bonificación
            if demographic_bonus > 0:
                original_score = car.get('similarity_score', 0)
                car['similarity_score'] = original_score + demographic_bonus
                car['demographic_bonus'] = demographic_bonus
                logger.info(f"Bonus demográfico aplicado: {car['name']} +{demographic_bonus} (total: {car['similarity_score']})")
        
        # Reordenar por puntuación actualizada
        recommendations.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return recommendations
    
    def get_age_group(self, age_range: str) -> str:
        """Convertir rango de edad a grupo demográfico"""
        if age_range in ['18-25']:
            return 'young'
        elif age_range in ['26-35', '36-45']:
            return 'reproductive'
        elif age_range in ['46-55', '56+']:
            return 'mature'
        else:
            return 'unknown'
    
    def get_recommendations(self, brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None) -> List[Dict]:
        """
        Obtener recomendaciones de autos basadas en preferencias del usuario
        Incluye personalización demográfica
        
        Args:
            brands: Lista de marcas preferidas o dict de grupos
            budget: Rango de presupuesto (ej: "15000-30000", "100000+")
            fuel: Tipo de combustible preferido
            types: Lista de tipos de vehículo preferidos
            transmission: Tipo de transmisión preferida
            gender: Género del usuario para personalización
            age_range: Rango de edad del usuario para personalización
        
        Returns:
            Lista de diccionarios con recomendaciones de autos personalizadas
        """
        try:
            # Log de entrada para debugging
            logger.info("=== GENERANDO RECOMENDACIONES PERSONALIZADAS ===")
            logger.info(f"Brands: {brands}")
            logger.info(f"Budget: {budget}")
            logger.info(f"Fuel: {fuel}")
            logger.info(f"Types: {types}")
            logger.info(f"Transmission: {transmission}")
            logger.info(f"Gender: {gender}")
            logger.info(f"Age Range: {age_range}")
            
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
            
            # Agregar puntuación de similitud básica
            if recommendations:
                recommendations = self.add_similarity_score(recommendations, preferences)
                logger.info(f"Puntuación básica aplicada")
                
                # Aplicar personalización demográfica si se proporciona
                if gender and age_range:
                    recommendations = self.apply_demographic_scoring(recommendations, gender, age_range)
                    logger.info(f"Personalización demográfica aplicada")
            
            # Limitar a máximo 10 recomendaciones
            recommendations = recommendations[:10]
            
            logger.info(f"Devolviendo {len(recommendations)} recomendaciones finales personalizadas")
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

def get_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
    """
    Función principal para obtener recomendaciones (compatibilidad con Flask)
    
    Esta función es llamada directamente desde app.py
    """
    recommender = get_recommender_instance()
    
    if recommender is None:
        logger.error("No hay conexión a Neo4j disponible")
        # Devolver datos de ejemplo si no hay conexión
        return get_fallback_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
    
    try:
        return recommender.get_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
    except Exception as e:
        logger.error(f"Error en get_recommendations: {e}")
        return get_fallback_recommendations(brands, budget, fuel, types, transmission, gender, age_range)

def get_fallback_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
    """Recomendaciones de respaldo cuando Neo4j no está disponible"""
    logger.warning("Usando recomendaciones de respaldo con personalización demográfica")
    
    # Datos de ejemplo expandidos
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
            "features": ["Aire acondicionado", "Radio AM/FM", "Bluetooth", "Cámara trasera", "Seguridad Toyota Safety"],
            "similarity_score": 85.0,
            "image": None
        },
        {
            "id": "fallback_2",
            "name": "Honda CR-V 2024",
            "model": "CR-V",
            "brand": "Honda",
            "year": 2024,
            "price": 35000,
            "type": "SUV",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Espacio familiar", "Asientos cómodos", "Honda Sensing", "Amplio maletero"],
            "similarity_score": 80.0,
            "image": None
        },
        {
            "id": "fallback_3",
            "name": "BMW M3 2024",
            "model": "M3",
            "brand": "BMW",
            "year": 2024,
            "price": 75000,
            "type": "Coupé",
            "fuel": "Gasolina",
            "transmission": "Manual",
            "features": ["Motor turbo", "Deportivo", "Asientos sport", "Performance premium"],
            "similarity_score": 75.0,
            "image": None
        },
        {
            "id": "fallback_4",
            "name": "Mercedes-Benz S-Class 2024",
            "model": "S-Class",
            "brand": "Mercedes-Benz",
            "year": 2024,
            "price": 95000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Asientos de cuero premium", "Lujo alemán", "Tecnología avanzada", "Confort superior"],
            "similarity_score": 70.0,
            "image": None
        },
        {
            "id": "fallback_5",
            "name": "Tesla Model Y 2024",
            "model": "Model Y",
            "brand": "Tesla",
            "year": 2024,
            "price": 55000,
            "type": "SUV",
            "fuel": "Eléctrico",
            "transmission": "Automática",
            "features": ["Piloto automático", "Pantalla táctil", "Carga rápida", "Tecnología verde"],
            "similarity_score": 68.0,
            "image": None
        },
        {
            "id": "fallback_6",
            "name": "Ford Mustang GT 2024",
            "model": "Mustang GT",
            "brand": "Ford",
            "year": 2024,
            "price": 45000,
            "type": "Coupé",
            "fuel": "Gasolina",
            "transmission": "Manual",
            "features": ["Motor V8", "Deportivo", "Diseño icónico", "Performance sport"],
            "similarity_score": 65.0,
            "image": None
        }
    ]
    
    # Aplicar filtros básicos
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
        
        # Filtro básico por presupuesto
        if budget:
            try:
                if budget == "100000+":
                    if car["price"] < 100000:
                        include_car = False
                elif "-" in budget:
                    min_val, max_val = budget.split("-")
                    if not (int(min_val) <= car["price"] <= int(max_val)):
                        include_car = False
            except:
                pass
        
        if include_car:
            filtered_cars.append(car)
    
    # Si no hay autos filtrados, devolver todos los de ejemplo
    final_cars = filtered_cars if filtered_cars else fallback_cars
    
    # Aplicar personalización demográfica si se proporciona
    if gender and age_range:
        final_cars = apply_demographic_scoring_fallback(final_cars, gender, age_range)
    
    return final_cars[:10]  # Limitar a 10

def apply_demographic_scoring_fallback(recommendations, gender, age_range):
    """Aplicar scoring demográfico a las recomendaciones de fallback"""
    
    # Definir grupos de edad
    if age_range in ['18-25']:
        age_group = 'young'
    elif age_range in ['26-35', '36-45']:
        age_group = 'reproductive'
    elif age_range in ['46-55', '56+']:
        age_group = 'mature'
    else:
        age_group = 'unknown'
    
    for car in recommendations:
        demographic_bonus = 0
        car_type = car.get('type', '').lower()
        car_brand = car.get('brand', '').lower()
        car_name = car.get('name', '').lower()
        features_text = str(car.get('features', [])).lower()
        
        # Lógica para mujeres
        if gender == 'femenino':
            if age_group == 'young':  # 18-25: igual que hombres jóvenes
                if car_type in ['coupé', 'convertible'] or any(sport_word in car_name for sport_word in ['sport', 'gt', 'turbo', 'mustang', 'm3']):
                    demographic_bonus += 5
                    
            elif age_group == 'reproductive':  # 26-45: preferencia familiar
                if car_type in ['suv']:
                    demographic_bonus += 15
                elif car_type == 'sedán':
                    demographic_bonus += 10
                # Bonus por características familiares
                if any(family_word in features_text for family_word in ['familia', 'seguridad', 'espacio', 'asientos']):
                    demographic_bonus += 8
                    
            elif age_group == 'mature':  # 46+: comfort y luxury
                if any(luxury_brand in car_brand for luxury_brand in ['mercedes', 'bmw', 'audi', 'lexus']):
                    demographic_bonus += 12
        
        # Lógica para hombres
        elif gender == 'masculino':
            if age_group == 'young':  # 18-25: deportivos
                if car_type in ['coupé', 'convertible'] or any(sport_word in car_name for sport_word in ['sport', 'gt', 'turbo', 'mustang', 'm3']):
                    demographic_bonus += 8
                    
            elif age_group == 'mature':  # 46+: comfort y luxury
                if any(luxury_brand in car_brand for luxury_brand in ['mercedes', 'bmw', 'audi', 'lexus']):
                    demographic_bonus += 12
        
        # Para todos: bonificación por características de comfort en edad madura
        if age_group == 'mature':
            comfort_features = ['cuero', 'premium', 'lujo', 'confort', 'leather', 'luxury']
            for feature in comfort_features:
                if feature in features_text:
                    demographic_bonus += 3
                    break
        
        # Aplicar bonificación
        if demographic_bonus > 0:
            original_score = car.get('similarity_score', 0)
            car['similarity_score'] = original_score + demographic_bonus
            car['demographic_bonus'] = demographic_bonus
    
    # Reordenar por puntuación actualizada
    recommendations.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
    
    return recommendations

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
    print("=== PRUEBA DEL SISTEMA DE RECOMENDACIONES PERSONALIZADO ===")
    
    # Probar conexión
    if test_connection():
        print("✓ Conexión exitosa")
        
        # Probar recomendaciones con personalización demográfica
        print("\n--- Prueba 1: Mujer joven (18-25) buscando auto económico ---")
        recommendations = get_recommendations(
            brands=["Toyota", "Honda"],
            budget="15000-30000",
            fuel="Gasolina",
            types=["Sedán"],
            transmission="Automática",
            gender="femenino",
            age_range="18-25"
        )
        
        for i, car in enumerate(recommendations[:3], 1):
            bonus = car.get('demographic_bonus', 0)
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')} (Bonus demográfico: +{bonus})")
        
        print("\n--- Prueba 2: Mujer edad reproductiva (26-35) buscando SUV familiar ---")
        recommendations = get_recommendations(
            brands=["Honda", "Toyota"],
            budget="30000-50000",
            fuel="Gasolina",
            types=["SUV"],
            transmission="Automática",
            gender="femenino",
            age_range="26-35"
        )
        
        for i, car in enumerate(recommendations[:3], 1):
            bonus = car.get('demographic_bonus', 0)
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')} (Bonus demográfico: +{bonus})")
        
        print("\n--- Prueba 3: Hombre joven (18-25) buscando deportivo ---")
        recommendations = get_recommendations(
            brands=["BMW", "Ford"],
            budget="40000-80000",
            fuel="Gasolina",
            types=["Coupé"],
            transmission="Manual",
            gender="masculino",
            age_range="18-25"
        )
        
        for i, car in enumerate(recommendations[:3], 1):
            bonus = car.get('demographic_bonus', 0)
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')} (Bonus demográfico: +{bonus})")
        
        print("\n--- Prueba 4: Persona madura (46+) buscando lujo ---")
        recommendations = get_recommendations(
            brands=["Mercedes-Benz", "BMW"],
            budget="80000-120000",
            fuel="Gasolina",
            types=["Sedán"],
            transmission="Automática",
            gender="masculino",
            age_range="46-55"
        )
        
        for i, car in enumerate(recommendations[:3], 1):
            bonus = car.get('demographic_bonus', 0)
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')} (Bonus demográfico: +{bonus})")
        
        # Mostrar estadísticas
        print("\n--- Estadísticas de la base de datos ---")
        stats = get_database_statistics()
        if stats:
            print(f"Total de autos: {stats.get('total_cars', 'N/A')}")
            print(f"Rango de precios: ${stats.get('price_range', {}).get('min', 'N/A'):,} - ${stats.get('price_range', {}).get('max', 'N/A'):,}")
            print(f"Precio promedio: ${stats.get('price_range', {}).get('average', 'N/A'):,}")
        
    else:
        print("✗ No se pudo conectar a Neo4j")
        print("Probando con datos de ejemplo...")
        
        # Probar con datos de fallback
        recommendations = get_fallback_recommendations(
            brands=["Toyota"],
            budget="20000-40000",
            gender="femenino",
            age_range="26-35"
        )
        
        print(f"\n--- Recomendaciones de ejemplo (mujer 26-35) ---")
        for i, car in enumerate(recommendations[:3], 1):
            bonus = car.get('demographic_bonus', 0)
            print(f"{i}. {car['name']} - ${car['price']:,} - Score: {car.get('similarity_score', 'N/A')} (Bonus demográfico: +{bonus})")
        
        print("\nAsegúrate de que:")
        print("1. Neo4j Desktop esté ejecutándose")
        print("2. La base de datos esté activa")
        print("3. Las credenciales sean correctas")
        print("4. El puerto 7687 esté disponible")