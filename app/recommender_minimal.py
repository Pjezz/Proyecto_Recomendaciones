#!/usr/bin/env python3
"""
Sistema de recomendaciones inteligente para autos con separación clara entre filtrados y recomendaciones
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
    
    def get_brand_patterns(self, selected_brands):
        """Analizar patrones en las marcas seleccionadas para hacer recomendaciones inteligentes"""
        if not selected_brands:
            return []
        
        # Definir grupos de marcas por características
        brand_groups = {
            'german_luxury': ['BMW', 'Mercedes-Benz', 'Audi', 'Porsche', 'Volkswagen'],
            'japanese_reliable': ['Toyota', 'Honda', 'Mazda', 'Nissan', 'Subaru', 'Lexus'],
            'american_power': ['Ford', 'Chevrolet', 'Dodge', 'Cadillac'],
            'korean_value': ['Hyundai', 'Kia', 'Genesis'],
            'luxury_premium': ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Genesis', 'Porsche'],
            'electric_innovative': ['Tesla', 'BMW', 'Mercedes-Benz', 'Audi'],
            'sporty_performance': ['BMW', 'Mercedes-Benz', 'Audi', 'Ford', 'Chevrolet', 'Mazda']
        }
        
        # Identificar patrones en las marcas seleccionadas
        detected_patterns = []
        for pattern_name, brands_in_pattern in brand_groups.items():
            # Si al menos 50% de las marcas seleccionadas están en este patrón
            overlap = len(set(selected_brands) & set(brands_in_pattern))
            if overlap >= len(selected_brands) * 0.5:
                detected_patterns.append(pattern_name)
        
        # Generar recomendaciones basadas en patrones
        recommended_brands = set()
        for pattern in detected_patterns:
            recommended_brands.update(brand_groups[pattern])
        
        # Remover marcas ya seleccionadas
        recommended_brands = list(recommended_brands - set(selected_brands))
        
        logger.info(f"🔍 Patrones detectados: {detected_patterns}")
        logger.info(f"🎯 Marcas recomendadas: {recommended_brands[:8]}")
        
        return recommended_brands
    
    def get_filtered_cars(self, session, brands, budget, fuel, types, transmission, gender, age_range):
        """Obtener autos que coinciden EXACTAMENTE con todos los filtros del usuario"""
        try:
            # Construir condiciones de filtro estrictas
            conditions = []
            params = {}
            
            if brands and len(brands) > 0:
                conditions.append("m.nombre IN $brands")
                params['brands'] = brands
            
            if budget and isinstance(budget, str) and '-' in budget:
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
            
            # Si no hay condiciones suficientes, no retornar nada
            if len(conditions) < 3:  # Al menos 3 filtros deben estar presentes
                logger.info("⚠️ Insuficientes filtros para resultados exactos")
                return []
            
            where_clause = "WHERE " + " AND ".join(conditions)
            
            cypher_query = f"""
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            {where_clause}
            
            WITH a, m, t, c, tr,
                 90 + (m.reliability * 2) + 
                 (CASE WHEN a.trim_level = 'Premium' THEN 5 ELSE 0 END) +
                 (CASE 
                     WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] AND t.categoria = 'SUV' THEN 8
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
            LIMIT 8
            """
            
            params['gender'] = gender
            params['age_range'] = age_range
            
            logger.info(f"🔍 Ejecutando consulta de filtros exactos")
            logger.info(f"📋 Condiciones: {len(conditions)} filtros aplicados")
            
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
                    'match_type': 'filtered',
                    'match_reason': 'Coincide exactamente con todos tus filtros',
                    'image': None
                }
                filtered_cars.append(car)
            
            logger.info(f"🔍 Obtenidos {len(filtered_cars)} resultados filtrados exactos")
            return filtered_cars
            
        except Exception as e:
            logger.error(f"❌ Error en filtrados exactos: {e}")
            return []
    
    def get_smart_recommendations(self, session, brands, budget, fuel, types, transmission, gender, age_range):
        """Obtener recomendaciones inteligentes basadas en patrones de gustos"""
        try:
            # Obtener marcas recomendadas basadas en patrones
            recommended_brands = self.get_brand_patterns(brands)
            
            if not recommended_brands:
                logger.info("⚠️ No se detectaron patrones para recomendaciones")
                return []
            
            # Construir consulta más flexible para recomendaciones
            cypher_query = """
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            
            WHERE m.nombre IN $recommended_brands
            AND (
                // Respetar presupuesto si está definido
                ($min_price IS NULL OR a.precio >= $min_price) AND
                ($max_price IS NULL OR a.precio <= $max_price * 1.3)  // 30% más flexible en precio
            )
            AND (
                // Preferir tipos seleccionados pero ser flexible
                $types IS NULL OR SIZE($types) = 0 OR 
                t.categoria IN $types OR 
                (t.categoria = 'SUV' AND 'Crossover' IN $types) OR
                (t.categoria = 'Crossover' AND 'SUV' IN $types)
            )
            
            WITH a, m, t, c, tr,
                 // Calcular score de recomendación
                 60 + (m.reliability * 3) +
                 (CASE m.price_range
                     WHEN 'económico' THEN 5
                     WHEN 'medio-bajo' THEN 8
                     WHEN 'medio' THEN 12
                     WHEN 'medio-alto' THEN 15
                     WHEN 'alto' THEN 18
                     ELSE 8
                 END) +
                 
                 // Bonificación por compatibilidad con gustos
                 (CASE 
                     WHEN m.nombre IN ['BMW', 'Mercedes-Benz', 'Audi'] AND $selected_luxury = true THEN 15
                     WHEN m.nombre IN ['Toyota', 'Honda', 'Mazda'] AND $selected_reliable = true THEN 12
                     WHEN m.nombre IN ['Ford', 'Chevrolet'] AND $selected_american = true THEN 10
                     ELSE 5
                 END) +
                 
                 // Personalización demográfica
                 (CASE 
                     WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] AND t.categoria = 'SUV' THEN 12
                     WHEN $gender = 'masculino' AND $age_range = '18-25' AND t.categoria IN ['Coupé', 'Convertible'] THEN 10
                     WHEN $age_range IN ['46-55', '56+'] AND m.nombre IN ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus'] THEN 15
                     ELSE 3
                 END) as recommendation_score
            
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
            LIMIT 10
            """
            
            # Detectar patrones para mejorar recomendaciones
            selected_luxury = any(brand in ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus'] for brand in brands)
            selected_reliable = any(brand in ['Toyota', 'Honda', 'Mazda'] for brand in brands)
            selected_american = any(brand in ['Ford', 'Chevrolet'] for brand in brands)
            
            # Preparar parámetros
            params = {
                'recommended_brands': recommended_brands[:15],  # Limitar para performance
                'types': types if types else [],
                'gender': gender,
                'age_range': age_range,
                'selected_luxury': selected_luxury,
                'selected_reliable': selected_reliable,
                'selected_american': selected_american,
                'min_price': None,
                'max_price': None
            }
            
            # Agregar parámetros de presupuesto si existe
            if budget and isinstance(budget, str) and '-' in budget:
                min_price, max_price = budget.split('-')
                params['min_price'] = int(min_price)
                params['max_price'] = int(max_price)
            
            logger.info(f"🎯 Ejecutando recomendaciones con {len(recommended_brands)} marcas sugeridas")
            logger.info(f"📊 Patrones detectados: Lujo={selected_luxury}, Confiable={selected_reliable}, Americano={selected_american}")
            
            result = session.run(cypher_query, params)
            
            recommended_cars = []
            for record in result:
                # Generar razón de recomendación personalizada
                brand = record['brand']
                match_reason = self.generate_recommendation_reason(brand, brands, gender, age_range)
                
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
                    'match_type': 'recommended',
                    'match_reason': match_reason,
                    'image': None
                }
                recommended_cars.append(car)
            
            logger.info(f"🎯 Obtenidas {len(recommended_cars)} recomendaciones inteligentes")
            return recommended_cars
            
        except Exception as e:
            logger.error(f"❌ Error en recomendaciones inteligentes: {e}")
            return []
    
    def generate_recommendation_reason(self, brand, selected_brands, gender, age_range):
        """Generar razón personalizada para la recomendación"""
        reasons = []
        
        # Analizar patrones de marca
        if any(selected_brand in ['BMW', 'Mercedes-Benz', 'Audi'] for selected_brand in selected_brands):
            if brand in ['BMW', 'Mercedes-Benz', 'Audi', 'Lexus', 'Genesis']:
                reasons.append(f"{brand} es similar a tus marcas premium seleccionadas")
        
        if any(selected_brand in ['Toyota', 'Honda', 'Mazda'] for selected_brand in selected_brands):
            if brand in ['Toyota', 'Honda', 'Mazda', 'Nissan', 'Subaru']:
                reasons.append(f"{brand} comparte la confiabilidad japonesa que prefieres")
        
        if any(selected_brand in ['Ford', 'Chevrolet'] for selected_brand in selected_brands):
            if brand in ['Ford', 'Chevrolet', 'Dodge']:
                reasons.append(f"{brand} mantiene el espíritu americano de tus selecciones")
        
        # Razones demográficas
        if gender == 'femenino' and age_range in ['26-35', '36-45']:
            reasons.append("Ideal para tu perfil familiar")
        elif gender == 'masculino' and age_range == '18-25':
            reasons.append("Perfecto para tu estilo dinámico")
        elif age_range in ['46-55', '56+']:
            reasons.append("Enfocado en confort y prestigio")
        
        if not reasons:
            reasons.append("Recomendado por tu patrón de preferencias")
        
        return ". ".join(reasons)
    
    def get_fallback_data(self, brands, budget, fuel, types, transmission, gender, age_range):
        """Datos de respaldo cuando Neo4j no está disponible"""
        logger.info("🔄 Generando datos de respaldo con separación filtrados/recomendaciones")
        
        # Simular datos filtrados (coincidencias exactas)
        filtered_results = []
        if brands:
            for i, brand in enumerate(brands[:3]):  # Máximo 3 marcas
                car = {
                    'id': f'filtered_{brand.lower()}_{i}',
                    'name': f'{brand} Premium 2024',
                    'model': 'Premium',
                    'brand': brand,
                    'year': 2024,
                    'price': 35000 + (i * 5000),
                    'type': types[0] if types else 'SUV',
                    'fuel': fuel[0] if fuel else 'Gasolina',
                    'transmission': transmission[0] if transmission else 'Automática',
                    'features': ['Premium Package', 'Safety Tech', 'Comfort Features'],
                    'segment': 'premium',
                    'similarity_score': 92.0 - (i * 2),
                    'match_type': 'filtered',
                    'match_reason': 'Coincide exactamente con todos tus filtros',
                    'image': None
                }
                filtered_results.append(car)
        
        # Simular recomendaciones inteligentes
        recommended_results = []
        
        # Patrones de recomendación basados en marcas seleccionadas
        recommendation_patterns = {
            'BMW': ['Mercedes-Benz', 'Audi', 'Lexus'],
            'Mercedes-Benz': ['BMW', 'Audi', 'Genesis'],
            'Audi': ['BMW', 'Mercedes-Benz', 'Lexus'],
            'Toyota': ['Honda', 'Mazda', 'Subaru'],
            'Honda': ['Toyota', 'Mazda', 'Nissan'],
            'Ford': ['Chevrolet', 'Jeep'],
            'Chevrolet': ['Ford', 'Dodge']
        }
        
        recommended_brands = set()
        for brand in brands:
            if brand in recommendation_patterns:
                recommended_brands.update(recommendation_patterns[brand])
        
        recommended_brands = list(recommended_brands)[:4]  # Máximo 4 recomendaciones
        
        for i, brand in enumerate(recommended_brands):
            reason = f"{brand} es similar a tus marcas preferidas"
            if gender == 'femenino' and age_range in ['26-35', '36-45']:
                reason += " y es ideal para uso familiar"
            
            car = {
                'id': f'recommended_{brand.lower()}_{i}',
                'name': f'{brand} Sport 2024',
                'model': 'Sport',
                'brand': brand,
                'year': 2024,
                'price': 32000 + (i * 6000),
                'type': types[0] if types else 'SUV',
                'fuel': fuel[0] if fuel else 'Gasolina', 
                'transmission': transmission[0] if transmission else 'Automática',
                'features': ['Advanced Tech', 'Sport Package', 'Premium Interior'],
                'segment': 'sport',
                'similarity_score': 78.0 - (i * 3),
                'match_type': 'recommended',
                'match_reason': reason,
                'image': None
            }
            recommended_results.append(car)
        
        return filtered_results + recommended_results

# Instancia global del sistema de recomendaciones
recommendation_system = CarRecommendationSystem()

def get_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None, gender=None, age_range=None):
    """
    Función principal de recomendaciones que devuelve tanto filtrados como recomendaciones
    """
    try:
        logger.info("🎯 INICIANDO SISTEMA DE RECOMENDACIONES INTELIGENTE")
        logger.info("=" * 60)
        logger.info(f"📊 Entrada: brands={brands}, budget={budget}, fuel={fuel}")
        logger.info(f"         types={types}, transmission={transmission}")
        logger.info(f"         gender={gender}, age_range={age_range}")
        
        # Normalizar parámetros
        brands = brands if isinstance(brands, list) else [brands] if brands else []
        fuel = fuel if isinstance(fuel, list) else [fuel] if fuel else []
        types = types if isinstance(types, list) else [types] if types else []
        transmission = transmission if isinstance(transmission, list) else [transmission] if transmission else []
        
        if not recommendation_system.connected:
            logger.warning("❌ Neo4j no conectado, usando datos de respaldo")
            return recommendation_system.get_fallback_data(brands, budget, fuel, types, transmission, gender, age_range)
        
        with recommendation_system.driver.session() as session:
            # Obtener resultados filtrados (coincidencias exactas)
            filtered_cars = recommendation_system.get_filtered_cars(
                session, brands, budget, fuel, types, transmission, gender, age_range
            )
            
            # Obtener recomendaciones inteligentes
            recommended_cars = recommendation_system.get_smart_recommendations(
                session, brands, budget, fuel, types, transmission, gender, age_range
            )
            
            # Combinar resultados
            all_results = filtered_cars + recommended_cars
            
            logger.info(f"📊 RESULTADOS FINALES:")
            logger.info(f"  🔍 Filtrados exactos: {len(filtered_cars)}")
            logger.info(f"  🎯 Recomendaciones inteligentes: {len(recommended_cars)}")
            logger.info(f"  📋 Total: {len(all_results)}")
            
            if not all_results:
                logger.warning("⚠️ No se encontraron resultados, usando respaldo")
                return recommendation_system.get_fallback_data(brands, budget, fuel, types, transmission, gender, age_range)
            
            logger.info("=" * 60)
            return all_results
        
    except Exception as e:
        logger.error(f"❌ ERROR EN get_recommendations: {e}")
        traceback.print_exc()
        return recommendation_system.get_fallback_data(brands, budget, fuel, types, transmission, gender, age_range)

def test_recommendations():
    """Función de prueba"""
    print("🧪 PROBANDO SISTEMA DE RECOMENDACIONES SEPARADO")
    print("=" * 60)
    
    results = get_recommendations(
        brands=["BMW", "Toyota"],
        budget="30000-60000",
        fuel=["Gasolina"],
        types=["SUV"],
        transmission=["Automática"],
        gender="femenino",
        age_range="26-35"
    )
    
    filtered = [car for car in results if car['match_type'] == 'filtered']
    recommended = [car for car in results if car['match_type'] == 'recommended']
    
    print(f"\n🔍 FILTRADOS EXACTOS ({len(filtered)}):")
    for car in filtered:
        print(f"  - {car['name']} - ${car['price']:,} - {car['match_reason']}")
    
    print(f"\n🎯 RECOMENDACIONES ({len(recommended)}):")
    for car in recommended:
        print(f"  - {car['name']} - ${car['price']:,} - {car['match_reason']}")
    
    print("\n✅ Prueba completada")

if __name__ == "__main__":
    test_recommendations()
    recommendation_system.close()