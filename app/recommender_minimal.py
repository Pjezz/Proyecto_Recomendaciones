#!/usr/bin/env python3
"""
Sistema de recomendaciones inteligente para autos
Funciona con Neo4j y incluye personalización demográfica
"""

from neo4j import GraphDatabase
import logging
import traceback
from typing import List, Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CarRecommendationSystem:
    def __init__(self):
        # Configuraciones de conexión a probar
        self.configs = [
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
        ]
        self.driver = None
        self.connected = False
        self.connect()
    
    def connect(self):
        """Establecer conexión con Neo4j"""
        for config in self.configs:
            try:
                self.driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"✅ Conexión exitosa con Neo4j usando {config['password']}")
                self.connected = True
                return
            except Exception as e:
                logger.warning(f"❌ Fallo conexión con {config['password']}: {e}")
                continue
        
        logger.error("❌ No se pudo conectar a Neo4j con ninguna configuración")
        self.connected = False
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def get_recommendations_from_neo4j(self, brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
        """Obtener recomendaciones desde Neo4j con personalización demográfica"""
        if not self.connected:
            logger.warning("❌ Neo4j no conectado, usando datos de ejemplo")
            return self.get_fallback_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
        
        try:
            with self.driver.session() as session:
                # Construir la consulta dinámicamente
                conditions = []
                params = {}
                
                # Filtros básicos
                if brands and len(brands) > 0:
                    conditions.append("m.nombre IN $brands")
                    params['brands'] = brands
                
                if budget:
                    try:
                        if isinstance(budget, str):
                            # Formato: "20000-50000"
                            if '-' in budget:
                                min_price, max_price = budget.split('-')
                                conditions.append("a.precio >= $min_price AND a.precio <= $max_price")
                                params['min_price'] = int(min_price)
                                params['max_price'] = int(max_price)
                        elif isinstance(budget, dict):
                            if 'min' in budget and budget['min']:
                                conditions.append("a.precio >= $min_price")
                                params['min_price'] = int(budget['min'])
                            if 'max' in budget and budget['max']:
                                conditions.append("a.precio <= $max_price")
                                params['max_price'] = int(budget['max'])
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Error procesando budget: {e}")
                
                if fuel and len(fuel) > 0:
                    conditions.append("c.tipo IN $fuel")
                    params['fuel'] = fuel
                
                if types and len(types) > 0:
                    conditions.append("t.categoria IN $types")
                    params['types'] = types
                
                if transmission and len(transmission) > 0:
                    conditions.append("tr.tipo IN $transmission")
                    params['transmission'] = transmission
                
                # Construir WHERE clause
                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)
                
                # Consulta principal
                cypher_query = f"""
                MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
                MATCH (a)-[:ES_TIPO]->(t:Tipo)
                MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                {where_clause}
                
                // Calcular puntuación base
                WITH a, m, t, c, tr,
                     CASE 
                         WHEN m.reliability >= 8 THEN 20
                         WHEN m.reliability >= 7 THEN 15
                         ELSE 10
                     END as reliability_score,
                     
                     CASE m.price_range
                         WHEN 'económico' THEN 5
                         WHEN 'medio-bajo' THEN 10
                         WHEN 'medio' THEN 15
                         WHEN 'medio-alto' THEN 20
                         WHEN 'alto' THEN 25
                         ELSE 15
                     END as brand_score
                
                // Aplicar bonificaciones demográficas
                WITH a, m, t, c, tr, reliability_score, brand_score,
                     CASE 
                         WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] AND t.categoria = 'SUV' THEN 15
                         WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] AND t.categoria = 'Sedán' THEN 10
                         WHEN $gender = 'masculino' AND $age_range = '18-25' AND t.categoria IN ['Coupé', 'Convertible'] THEN 8
                         WHEN $age_range IN ['46-55', '56+'] AND m.nombre IN ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus'] THEN 12
                         ELSE 0
                     END as demographic_bonus
                
                WITH a, m, t, c, tr, 
                     reliability_score + brand_score + demographic_bonus + 
                     (CASE WHEN a.trim_level = 'Premium' THEN 5 ELSE 0 END) as total_score
                
                RETURN 
                    a.id as id,
                    a.modelo as model,
                    m.nombre as brand,
                    a.año as year,
                    a.precio as price,
                    t.categoria as type,
                    c.tipo as fuel_type,
                    tr.tipo as transmission,
                    a.caracteristicas as features,
                    a.segmento as segment,
                    total_score as similarity_score
                
                ORDER BY total_score DESC, a.precio ASC
                LIMIT 10
                """
                
                # Ejecutar consulta
                params['gender'] = gender
                params['age_range'] = age_range
                
                logger.info(f"🔍 Ejecutando consulta Neo4j con parámetros: {params}")
                result = session.run(cypher_query, params)
                
                recommendations = []
                for record in result:
                    car = {
                        'id': record['id'],
                        'name': f"{record['brand']} {record['model']} {record['year']}",
                        'model': record['model'],
                        'brand': record['brand'],
                        'year': record['year'],
                        'price': record['price'],
                        'type': record['type'],
                        'fuel': record['fuel_type'],
                        'transmission': record['transmission'],
                        'features': record['features'] or [],
                        'segment': record['segment'],
                        'similarity_score': float(record['similarity_score']),
                        'image': None  # Placeholder para imágenes
                    }
                    recommendations.append(car)
                
                logger.info(f"✅ Obtenidas {len(recommendations)} recomendaciones de Neo4j")
                
                # Si no hay resultados, relajar filtros
                if not recommendations:
                    logger.info("🔄 No hay resultados, intentando con filtros relajados...")
                    return self.get_relaxed_recommendations(session, gender, age_range)
                
                return recommendations
                
        except Exception as e:
            logger.error(f"❌ Error en consulta Neo4j: {e}")
            traceback.print_exc()
            return self.get_fallback_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
    
    def get_relaxed_recommendations(self, session, gender=None, age_range=None):
        """Obtener recomendaciones con filtros relajados"""
        try:
            cypher_query = """
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            
            WITH a, m, t, c, tr,
                 m.reliability * 2 + 
                 (CASE WHEN $gender = 'femenino' AND t.categoria = 'SUV' THEN 15 ELSE 0 END) +
                 (CASE WHEN $gender = 'masculino' AND t.categoria = 'Coupé' THEN 8 ELSE 0 END) +
                 (CASE WHEN m.nombre IN ['Toyota', 'Honda', 'BMW', 'Mercedes-Benz'] THEN 10 ELSE 5 END) as score
            
            RETURN 
                a.id as id,
                a.modelo as model,
                m.nombre as brand,
                a.año as year,
                a.precio as price,
                t.categoria as type,
                c.tipo as fuel_type,
                tr.tipo as transmission,
                a.caracteristicas as features,
                a.segmento as segment,
                score as similarity_score
            
            ORDER BY score DESC, a.precio ASC
            LIMIT 8
            """
            
            result = session.run(cypher_query, gender=gender, age_range=age_range)
            
            recommendations = []
            for record in result:
                car = {
                    'id': record['id'],
                    'name': f"{record['brand']} {record['model']} {record['year']}",
                    'model': record['model'],
                    'brand': record['brand'],
                    'year': record['year'],
                    'price': record['price'],
                    'type': record['type'],
                    'fuel': record['fuel_type'],
                    'transmission': record['transmission'],
                    'features': record['features'] or [],
                    'segment': record['segment'],
                    'similarity_score': float(record['similarity_score']),
                    'image': None
                }
                recommendations.append(car)
            
            logger.info(f"✅ Obtenidas {len(recommendations)} recomendaciones relajadas")
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ Error en recomendaciones relajadas: {e}")
            return []
    
    def get_fallback_recommendations(self, brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
        """Recomendaciones de respaldo cuando Neo4j no está disponible"""
        logger.info("🔄 Generando recomendaciones de respaldo con personalización")
        
        # Base de datos de autos de ejemplo
        sample_cars = [
            {
                'id': 'fallback_1',
                'name': 'Toyota Corolla 2024',
                'model': 'Corolla',
                'brand': 'Toyota',
                'year': 2024,
                'price': 25000,
                'type': 'Sedán',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['Aire acondicionado', 'Bluetooth', 'Cámara trasera', 'Toyota Safety Sense'],
                'segment': 'compacto',
                'similarity_score': 85.0,
                'image': None
            },
            {
                'id': 'fallback_2',
                'name': 'Honda CR-V 2024',
                'model': 'CR-V',
                'brand': 'Honda',
                'year': 2024,
                'price': 35000,
                'type': 'SUV',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['Honda Sensing', 'Pantalla táctil', 'Asientos cómodos', 'Amplio maletero'],
                'segment': 'compacto',
                'similarity_score': 80.0,
                'image': None
            },
            {
                'id': 'fallback_3',
                'name': 'BMW 3 Series 2024',
                'model': '3 Series',
                'brand': 'BMW',
                'year': 2024,
                'price': 45000,
                'type': 'Sedán',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['iDrive', 'Asientos de cuero', 'Faros LED', 'Performance premium'],
                'segment': 'lujo',
                'similarity_score': 75.0,
                'image': None
            },
            {
                'id': 'fallback_4',
                'name': 'Tesla Model Y 2024',
                'model': 'Model Y',
                'brand': 'Tesla',
                'year': 2024,
                'price': 48000,
                'type': 'SUV',
                'fuel': 'Eléctrico',
                'transmission': 'Automática',
                'features': ['Piloto automático', 'Pantalla táctil 15"', 'Supercargador', 'Tecnología avanzada'],
                'segment': 'eléctrico',
                'similarity_score': 78.0,
                'image': None
            },
            {
                'id': 'fallback_5',
                'name': 'Mercedes-Benz C-Class 2024',
                'model': 'C-Class',
                'brand': 'Mercedes-Benz',
                'year': 2024,
                'price': 48000,
                'type': 'Sedán',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['MBUX', 'Asientos de cuero', 'Sonido Burmester', 'Lujo alemán'],
                'segment': 'lujo',
                'similarity_score': 72.0,
                'image': None
            },
            {
                'id': 'fallback_6',
                'name': 'Mazda CX-5 2024',
                'model': 'CX-5',
                'brand': 'Mazda',
                'year': 2024,
                'price': 32000,
                'type': 'SUV',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['i-ACTIVSENSE', 'Diseño KODO', 'Interior premium', 'Manejo deportivo'],
                'segment': 'compacto',
                'similarity_score': 70.0,
                'image': None
            },
            {
                'id': 'fallback_7',
                'name': 'Ford Mustang 2024',
                'model': 'Mustang',
                'brand': 'Ford',
                'year': 2024,
                'price': 38000,
                'type': 'Coupé',
                'fuel': 'Gasolina',
                'transmission': 'Manual',
                'features': ['Motor V8', 'Diseño icónico', 'Performance sport', 'Sistema de escape'],
                'segment': 'deportivo',
                'similarity_score': 68.0,
                'image': None
            },
            {
                'id': 'fallback_8',
                'name': 'Hyundai Tucson 2024',
                'model': 'Tucson',
                'brand': 'Hyundai',
                'year': 2024,
                'price': 28000,
                'type': 'SUV',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['SmartSense', 'Garantía 10 años', 'Diseño moderno', 'Valor excepcional'],
                'segment': 'compacto',
                'similarity_score': 65.0,
                'image': None
            }
        ]
        
        # Filtrar por preferencias
        filtered_cars = []
        for car in sample_cars:
            include = True
            
            # Filtrar por marca
            if brands and len(brands) > 0 and car['brand'] not in brands:
                include = False
            
            # Filtrar por presupuesto
            if budget and include:
                try:
                    if isinstance(budget, str) and '-' in budget:
                        min_price, max_price = budget.split('-')
                        if not (int(min_price) <= car['price'] <= int(max_price)):
                            include = False
                    elif isinstance(budget, dict):
                        if 'min' in budget and budget['min'] and car['price'] < int(budget['min']):
                            include = False
                        if 'max' in budget and budget['max'] and car['price'] > int(budget['max']):
                            include = False
                except (ValueError, TypeError):
                    pass
            
            # Filtrar por combustible
            if fuel and len(fuel) > 0 and car['fuel'] not in fuel:
                include = False
            
            # Filtrar por tipo
            if types and len(types) > 0 and car['type'] not in types:
                include = False
            
            # Filtrar por transmisión
            if transmission and len(transmission) > 0 and car['transmission'] not in transmission:
                include = False
            
            if include:
                filtered_cars.append(car.copy())
        
        # Aplicar personalización demográfica
        for car in filtered_cars:
            demographic_bonus = 0
            
            # Bonificaciones por género y edad
            if gender == 'femenino':
                if age_range in ['26-35', '36-45'] and car['type'] == 'SUV':
                    demographic_bonus += 15
                elif age_range in ['26-35', '36-45'] and car['type'] == 'Sedán':
                    demographic_bonus += 10
            elif gender == 'masculino':
                if age_range == '18-25' and car['type'] in ['Coupé', 'Convertible']:
                    demographic_bonus += 8
            
            # Bonificación por edad madura y marcas premium
            if age_range in ['46-55', '56+'] and car['brand'] in ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus']:
                demographic_bonus += 12
            
            # Aplicar bonificación
            car['similarity_score'] += demographic_bonus
            if demographic_bonus > 0:
                car['demographic_bonus'] = demographic_bonus
        
        # Ordenar por puntuación
        filtered_cars.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Limitar a 8 resultados
        result = filtered_cars[:8]
        
        logger.info(f"✅ Generadas {len(result)} recomendaciones de respaldo con personalización")
        return result


# Instancia global del sistema de recomendaciones
recommendation_system = CarRecommendationSystem()

def get_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
    """
    Función principal de recomendaciones - CORREGIDA para aceptar 7 parámetros
    
    Args:
        brands: Lista de marcas preferidas
        budget: Presupuesto (string "min-max" o dict {"min": x, "max": y})
        fuel: Lista de tipos de combustible
        types: Lista de tipos de vehículo
        transmission: Lista de tipos de transmisión
        gender: Género del usuario ('masculino', 'femenino')
        age_range: Rango de edad ('18-25', '26-35', '36-45', '46-55', '56+')
    
    Returns:
        Lista de recomendaciones de autos
    """
    try:
        logger.info("🎯 INICIANDO SISTEMA DE RECOMENDACIONES")
        logger.info("=" * 50)
        logger.info(f"📊 Parámetros recibidos:")
        logger.info(f"  🏷️  Marcas: {brands}")
        logger.info(f"  💰 Presupuesto: {budget}")
        logger.info(f"  ⛽ Combustible: {fuel}")
        logger.info(f"  🚗 Tipos: {types}")
        logger.info(f"  ⚙️  Transmisión: {transmission}")
        logger.info(f"  👤 Género: {gender}")
        logger.info(f"  🎂 Edad: {age_range}")
        
        # Obtener recomendaciones del sistema
        recommendations = recommendation_system.get_recommendations_from_neo4j(
            brands=brands,
            budget=budget,
            fuel=fuel,
            types=types,
            transmission=transmission,
            gender=gender,
            age_range=age_range
        )
        
        logger.info(f"✅ RECOMENDACIONES GENERADAS: {len(recommendations)}")
        for i, car in enumerate(recommendations, 1):
            logger.info(f"  {i}. {car['name']} - ${car['price']:,} - Score: {car['similarity_score']:.1f}")
        
        logger.info("=" * 50)
        return recommendations
        
    except Exception as e:
        logger.error(f"❌ ERROR EN get_recommendations: {e}")
        traceback.print_exc()
        
        # Retornar recomendaciones de respaldo
        fallback = recommendation_system.get_fallback_recommendations(
            brands, budget, fuel, types, transmission, gender, age_range
        )
        logger.info(f"🔄 Retornando {len(fallback)} recomendaciones de respaldo")
        return fallback

def test_recommendations():
    """Función de prueba para verificar el sistema"""
    print("🧪 PROBANDO SISTEMA DE RECOMENDACIONES")
    print("=" * 60)
    
    # Prueba 1: Mujer joven que necesita SUV
    print("\n👩 Prueba 1: Mujer 26-35 años, busca SUV")
    results1 = get_recommendations(
        brands=["Toyota", "Honda", "Mazda"],
        budget="25000-45000",
        fuel=["Gasolina", "Híbrido"],
        types=["SUV"],
        transmission=["Automática"],
        gender="femenino",
        age_range="26-35"
    )
    print(f"Resultados: {len(results1)} autos encontrados")
    
    # Prueba 2: Hombre joven deportivo
    print("\n👨 Prueba 2: Hombre 18-25 años, busca deportivo")
    results2 = get_recommendations(
        brands=["BMW", "Ford", "Chevrolet"],
        budget="30000-60000",
        fuel=["Gasolina"],
        types=["Coupé", "Sedán"],
        transmission=["Manual", "Automática"],
        gender="masculino",
        age_range="18-25"
    )
    print(f"Resultados: {len(results2)} autos encontrados")
    
    # Prueba 3: Persona madura con presupuesto alto
    print("\n🧓 Prueba 3: Persona 46+ años, busca lujo")
    results3 = get_recommendations(
        brands=["Mercedes-Benz", "BMW", "Lexus"],
        budget="45000-80000",
        fuel=["Gasolina", "Híbrido"],
        types=["Sedán", "SUV"],
        transmission=["Automática"],
        gender="masculino",
        age_range="46-55"
    )
    print(f"Resultados: {len(results3)} autos encontrados")
    
    print("\n✅ Pruebas completadas")

if __name__ == "__main__":
    # Ejecutar pruebas si se ejecuta directamente
    test_recommendations()
    
    # Cerrar conexión
    recommendation_system.close()