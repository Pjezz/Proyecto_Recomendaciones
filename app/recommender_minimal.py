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
                # Normalizar parámetros de entrada para asegurar que sean listas
                def normalize_param(param):
                    if param is None:
                        return []
                    elif isinstance(param, str):
                        return [param]
                    elif isinstance(param, list):
                        return param
                    else:
                        return []
                
                # Normalizar todos los parámetros
                brands = normalize_param(brands)
                fuel = normalize_param(fuel)
                types = normalize_param(types)
                transmission = normalize_param(transmission)
                
                logger.info(f"🔍 Parámetros normalizados:")
                logger.info(f"  Marcas: {brands}")
                logger.info(f"  Combustible: {fuel}")
                logger.info(f"  Tipos: {types}")
                logger.info(f"  Transmisión: {transmission}")
                
                # Obtener tanto resultados filtrados como recomendaciones inteligentes
                filtered_results = self.get_filtered_results(session, brands, budget, fuel, types, transmission, gender, age_range)
                intelligent_recommendations = self.get_intelligent_recommendations(session, brands, budget, fuel, types, transmission, gender, age_range)
                
                # Combinar y marcar tipos
                all_results = []
                
                # Marcar resultados filtrados
                for car in filtered_results:
                    car['match_type'] = 'filtered'
                    car['similarity_score'] = max(car.get('similarity_score', 0), 85)  # Mínimo 85 para filtrados
                    all_results.append(car)
                
                # Marcar recomendaciones inteligentes
                for car in intelligent_recommendations:
                    car['match_type'] = 'recommended'
                    car['similarity_score'] = min(car.get('similarity_score', 0), 84)  # Máximo 84 para recomendaciones
                    all_results.append(car)
                
                logger.info(f"✅ Obtenidos {len(filtered_results)} filtrados + {len(intelligent_recommendations)} recomendaciones de Neo4j")
                
                # Si no hay resultados, usar respaldo
                if not all_results:
                    logger.info("🔄 No hay resultados, usando respaldo...")
                    return self.get_fallback_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
                
                return all_results
                
        except Exception as e:
            logger.error(f"❌ Error en consulta Neo4j: {e}")
            traceback.print_exc()
            return self.get_fallback_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
    
    def get_filtered_results(self, session, brands, budget, fuel, types, transmission, gender, age_range):
        """Obtener resultados que coinciden exactamente con los filtros"""
        try:
            # Construir consulta para coincidencias exactas
            conditions = []
            params = {}
            
            if brands and len(brands) > 0:
                conditions.append("m.nombre IN $brands")
                params['brands'] = brands
            
            if budget:
                if isinstance(budget, str) and '-' in budget:
                    min_price, max_price = budget.split('-')
                    conditions.append("a.precio >= $min_price AND a.precio <= $max_price")
                    params['min_price'] = int(min_price)
                    params['max_price'] = int(max_price)
            
            if fuel and len(fuel) > 0:
                conditions.append("c.tipo IN $fuel")
                params['fuel'] = fuel
            
            if types and len(types) > 0:
                conditions.append("t.categoria IN $types")
                params['types'] = types
            
            if transmission and len(transmission) > 0:
                conditions.append("tr.tipo IN $transmission")
                params['transmission'] = transmission
            
            # Si no hay condiciones, no devolver nada (evitar obtener toda la BD)
            if not conditions:
                logger.info("⚠️ No hay filtros específicos, no se devuelven resultados filtrados")
                return []
            
            where_clause = "WHERE " + " AND ".join(conditions)
            
            cypher_query = f"""
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            {where_clause}
            
            WITH a, m, t, c, tr,
                 85 + (m.reliability * 2) + 
                 (CASE WHEN a.trim_level = 'Premium' THEN 5 ELSE 0 END) +
                 (CASE 
                     WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] AND t.categoria = 'SUV' THEN 10
                     WHEN $gender = 'masculino' AND $age_range = '18-25' AND t.categoria IN ['Coupé', 'Convertible'] THEN 8
                     WHEN $age_range IN ['46-55', '56+'] AND m.nombre IN ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus'] THEN 8
                     ELSE 0
                 END) as filtered_score
            
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
                filtered_score as similarity_score
            
            ORDER BY filtered_score DESC, a.precio ASC
            LIMIT 6
            """
            
            params['gender'] = gender
            params['age_range'] = age_range
            
            logger.info(f"🔍 Ejecutando consulta de filtros exactos")
            logger.info(f"📊 Condiciones: {conditions}")
            logger.info(f"📋 Parámetros: {params}")
            
            result = session.run(cypher_query, params)
            
            filtered_cars = []
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
                filtered_cars.append(car)
            
            logger.info(f"🔍 Obtenidos {len(filtered_cars)} resultados filtrados")
            return filtered_cars
            
        except Exception as e:
            logger.error(f"❌ Error en filtrados: {e}")
            return []
    
    def get_intelligent_recommendations(self, session, brands, budget, fuel, types, transmission, gender, age_range):
        """Obtener recomendaciones inteligentes basadas en similitudes y demografía"""
        try:
            # Consulta más flexible para recomendaciones inteligentes
            cypher_query = """
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            
            // Calcular similitud con preferencias del usuario
            WITH a, m, t, c, tr,
                 // Score base por confiabilidad y marca
                 (m.reliability * 3) +
                 (CASE m.price_range
                     WHEN 'económico' THEN 5
                     WHEN 'medio-bajo' THEN 10
                     WHEN 'medio' THEN 15
                     WHEN 'medio-alto' THEN 20
                     WHEN 'alto' THEN 25
                     ELSE 10
                 END) +
                 
                 // Bonificación por coincidencia parcial con filtros
                 (CASE WHEN m.nombre IN $brands THEN 15 ELSE 
                      (CASE WHEN EXISTS { 
                          MATCH (m)-[:SIMILAR_A]->(similar:Marca) 
                          WHERE similar.nombre IN $brands 
                      } THEN 8 ELSE 0 END)
                  END) +
                 (CASE WHEN c.tipo IN $fuel THEN 10 ELSE 0 END) +
                 (CASE WHEN t.categoria IN $types THEN 10 ELSE 
                      (CASE WHEN t.categoria IN ['SUV', 'Crossover'] AND 'SUV' IN $types THEN 5 ELSE 0 END)
                  END) +
                 (CASE WHEN tr.tipo IN $transmission THEN 8 ELSE 0 END) +
                 
                 // Personalización demográfica inteligente
                 (CASE 
                     WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] THEN
                         (CASE WHEN t.categoria = 'SUV' THEN 20
                               WHEN t.categoria = 'Sedán' THEN 15
                               ELSE 5 END)
                     WHEN $gender = 'masculino' AND $age_range = '18-25' THEN
                         (CASE WHEN t.categoria IN ['Coupé', 'Convertible'] THEN 18
                               WHEN t.categoria = 'Sedán' THEN 12
                               ELSE 3 END)
                     WHEN $age_range IN ['46-55', '56+'] THEN
                         (CASE WHEN m.nombre IN ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus'] THEN 20
                               ELSE 5 END)
                     ELSE 5
                 END) as recommendation_score
            
            // Filtrar solo recomendaciones inteligentes (no coincidencias exactas)
            WHERE NOT (
                ($brands IS NULL OR SIZE($brands) = 0 OR m.nombre IN $brands) AND
                ($fuel IS NULL OR SIZE($fuel) = 0 OR c.tipo IN $fuel) AND
                ($types IS NULL OR SIZE($types) = 0 OR t.categoria IN $types) AND
                ($transmission IS NULL OR SIZE($transmission) = 0 OR tr.tipo IN $transmission)
            )
            
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
                recommendation_score as similarity_score
            
            ORDER BY recommendation_score DESC, a.precio ASC
            LIMIT 8
            """
            
            params = {
                'brands': brands if brands else [],
                'fuel': fuel if fuel else [],
                'types': types if types else [],
                'transmission': transmission if transmission else [],
                'gender': gender,
                'age_range': age_range
            }
            
            logger.info(f"🎯 Ejecutando consulta de recomendaciones inteligentes")
            logger.info(f"📊 Parámetros: {params}")
            
            result = session.run(cypher_query, params)
            
            recommended_cars = []
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
                    'similarity_score': min(float(record['similarity_score']), 84),  # Máximo 84 para recomendaciones
                    'image': None
                }
                recommended_cars.append(car)
            
            logger.info(f"🎯 Obtenidas {len(recommended_cars)} recomendaciones inteligentes")
            return recommended_cars
            
        except Exception as e:
            logger.error(f"❌ Error en recomendaciones inteligentes: {e}")
            return []
    
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
        logger.info("🔄 Generando recomendaciones de respaldo con separación filtrados/recomendaciones")
        
        # Base de datos expandida con las marcas que el usuario puede seleccionar
        sample_cars = [
            # BMW (marca seleccionada)
            {
                'id': 'bmw_1',
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
                'similarity_score': 92.0,
                'match_type': 'potential_filtered',
                'image': None
            },
            {
                'id': 'bmw_2',
                'name': 'BMW X3 2024',
                'model': 'X3',
                'brand': 'BMW',
                'year': 2024,
                'price': 52000,
                'type': 'SUV',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['xDrive', 'Tecnología BMW', 'Sistema de navegación', 'Control de voz'],
                'segment': 'lujo',
                'similarity_score': 90.0,
                'match_type': 'potential_filtered',
                'image': None
            },
            
            # Mercedes-Benz (marca seleccionada)
            {
                'id': 'mercedes_1',
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
                'similarity_score': 91.0,
                'match_type': 'potential_filtered',
                'image': None
            },
            
            # Mazda (marca seleccionada)
            {
                'id': 'mazda_1',
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
                'similarity_score': 89.0,
                'match_type': 'potential_filtered',
                'image': None
            },
            {
                'id': 'mazda_2',
                'name': 'Mazda 6 2024',
                'model': '6',
                'brand': 'Mazda',
                'year': 2024,
                'price': 28000,
                'type': 'Sedán',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['SkyActiv', 'Diseño elegante', 'Tecnología Mazda', 'Eficiencia'],
                'segment': 'medio',
                'similarity_score': 87.0,
                'match_type': 'potential_filtered',
                'image': None
            },
            
            # Subaru (marca seleccionada)
            {
                'id': 'subaru_1',
                'name': 'Subaru Outback 2024',
                'model': 'Outback',
                'brand': 'Subaru',
                'year': 2024,
                'price': 35000,
                'type': 'SUV',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['Symmetrical AWD', 'EyeSight', 'Aventurero', 'Seguridad Subaru'],
                'segment': 'aventura',
                'similarity_score': 88.0,
                'match_type': 'potential_filtered',
                'image': None
            },
            
            # Marcas similares (para recomendaciones)
            {
                'id': 'audi_1',
                'name': 'Audi A4 2024',
                'model': 'A4',
                'brand': 'Audi',
                'year': 2024,
                'price': 44000,
                'type': 'Sedán',
                'fuel': 'Gasolina',
                'transmission': 'Automática',
                'features': ['Quattro AWD', 'Virtual cockpit', 'Premium sound', 'Tecnología alemana'],
                'segment': 'lujo',
                'similarity_score': 78.0,
                'match_type': 'similar_tastes',
                'image': None
            },
            {
                'id': 'lexus_1',
                'name': 'Lexus ES 2024',
                'model': 'ES',
                'brand': 'Lexus',
                'year': 2024,
                'price': 46000,
                'type': 'Sedán',
                'fuel': 'Híbrido',
                'transmission': 'Automática',
                'features': ['Lexus Safety System', 'Lujo japonés', 'Confiabilidad', 'Confort premium'],
                'segment': 'lujo',
                'similarity_score': 76.0,
                'match_type': 'similar_tastes',
                'image': None
            },
            {
                'id': 'honda_1',
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
                'similarity_score': 74.0,
                'match_type': 'similar_tastes',
                'image': None
            },
            {
                'id': 'toyota_1',
                'name': 'Toyota Highlander 2024',
                'model': 'Highlander',
                'brand': 'Toyota',
                'year': 2024,
                'price': 40000,
                'type': 'SUV',
                'fuel': 'Híbrido',
                'transmission': 'Automática',
                'features': ['Toyota Safety Sense', 'Híbrido', 'Familiar', 'Confiabilidad japonesa'],
                'segment': 'familiar',
                'similarity_score': 72.0,
                'match_type': 'similar_tastes',
                'demographic_bonus': 8,
                'image': None
            }
        ]
        
        # Normalizar parámetros
        brands = brands if brands else []
        fuel = fuel if fuel else []
        types = types if types else []
        transmission = transmission if transmission else []
        
        # Separar en filtrados y recomendaciones
        filtered_results = []
        similar_tastes = []
        demographic_recs = []
        
        for car in sample_cars:
            car_copy = car.copy()
            
            # Verificar si debería ser filtrado exacto
            should_be_filtered = True
            
            if len(brands) > 0 and car['brand'] not in brands:
                should_be_filtered = False
            
            if len(fuel) > 0 and car['fuel'] not in fuel:
                should_be_filtered = False
            
            if len(types) > 0 and car['type'] not in types:
                should_be_filtered = False
            
            if len(transmission) > 0 and car['transmission'] not in transmission:
                should_be_filtered = False
            
            # Verificar presupuesto
            if budget and isinstance(budget, str) and '-' in budget:
                try:
                    min_price, max_price = budget.split('-')
                    if not (int(min_price) <= car['price'] <= int(max_price)):
                        should_be_filtered = False
                except (ValueError, TypeError):
                    pass
            
            # Aplicar personalización demográfica
            demographic_bonus = 0
            if gender == 'femenino':
                if age_range in ['26-35', '36-45'] and car['type'] == 'SUV':
                    demographic_bonus += 15
                elif age_range in ['26-35', '36-45'] and car['type'] == 'Sedán':
                    demographic_bonus += 10
            elif gender == 'masculino':
                if age_range == '18-25' and car['type'] in ['Coupé', 'Convertible']:
                    demographic_bonus += 12
            
            if age_range in ['46-55', '56+'] and car['brand'] in ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus']:
                demographic_bonus += 10
            
            car_copy['similarity_score'] += demographic_bonus
            if demographic_bonus > 0:
                car_copy['demographic_bonus'] = demographic_bonus
            
            # Clasificar
            if should_be_filtered:
                car_copy['match_type'] = 'filtered'
                car_copy['similarity_score'] = max(car_copy['similarity_score'], 85)
                filtered_results.append(car_copy)
            elif car.get('match_type') == 'similar_tastes':
                car_copy['match_type'] = 'recommended'
                car_copy['similarity_score'] = min(car_copy['similarity_score'], 84)
                similar_tastes.append(car_copy)
            elif demographic_bonus > 0:
                car_copy['match_type'] = 'recommended'
                car_copy['similarity_score'] = min(car_copy['similarity_score'], 84)
                demographic_recs.append(car_copy)
        
        # Ordenar y limitar
        filtered_results.sort(key=lambda x: x['similarity_score'], reverse=True)
        similar_tastes.sort(key=lambda x: x['similarity_score'], reverse=True)
        demographic_recs.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        filtered_results = filtered_results[:6]
        similar_tastes = similar_tastes[:6]
        demographic_recs = demographic_recs[:6]
        
        # Combinar para retornar
        all_results = filtered_results + similar_tastes + demographic_recs
        
        logger.info(f"✅ Generados {len(filtered_results)} filtrados + {len(similar_tastes)} gustos similares + {len(demographic_recs)} demográficas")
        return all_results

# Instancia global del sistema de recomendaciones
recommendation_system = CarRecommendationSystem()

def get_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
    """
    Función principal de recomendaciones
    
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
        logger.info(f"📊 Parámetros recibidos RAW:")
        logger.info(f"  🏷️  Marcas: {brands} (tipo: {type(brands)})")
        logger.info(f"  💰 Presupuesto: {budget} (tipo: {type(budget)})")
        logger.info(f"  ⛽ Combustible: {fuel} (tipo: {type(fuel)})")
        logger.info(f"  🚗 Tipos: {types} (tipo: {type(types)})")
        logger.info(f"  ⚙️  Transmisión: {transmission} (tipo: {type(transmission)})")
        logger.info(f"  👤 Género: {gender} (tipo: {type(gender)})")
        logger.info(f"  🎂 Edad: {age_range} (tipo: {type(age_range)})")
        
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