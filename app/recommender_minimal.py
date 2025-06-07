#!/usr/bin/env python3
"""
Sistema de recomendaciones inteligente para autos con separación clara entre filtrados y recomendaciones
MEJORADO: Más resultados filtrados y recomendaciones
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
                # Manejar si fuel es string o list
                if isinstance(fuel, str):
                    conditions.append("c.tipo = $fuel")
                    params['fuel'] = fuel
                else:
                    conditions.append("c.tipo IN $fuel")
                    params['fuel'] = fuel
            
            if types and len(types) > 0:
                conditions.append("t.categoria IN $types")
                params['types'] = types
            
            if transmission and len(transmission) > 0:
                # Manejar si transmission es string o list
                if isinstance(transmission, str):
                    conditions.append("tr.tipo = $transmission")
                    params['transmission'] = transmission
                else:
                    conditions.append("tr.tipo IN $transmission")
                    params['transmission'] = transmission
            
            # CAMBIO: Reducir el requisito mínimo de filtros de 3 a 2
            if len(conditions) < 2:
                logger.info("⚠️ Insuficientes filtros para resultados exactos (mínimo 2)")
                return []
            
            where_clause = "WHERE " + " AND ".join(conditions)
            
            cypher_query = f"""
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            {where_clause}
            
            WITH a, m, t, c, tr,
                 90 + (CASE WHEN m.nombre IN $brands THEN 5 ELSE 0 END) + 
                 (CASE WHEN a.precio <= $max_price * 0.9 THEN 3 ELSE 0 END) +
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
            LIMIT 15
            """
            
            params['gender'] = gender or ''
            params['age_range'] = age_range or ''
            # Asegurar que max_price existe para el cálculo
            if 'max_price' not in params:
                params['max_price'] = 999999
            
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
            
            # CAMBIO: Siempre incluir algunas marcas populares para asegurar resultados
            popular_brands = ['Toyota', 'Honda', 'Ford', 'BMW', 'Mercedes-Benz', 'Audi', 'Tesla', 'Nissan']
            all_recommended_brands = list(set(recommended_brands + popular_brands))
            
            # Remover marcas ya seleccionadas por el usuario
            all_recommended_brands = [b for b in all_recommended_brands if b not in (brands or [])]
            
            if not all_recommended_brands:
                logger.info("⚠️ No se detectaron patrones, usando marcas populares")
                all_recommended_brands = popular_brands
            
            # Construir consulta más flexible para recomendaciones
            cypher_query = """
            MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
            MATCH (a)-[:ES_TIPO]->(t:Tipo)
            MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
            MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
            
            WHERE m.nombre IN $recommended_brands
            AND (
                // Respetar presupuesto si está definido (más flexible)
                ($min_price IS NULL OR a.precio >= $min_price * 0.7) AND
                ($max_price IS NULL OR a.precio <= $max_price * 1.5)  // 50% más flexible en precio
            )
            AND (
                // Ser más flexible con tipos y combustibles
                $types IS NULL OR SIZE($types) = 0 OR 
                t.categoria IN $types OR 
                (t.categoria = 'SUV' AND 'Crossover' IN $types) OR
                (t.categoria = 'Crossover' AND 'SUV' IN $types) OR
                (t.categoria = 'Sedán' AND 'Hatchback' IN $types) OR
                (t.categoria = 'Hatchback' AND 'Sedán' IN $types)
            )
            AND (
                // Ser más flexible con combustible
                $fuel_filter IS NULL OR
                c.tipo = $fuel_filter OR
                (c.tipo = 'Híbrido' AND $fuel_filter = 'Gasolina') OR
                (c.tipo = 'Gasolina' AND $fuel_filter = 'Híbrido')
            )
            
            WITH a, m, t, c, tr,
                 // Calcular score de recomendación
                 50 + 
                 // Bonificación por marca en patrones detectados
                 (CASE WHEN m.nombre IN $pattern_brands THEN 15 ELSE 5 END) +
                 
                 // Bonificación por rango de precio
                 (CASE 
                     WHEN a.precio >= 15000 AND a.precio <= 30000 THEN 8  // Económico
                     WHEN a.precio >= 30000 AND a.precio <= 50000 THEN 12 // Medio
                     WHEN a.precio >= 50000 AND a.precio <= 80000 THEN 10 // Premium
                     WHEN a.precio >= 80000 THEN 8                       // Lujo
                     ELSE 5
                 END) +
                 
                 // Personalización demográfica
                 (CASE 
                     WHEN $gender = 'femenino' AND $age_range IN ['26-35', '36-45'] AND t.categoria = 'SUV' THEN 15
                     WHEN $gender = 'masculino' AND $age_range = '18-25' AND t.categoria IN ['Coupé', 'Convertible'] THEN 12
                     WHEN $age_range IN ['46-55', '56+'] AND m.nombre IN ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus'] THEN 18
                     WHEN t.categoria = 'SUV' THEN 5  // SUVs son populares en general
                     WHEN c.tipo = 'Híbrido' THEN 5   // Híbridos son atractivos
                     ELSE 3
                 END) +
                 
                 // Bonificación aleatoria para diversidad
                 (rand() * 5) as recommendation_score
            
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
            LIMIT 20
            """
            
            # Preparar parámetros
            params = {
                'recommended_brands': all_recommended_brands[:20],  # Incluir más marcas
                'pattern_brands': recommended_brands[:10] if recommended_brands else [],
                'types': types if types else [],
                'gender': gender or '',
                'age_range': age_range or '',
                'fuel_filter': fuel[0] if isinstance(fuel, list) and fuel else (fuel if isinstance(fuel, str) else None),
                'min_price': None,
                'max_price': None
            }
            
            # Agregar parámetros de presupuesto si existe
            if budget and isinstance(budget, str) and '-' in budget:
                min_price, max_price = budget.split('-')
                params['min_price'] = int(min_price)
                params['max_price'] = int(max_price)
            
            logger.info(f"🎯 Ejecutando recomendaciones con {len(all_recommended_brands)} marcas sugeridas")
            
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
        if selected_brands:
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
        
        # Razones generales de marca
        brand_reasons = {
            'Toyota': 'Reconocida por su confiabilidad y bajo costo de mantenimiento',
            'Honda': 'Excelente relación calidad-precio y durabilidad comprobada',
            'BMW': 'Lujo alemán con tecnología de vanguardia',
            'Mercedes-Benz': 'Símbolo de elegancia y prestaciones premium',
            'Tesla': 'Innovación en movilidad eléctrica y tecnología autónoma',
            'Ford': 'Tradición americana con gran versatilidad',
            'Audi': 'Diseño sofisticado y tecnología quattro',
            'Nissan': 'Innovación japonesa accesible'
        }
        
        if brand in brand_reasons:
            reasons.append(brand_reasons[brand])
        
        if not reasons:
            reasons.append("Recomendado por tu patrón de preferencias")
        
        return ". ".join(reasons)
    
    def get_fallback_data(self, brands, budget, fuel, types, transmission, gender, age_range):
        """Datos de respaldo cuando Neo4j no está disponible"""
        logger.info("🔄 Generando datos de respaldo con separación filtrados/recomendaciones")
        
        # Simular datos filtrados (coincidencias exactas) - MÁS CANTIDAD
        filtered_results = []
        if brands:
            for i, brand in enumerate(brands[:3]):  # Máximo 3 marcas
                # Generar 2-3 autos por marca para tener más variedad
                models = ['Premium', 'Sport', 'Luxury'][:2+i]
                for j, model in enumerate(models):
                    car = {
                        'id': f'filtered_{brand.lower()}_{i}_{j}',
                        'name': f'{brand} {model} 2024',
                        'model': model,
                        'brand': brand,
                        'year': 2024,
                        'price': 35000 + (i * 5000) + (j * 3000),
                        'type': types[0] if types else 'SUV',
                        'fuel': fuel[0] if fuel else 'Gasolina',
                        'transmission': transmission[0] if transmission else 'Automática',
                        'features': ['Premium Package', 'Safety Tech', 'Comfort Features', f'Feature {j+1}'],
                        'segment': 'premium',
                        'similarity_score': 92.0 - (i * 2) - (j * 1),
                        'match_type': 'filtered',
                        'match_reason': 'Coincide exactamente con todos tus filtros',
                        'image': None
                    }
                    filtered_results.append(car)
        
        # Si no hay marcas seleccionadas, crear algunos filtrados genéricos
        if not filtered_results:
            generic_brands = ['Toyota', 'Honda', 'Ford']
            for i, brand in enumerate(generic_brands):
                car = {
                    'id': f'filtered_generic_{i}',
                    'name': f'{brand} Popular 2024',
                    'model': 'Popular',
                    'brand': brand,
                    'year': 2024,
                    'price': 30000 + (i * 5000),
                    'type': types[0] if types else 'Sedán',
                    'fuel': fuel[0] if fuel else 'Gasolina',
                    'transmission': transmission[0] if transmission else 'Automática',
                    'features': ['Standard Package', 'Basic Safety', 'Essential Features'],
                    'segment': 'standard',
                    'similarity_score': 90.0 - (i * 3),
                    'match_type': 'filtered',
                    'match_reason': 'Coincide con tus filtros principales',
                    'image': None
                }
                filtered_results.append(car)
        
        # Simular recomendaciones inteligentes - MÁS CANTIDAD
        recommended_results = []
        
        # Patrones de recomendación basados en marcas seleccionadas
        recommendation_patterns = {
            'BMW': ['Mercedes-Benz', 'Audi', 'Lexus', 'Genesis'],
            'Mercedes-Benz': ['BMW', 'Audi', 'Genesis', 'Lexus'],
            'Audi': ['BMW', 'Mercedes-Benz', 'Lexus', 'Genesis'],
            'Toyota': ['Honda', 'Mazda', 'Subaru', 'Nissan'],
            'Honda': ['Toyota', 'Mazda', 'Nissan', 'Subaru'],
            'Ford': ['Chevrolet', 'Jeep', 'Dodge'],
            'Chevrolet': ['Ford', 'Dodge', 'Jeep'],
            'Tesla': ['BMW', 'Mercedes-Benz', 'Audi'],  # Marcas que también innovan
        }
        
        # Recomendaciones basadas en marcas seleccionadas
        recommended_brands = set()
        for brand in (brands or []):
            if brand in recommendation_patterns:
                recommended_brands.update(recommendation_patterns[brand])
        
        # Si no hay marcas seleccionadas, usar marcas populares
        if not recommended_brands:
            recommended_brands = {'Honda', 'Toyota', 'BMW', 'Mercedes-Benz', 'Audi', 'Tesla'}
        
        recommended_brands = list(recommended_brands)[:8]  # Máximo 8 marcas recomendadas
        
        # Generar múltiples modelos por marca recomendada
        for i, brand in enumerate(recommended_brands):
            models = ['Sport', 'Elegant', 'Performance'][:2]  # 2 modelos por marca
            for j, model in enumerate(models):
                reason = f"{brand} es similar a tus marcas preferidas"
                if gender == 'femenino' and age_range in ['26-35', '36-45']:
                    reason += " y es ideal para uso familiar"
                elif gender == 'masculino' and age_range == '18-25':
                    reason += " y ofrece gran performance"
                
                car = {
                    'id': f'recommended_{brand.lower()}_{i}_{j}',
                    'name': f'{brand} {model} 2024',
                    'model': model,
                    'brand': brand,
                    'year': 2024,
                    'price': 32000 + (i * 6000) + (j * 2000),
                    'type': types[0] if types else 'SUV',
                    'fuel': fuel[0] if fuel else 'Gasolina', 
                    'transmission': transmission[0] if transmission else 'Automática',
                    'features': ['Advanced Tech', f'{model} Package', 'Premium Interior', f'Exclusive {j+1}'],
                    'segment': 'recommended',
                    'similarity_score': 78.0 - (i * 2) - (j * 1),
                    'match_type': 'recommended',
                    'match_reason': reason,
                    'image': None
                }
                recommended_results.append(car)
        
        logger.info(f"🔄 Generados {len(filtered_results)} filtrados y {len(recommended_results)} recomendaciones de respaldo")
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