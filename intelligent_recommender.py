#!/usr/bin/env python3
"""
Sistema de recomendaciones inteligente para automóviles
Usa algoritmos de similitud, perfiles demográficos y análisis de preferencias
para recomendar autos más allá de simples filtros
"""

from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any, Optional, Tuple
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntelligentCarRecommender:
    def __init__(self, uri: str, user: str, password: str):
        """Inicializar el sistema de recomendaciones inteligente"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Conexión exitosa al sistema de recomendaciones")
        except Exception as e:
            logger.error(f"Error conectando a Neo4j: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def get_demographic_profile(self, gender: str, age_range: str) -> str:
        """Determinar perfil demográfico basado en género y edad"""
        profile_mapping = {
            ("masculino", "18-25"): "hombre_18_25",
            ("masculino", "26-35"): "hombre_26_35", 
            ("masculino", "36-45"): "hombre_36_50",
            ("masculino", "46-55"): "hombre_36_50",
            ("masculino", "56+"): "hombre_51_plus",
            ("femenino", "18-25"): "mujer_18_25",
            ("femenino", "26-35"): "mujer_26_35",
            ("femenino", "36-45"): "mujer_36_50", 
            ("femenino", "46-55"): "mujer_36_50",
            ("femenino", "56+"): "mujer_51_plus",
        }
        
        return profile_mapping.get((gender, age_range), "hombre_26_35")
    
    def parse_budget_range(self, budget_str: str) -> Tuple[int, int]:
        """Convertir string de presupuesto a rango numérico"""
        try:
            if budget_str == "100000+":
                return (100000, 999999)
            elif "-" in budget_str:
                min_val, max_val = budget_str.split("-")
                return (int(min_val), int(max_val))
            else:
                return (0, int(budget_str))
        except Exception as e:
            logger.warning(f"Error parseando presupuesto '{budget_str}': {e}")
            return (0, 999999)
    
    def get_brand_similarities(self, selected_brands: List[str]) -> List[str]:
        """Obtener marcas similares a las seleccionadas"""
        if not selected_brands:
            return []
        
        with self.driver.session() as session:
            # Obtener marcas similares con sus pesos
            result = session.run("""
                MATCH (m1:Marca)-[r:SIMILAR_A]->(m2:Marca)
                WHERE m1.nombre IN $brands
                RETURN m2.nombre as marca_similar, 
                       avg(r.peso) as peso_promedio,
                       count(*) as frecuencia
                ORDER BY peso_promedio DESC, frecuencia DESC
                LIMIT 10
            """, brands=selected_brands)
            
            similar_brands = [record["marca_similar"] for record in result]
            
            # Filtrar marcas que ya están seleccionadas
            similar_brands = [brand for brand in similar_brands if brand not in selected_brands]
            
            logger.info(f"Marcas similares encontradas para {selected_brands}: {similar_brands[:5]}")
            return similar_brands
    
    def get_demographic_recommendations(self, gender: str, age_range: str) -> Dict[str, List[str]]:
        """Obtener recomendaciones basadas en perfil demográfico"""
        profile_id = self.get_demographic_profile(gender, age_range)
        
        with self.driver.session() as session:
            # Obtener marcas recomendadas para el perfil
            brands_result = session.run("""
                MATCH (p:PerfilDemografico {id: $profile_id})-[:RECOMIENDA_MARCA]->(m:Marca)
                RETURN m.nombre as marca
                ORDER BY m.nombre
            """, profile_id=profile_id)
            
            recommended_brands = [record["marca"] for record in brands_result]
            
            # Obtener tipos recomendados para el perfil
            types_result = session.run("""
                MATCH (p:PerfilDemografico {id: $profile_id})-[:RECOMIENDA_TIPO]->(t:Tipo)
                RETURN t.categoria as tipo
                ORDER BY t.categoria
            """, profile_id=profile_id)
            
            recommended_types = [record["tipo"] for record in types_result]
            
            logger.info(f"Perfil {profile_id}: marcas {recommended_brands[:3]}, tipos {recommended_types}")
            
            return {
                "brands": recommended_brands,
                "types": recommended_types,
                "profile_id": profile_id
            }
    
    def calculate_car_score(self, car: Dict, user_preferences: Dict, demographic_recs: Dict) -> float:
        """Calcular puntuación de recomendación para un auto específico"""
        score = 0.0
        max_score = 0.0
        
        # 1. Coincidencia exacta con marcas seleccionadas (peso: 30%)
        max_score += 30
        if car['marca'] in user_preferences.get('selected_brands', []):
            score += 30
            logger.debug(f"Marca exacta {car['marca']}: +30")
        
        # 2. Marca similar a las seleccionadas (peso: 20%)
        max_score += 20
        similar_brands = self.get_brand_similarities(user_preferences.get('selected_brands', []))
        if car['marca'] in similar_brands:
            # Puntuación decreciente basada en posición en la lista de similares
            position_score = max(0, 20 - (similar_brands.index(car['marca']) * 2))
            score += position_score
            logger.debug(f"Marca similar {car['marca']}: +{position_score}")
        
        # 3. Recomendación demográfica de marca (peso: 25%)
        max_score += 25
        if car['marca'] in demographic_recs.get('brands', []):
            score += 25
            logger.debug(f"Marca demográfica {car['marca']}: +25")
        
        # 4. Coincidencia de tipo de vehículo (peso: 20%)
        max_score += 20
        if user_preferences.get('types') and car['tipo'] in user_preferences['types']:
            score += 20
            logger.debug(f"Tipo exacto {car['tipo']}: +20")
        elif car['tipo'] in demographic_recs.get('types', []):
            score += 15
            logger.debug(f"Tipo demográfico {car['tipo']}: +15")
        
        # 5. Compatibilidad de combustible (peso: 15%)
        max_score += 15
        if user_preferences.get('fuel') and car['combustible'] == user_preferences['fuel']:
            score += 15
            logger.debug(f"Combustible exacto {car['combustible']}: +15")
        elif self.is_compatible_fuel(car['combustible'], user_preferences.get('fuel')):
            score += 10
            logger.debug(f"Combustible compatible {car['combustible']}: +10")
        
        # 6. Compatibilidad de transmisión (peso: 10%)
        max_score += 10
        if user_preferences.get('transmission') and car['transmision'] == user_preferences['transmission']:
            score += 10
            logger.debug(f"Transmisión exacta {car['transmision']}: +10")
        
        # 7. Ajuste de presupuesto (modificador: -20% a +10%)
        if user_preferences.get('budget_range'):
            min_budget, max_budget = user_preferences['budget_range']
            car_price = car['precio']
            
            if min_budget <= car_price <= max_budget:
                # Dentro del presupuesto: sin penalización
                budget_modifier = 1.0
                logger.debug(f"Precio ${car_price:,} dentro del presupuesto: sin modificador")
            elif car_price < min_budget:
                # Muy barato: ligero bonus (pueden ser opciones de valor)
                budget_modifier = 1.05
                logger.debug(f"Precio ${car_price:,} por debajo del presupuesto: +5%")
            else:
                # Fuera del presupuesto: penalización gradual
                over_budget_ratio = (car_price - max_budget) / max_budget
                budget_modifier = max(0.3, 1.0 - (over_budget_ratio * 0.5))
                logger.debug(f"Precio ${car_price:,} sobre presupuesto: {budget_modifier:.2f}x")
            
            score *= budget_modifier
        
        # 8. Bonus por características premium según perfil demográfico
        if self.has_premium_features_for_profile(car, demographic_recs.get('profile_id')):
            score *= 1.1
            logger.debug(f"Características premium para perfil: +10%")
        
        # Normalizar puntuación (0-100)
        normalized_score = (score / max_score) * 100 if max_score > 0 else 0
        
        logger.debug(f"Auto {car['modelo']}: {normalized_score:.1f}/100")
        return normalized_score
    
    def is_compatible_fuel(self, car_fuel: str, preferred_fuel: str) -> bool:
        """Verificar si dos tipos de combustible son compatibles"""
        if not preferred_fuel:
            return False
        
        compatibility_matrix = {
            "Gasolina": ["Híbrido"],  # Híbridos usan gasolina también
            "Híbrido": ["Gasolina", "Eléctrico"],  # Híbridos son puente entre ambos
            "Eléctrico": ["Híbrido"],  # Híbridos pueden interesar a quien busca eléctrico
            "Diésel": []  # Diésel es más específico
        }
        
        return car_fuel in compatibility_matrix.get(preferred_fuel, [])
    
    def has_premium_features_for_profile(self, car: Dict, profile_id: str) -> bool:
        """Verificar si el auto tiene características premium relevantes para el perfil"""
        if not profile_id or not car.get('caracteristicas'):
            return False
        
        premium_features_by_profile = {
            "hombre_18_25": ["deportivo", "sport", "turbo", "performance"],
            "hombre_26_35": ["tecnológico", "navegación", "bluetooth", "pantalla"],
            "hombre_36_50": ["lujo", "cuero", "premium", "sonido"],
            "hombre_51_plus": ["lujo", "confort", "premium", "automatico"],
            "mujer_18_25": ["bluetooth", "pantalla", "diseño", "compacto"],
            "mujer_26_35": ["seguridad", "familia", "espacio", "camara"],
            "mujer_36_50": ["seguridad", "familia", "espacio", "automatico"],
            "mujer_51_plus": ["confort", "automatico", "lujo", "facil"]
        }
        
        relevant_features = premium_features_by_profile.get(profile_id, [])
        car_features_text = " ".join(car['caracteristicas']).lower()
        
        return any(feature in car_features_text for feature in relevant_features)
    
    def get_intelligent_recommendations(self, 
                                      brands: List[str] = None, 
                                      budget: str = None,
                                      fuel: str = None, 
                                      types: List[str] = None, 
                                      transmission: str = None,
                                      gender: str = None, 
                                      age_range: str = None,
                                      limit: int = 15) -> List[Dict[str, Any]]:
        """
        Obtener recomendaciones inteligentes de autos
        
        Este método implementa un algoritmo de recomendación híbrido que combina:
        1. Filtrado colaborativo (similitudes entre marcas)
        2. Filtrado basado en contenido (características del auto)
        3. Recomendaciones demográficas (perfil de usuario)
        4. Sistemas de puntuación ponderada
        """
        
        logger.info("=== INICIANDO RECOMENDACIONES INTELIGENTES ===")
        logger.info(f"Entrada: brands={brands}, budget={budget}, fuel={fuel}")
        logger.info(f"         types={types}, transmission={transmission}")
        logger.info(f"         gender={gender}, age_range={age_range}")
        
        # Preparar preferencias del usuario
        user_preferences = {
            'selected_brands': brands or [],
            'fuel': fuel,
            'types': types or [],
            'transmission': transmission,
            'budget_range': self.parse_budget_range(budget) if budget else None
        }
        
        # Obtener recomendaciones demográficas
        demographic_recs = {}
        if gender and age_range:
            demographic_recs = self.get_demographic_recommendations(gender, age_range)
            logger.info(f"Perfil demográfico: {demographic_recs['profile_id']}")
        
        # Expandir marcas con similares
        all_relevant_brands = (user_preferences['selected_brands'] + 
                             self.get_brand_similarities(user_preferences['selected_brands']) +
                             demographic_recs.get('brands', []))
        
        # Remover duplicados manteniendo orden
        seen = set()
        all_relevant_brands = [x for x in all_relevant_brands if not (x in seen or seen.add(x))]
        
        logger.info(f"Marcas expandidas: {all_relevant_brands[:8]}")
        
        # Obtener autos candidatos con consulta amplia
        with self.driver.session() as session:
            # Consulta que obtiene más autos para poder aplicar algoritmo de recomendación
            query = """
                MATCH (a:Auto)
                OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
                OPTIONAL MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                OPTIONAL MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                WHERE (
                    // Incluir autos de marcas relevantes
                    m.nombre IN $relevant_brands
                    OR
                    // O autos que coincidan con preferencias demográficas
                    (t.categoria IN $demographic_types)
                    OR 
                    // O autos dentro del rango de presupuesto
                    ($min_price IS NULL OR a.precio >= $min_price) AND
                    ($max_price IS NULL OR a.precio <= $max_price * 1.3)
                )
                RETURN a.id as id, a.modelo as modelo, a.año as año, 
                       a.precio as precio, a.caracteristicas as caracteristicas,
                       a.segmento as segmento, a.trim_level as trim_level,
                       m.nombre as marca, t.categoria as tipo, 
                       c.tipo as combustible, tr.tipo as transmision
                ORDER BY a.precio ASC
                LIMIT $query_limit
            """
            
            min_price, max_price = user_preferences['budget_range'] if user_preferences['budget_range'] else (None, None)
            
            result = session.run(query, 
                               relevant_brands=all_relevant_brands[:15],
                               demographic_types=demographic_recs.get('types', []),
                               min_price=min_price,
                               max_price=max_price,
                               query_limit=limit * 3)  # Obtener más candidatos para filtrar
            
            candidates = []
            for record in result:
                car = {
                    'id': record['id'],
                    'name': f"{record['marca']} {record['modelo']} {record['año']}",
                    'modelo': record['modelo'],
                    'brand': record['marca'],
                    'marca': record['marca'],  # Alias para compatibilidad
                    'year': record['año'],
                    'año': record['año'],
                    'price': float(record['precio']) if record['precio'] else 0,
                    'precio': float(record['precio']) if record['precio'] else 0,
                    'type': record['tipo'] or 'No especificado',
                    'tipo': record['tipo'] or 'No especificado',
                    'fuel': record['combustible'] or 'No especificado',
                    'combustible': record['combustible'] or 'No especificado',
                    'transmission': record['transmision'] or 'No especificada',
                    'transmision': record['transmision'] or 'No especificada',
                    'features': record['caracteristicas'] or [],
                    'caracteristicas': record['caracteristicas'] or [],
                    'segmento': record['segmento'],
                    'trim_level': record['trim_level'],
                    'image': None
                }
                candidates.append(car)
        
        logger.info(f"Candidatos obtenidos: {len(candidates)}")
        
        # Aplicar algoritmo de puntuación a cada candidato
        scored_cars = []
        for car in candidates:
            score = self.calculate_car_score(car, user_preferences, demographic_recs)
            car['similarity_score'] = round(score, 2)
            car['recommendation_reason'] = self.generate_recommendation_reason(
                car, user_preferences, demographic_recs, score
            )
            scored_cars.append(car)
        
        # Ordenar por puntuación y aplicar diversificación
        scored_cars.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        # Aplicar diversificación para evitar repetir marcas/tipos
        final_recommendations = self.diversify_recommendations(scored_cars, limit)
        
        logger.info(f"Recomendaciones finales: {len(final_recommendations)}")
        for i, car in enumerate(final_recommendations[:5], 1):
            logger.info(f"{i}. {car['name']} - Score: {car['similarity_score']}")
        
        logger.info("=== RECOMENDACIONES COMPLETADAS ===")
        
        return final_recommendations
    
    def generate_recommendation_reason(self, car: Dict, user_preferences: Dict, 
                                     demographic_recs: Dict, score: float) -> str:
        """Generar explicación de por qué se recomienda este auto"""
        reasons = []
        
        if car['marca'] in user_preferences.get('selected_brands', []):
            reasons.append(f"Es de {car['marca']}, una de tus marcas seleccionadas")
        
        similar_brands = self.get_brand_similarities(user_preferences.get('selected_brands', []))
        if car['marca'] in similar_brands:
            reasons.append(f"{car['marca']} es similar a tus marcas preferidas")
        
        if car['marca'] in demographic_recs.get('brands', []):
            reasons.append(f"Recomendado para tu perfil demográfico")
        
        if user_preferences.get('types') and car['tipo'] in user_preferences['types']:
            reasons.append(f"Coincide con tu preferencia de {car['tipo']}")
        
        if car['tipo'] in demographic_recs.get('types', []):
            reasons.append(f"{car['tipo']} es ideal para tu perfil")
        
        if score >= 80:
            reasons.append("Excelente compatibilidad con tus preferencias")
        elif score >= 60:
            reasons.append("Buena opción considerando tus criterios")
        
        return ". ".join(reasons) if reasons else "Opción interesante a considerar"
    
    def diversify_recommendations(self, scored_cars: List[Dict], limit: int) -> List[Dict]:
        """
        Diversificar recomendaciones para evitar que todas sean de la misma marca/tipo
        Implementa un algoritmo de diversificación que balancea puntuación con variedad
        """
        if not scored_cars:
            return []
        
        selected = []
        used_brands = set()
        used_types = set()
        
        # Primera pasada: tomar los mejores evitando repetir marca
        for car in scored_cars:
            if len(selected) >= limit:
                break
            
            # Criterios de diversificación
            brand_penalty = len([c for c in selected if c['marca'] == car['marca']]) * 10
            type_penalty = len([c for c in selected if c['tipo'] == car['tipo']]) * 5
            
            # Aplicar penalización por diversidad
            diversity_score = car['similarity_score'] - brand_penalty - type_penalty
            
            # Aceptar si es suficientemente bueno o si añade diversidad
            if (diversity_score >= 40 or 
                (car['marca'] not in used_brands and len(selected) < limit * 0.7) or
                len(selected) < 3):  # Siempre incluir los 3 mejores
                
                selected.append(car)
                used_brands.add(car['marca'])
                used_types.add(car['tipo'])
        
        # Segunda pasada: llenar espacios restantes con los mejores disponibles
        remaining_slots = limit - len(selected)
        if remaining_slots > 0:
            remaining_cars = [car for car in scored_cars if car not in selected]
            selected.extend(remaining_cars[:remaining_slots])
        
        return selected[:limit]
    
    def get_fallback_recommendations(self, **kwargs) -> List[Dict]:
        """Recomendaciones de respaldo cuando no hay datos suficientes"""
        logger.warning("Usando recomendaciones de respaldo")
        
        fallback_cars = [
            {
                "id": "fallback_1",
                "name": "Toyota Corolla 2024",
                "modelo": "Corolla",
                "brand": "Toyota",
                "marca": "Toyota",
                "year": 2024,
                "año": 2024,
                "price": 25000,
                "precio": 25000,
                "type": "Sedán",
                "tipo": "Sedán",
                "fuel": "Gasolina",
                "combustible": "Gasolina",
                "transmission": "Automática",
                "transmision": "Automática",
                "features": ["Aire acondicionado", "Bluetooth", "Cámara trasera"],
                "caracteristicas": ["Aire acondicionado", "Bluetooth", "Cámara trasera"],
                "similarity_score": 75.0,
                "recommendation_reason": "Opción confiable y popular",
                "image": None
            },
            {
                "id": "fallback_2",
                "name": "Honda Civic 2024",
                "modelo": "Civic",
                "brand": "Honda",
                "marca": "Honda",
                "year": 2024,
                "año": 2024,
                "price": 27000,
                "precio": 27000,
                "type": "Sedán",
                "tipo": "Sedán",
                "fuel": "Gasolina",
                "combustible": "Gasolina",
                "transmission": "Manual",
                "transmision": "Manual",
                "features": ["Pantalla táctil", "Apple CarPlay", "Honda Sensing"],
                "caracteristicas": ["Pantalla táctil", "Apple CarPlay", "Honda Sensing"],
                "similarity_score": 72.0,
                "recommendation_reason": "Excelente relación calidad-precio",
                "image": None
            },
            {
                "id": "fallback_3",
                "name": "Tesla Model 3 2024",
                "modelo": "Model 3",
                "brand": "Tesla",
                "marca": "Tesla",
                "year": 2024,
                "año": 2024,
                "price": 42000,
                "precio": 42000,
                "type": "Sedán",
                "tipo": "Sedán",
                "fuel": "Eléctrico",
                "combustible": "Eléctrico",
                "transmission": "Automática",
                "transmision": "Automática",
                "features": ["Piloto automático", "Pantalla táctil 15\"", "Supercargador"],
                "caracteristicas": ["Piloto automático", "Pantalla táctil 15\"", "Supercargador"],
                "similarity_score": 70.0,
                "recommendation_reason": "Tecnología avanzada y ecológico",
                "image": None
            }
        ]
        
        return fallback_cars

# Instancia global del recomendador
_recommender_instance = None

def get_recommender_instance():
    """Obtener instancia singleton del recomendador inteligente"""
    global _recommender_instance
    if _recommender_instance is None:
        # Configuraciones de conexión
        configs = [
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
        ]
        
        for config in configs:
            try:
                _recommender_instance = IntelligentCarRecommender(
                    config["uri"], config["user"], config["password"]
                )
                logger.info(f"Recomendador inicializado con {config['password']}")
                break
            except Exception as e:
                logger.warning(f"Error con config {config['password']}: {e}")
                continue
        
        if _recommender_instance is None:
            logger.error("No se pudo inicializar el recomendador")
    
    return _recommender_instance

def get_recommendations(brands=None, budget=None, fuel=None, types=None, 
                       transmission=None, gender=None, age_range=None):
    """
    Función principal para obtener recomendaciones inteligentes
    Compatible con la interfaz existente de Flask
    """
    recommender = get_recommender_instance()
    
    if recommender is None:
        logger.error("Recomendador no disponible, usando respaldo")
        return IntelligentCarRecommender("", "", "").get_fallback_recommendations()
    
    try:
        # Normalizar entrada
        if isinstance(brands, dict):
            brands = list(brands.values())
        elif isinstance(brands, str):
            brands = [brands]
        
        if isinstance(types, str):
            types = [types]
        
        # Mapear nombres de combustible
        fuel_mapping = {
            'gasolina': 'Gasolina',
            'gas': 'Gasolina', 
            'diesel': 'Diésel',
            'electrico': 'Eléctrico',
            'electric': 'Eléctrico',
            'hibrido': 'Híbrido',
            'hybrid': 'Híbrido'
        }
        
        if fuel and isinstance(fuel, str):
            fuel = fuel_mapping.get(fuel.lower(), fuel)
        
        # Mapear transmisión
        transmission_mapping = {
            'automatic': 'Automática',
            'automatica': 'Automática',
            'manual': 'Manual',
            'semiautomatic': 'Semiautomática',
            'semiautomatica': 'Semiautomática'
        }
        
        if transmission and isinstance(transmission, str):
            transmission = transmission_mapping.get(transmission.lower(), transmission)
        
        # Mapear tipos
        type_mapping = {
            'sedan': 'Sedán',
            'suv': 'SUV',
            'hatchback': 'Hatchback', 
            'pickup': 'Pickup',
            'coupe': 'Coupé',
            'convertible': 'Convertible'
        }
        
        if types:
            types = [type_mapping.get(t.lower() if isinstance(t, str) else t, t) for t in types]
        
        logger.info(f"Llamando recomendador inteligente con:")
        logger.info(f"  brands={brands}, budget={budget}, fuel={fuel}")
        logger.info(f"  types={types}, transmission={transmission}")
        logger.info(f"  gender={gender}, age_range={age_range}")
        
        # Llamar al sistema inteligente
        recommendations = recommender.get_intelligent_recommendations(
            brands=brands,
            budget=budget,
            fuel=fuel,
            types=types, 
            transmission=transmission,
            gender=gender,
            age_range=age_range,
            limit=10
        )
        
        logger.info(f"Recomendador devolvió {len(recommendations)} resultados")
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Error en recomendador inteligente: {e}")
        import traceback
        traceback.print_exc()
        return recommender.get_fallback_recommendations()

def test_intelligent_recommendations():
    """Función de prueba para el sistema de recomendaciones"""
    print("=== PRUEBA DEL SISTEMA DE RECOMENDACIONES INTELIGENTE ===")
    
    test_cases = [
        {
            "name": "Hombre joven buscando deportivo",
            "params": {
                "brands": ["Honda", "Toyota"],
                "budget": "25000-40000",
                "fuel": "Gasolina",
                "types": ["Sedán"],
                "transmission": "Manual",
                "gender": "masculino",
                "age_range": "18-25"
            }
        },
        {
            "name": "Mujer profesional buscando SUV familiar",
            "params": {
                "brands": ["Toyota"],
                "budget": "35000-55000", 
                "fuel": "Híbrido",
                "types": ["SUV"],
                "transmission": "Automática",
                "gender": "femenino",
                "age_range": "26-35"
            }
        },
        {
            "name": "Hombre maduro buscando lujo",
            "params": {
                "brands": ["BMW"],
                "budget": "50000-80000",
                "fuel": "Gasolina", 
                "types": ["Sedán"],
                "transmission": "Automática",
                "gender": "masculino",
                "age_range": "46-55"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- {test_case['name']} ---")
        recommendations = get_recommendations(**test_case['params'])
        
        print(f"Obtenidas {len(recommendations)} recomendaciones:")
        for i, car in enumerate(recommendations[:3], 1):
            print(f"{i}. {car['name']} - ${car['price']:,}")
            print(f"   Score: {car['similarity_score']}/100")
            print(f"   Razón: {car['recommendation_reason']}")
            print()

if __name__ == "__main__":
    test_intelligent_recommendations()