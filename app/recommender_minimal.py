#!/usr/bin/env python3
"""
Sistema de recomendaciones de autos usando Neo4j (versión simplificada para Python 3.13)
"""

from neo4j import GraphDatabase
import json

class CarRecommender:
    def __init__(self, uri, user, password):
        """Inicializar conexión a Neo4j"""
        try:
            self.driver = GraphDatabase.driver(uri, auth=(user, password))
            # Verificar conexión
            with self.driver.session() as session:
                session.run("RETURN 1")
            print("✓ Conexión exitosa a Neo4j")
        except Exception as e:
            print(f"✗ Error conectando a Neo4j: {e}")
            raise
    
    def close(self):
        """Cerrar conexión"""
        if hasattr(self, 'driver'):
            self.driver.close()
    
    def parse_budget_range(self, budget_str):
        """Convertir string de presupuesto a rango numérico"""
        try:
            if budget_str == "100000+":
                return (100000, 999999999)
            elif "-" in budget_str:
                min_val, max_val = budget_str.split("-")
                return (int(min_val), int(max_val))
            else:
                return (0, int(budget_str))
        except Exception as e:
            print(f"Error parseando presupuesto '{budget_str}': {e}")
            return (0, 999999999)
    
    def get_recommendations(self, brands=None, budget=None, fuel=None, types=None, transmission=None):
        """Obtener recomendaciones de autos"""
        try:
            print("=== GENERANDO RECOMENDACIONES ===")
            print(f"Brands: {brands}")
            print(f"Budget: {budget}")
            print(f"Fuel: {fuel}")
            print(f"Types: {types}")
            print(f"Transmission: {transmission}")
            
            # Normalizar entrada
            if brands and isinstance(brands, dict):
                brands = list(brands.values())
            
            if budget:
                min_price, max_price = self.parse_budget_range(budget)
            else:
                min_price, max_price = 0, 999999999
            
            # Construir consulta base
            query = """
                MATCH (a:Auto)
                WHERE a.precio >= $min_price AND a.precio <= $max_price
            """
            parameters = {
                'min_price': min_price,
                'max_price': max_price
            }
            
            # Agregar filtros según disponibilidad
            if brands:
                query += """
                    MATCH (a)-[:ES_MARCA]->(m:Marca)
                    WHERE m.nombre IN $brands
                """
                parameters['brands'] = brands
            
            if fuel:
                fuel_clean = fuel if isinstance(fuel, str) else fuel[0] if fuel else None
                if fuel_clean:
                    fuel_mapping = {
                        'gasolina': 'Gasolina',
                        'diesel': 'Diésel', 
                        'electrico': 'Eléctrico',
                        'hibrido': 'Híbrido'
                    }
                    fuel_clean = fuel_mapping.get(fuel_clean.lower(), fuel_clean)
                    query += """
                        MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                        WHERE c.tipo = $fuel
                    """
                    parameters['fuel'] = fuel_clean
            
            if types:
                if isinstance(types, str):
                    types = [types]
                type_mapping = {
                    'sedan': 'Sedán',
                    'suv': 'SUV', 
                    'hatchback': 'Hatchback',
                    'pickup': 'Pickup',
                    'coupe': 'Coupé'
                }
                types_clean = [type_mapping.get(t.lower(), t) for t in types]
                query += """
                    MATCH (a)-[:ES_TIPO]->(t:Tipo)
                    WHERE t.categoria IN $types
                """
                parameters['types'] = types_clean
            
            if transmission:
                trans_clean = transmission if isinstance(transmission, str) else transmission[0] if transmission else None
                if trans_clean:
                    trans_mapping = {
                        'automatic': 'Automática',
                        'automatica': 'Automática',
                        'manual': 'Manual'
                    }
                    trans_clean = trans_mapping.get(trans_clean.lower(), trans_clean)
                    query += """
                        MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                        WHERE tr.tipo = $transmission
                    """
                    parameters['transmission'] = trans_clean
            
            # Completar consulta
            query += """
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
            """
            
            print(f"Query: {query}")
            print(f"Parameters: {parameters}")
            
            # Ejecutar consulta
            with self.driver.session() as session:
                result = session.run(query, parameters)
                recommendations = []
                
                for record in result:
                    car_data = {
                        'id': record['id'],
                        'name': f"{record['marca'] or 'Auto'} {record['modelo']} {record['año']}",
                        'model': record['modelo'],
                        'brand': record['marca'] or 'Marca no especificada',
                        'year': record['año'],
                        'price': float(record['precio']) if record['precio'] else 0,
                        'type': record['tipo'] or 'Tipo no especificado',
                        'fuel': record['combustible'] or 'Combustible no especificado',
                        'transmission': record['transmision'] or 'Transmisión no especificada',
                        'features': record['caracteristicas'] or [],
                        'image': None
                    }
                    recommendations.append(car_data)
                
                print(f"Encontradas {len(recommendations)} recomendaciones")
                return recommendations
                
        except Exception as e:
            print(f"Error en get_recommendations: {e}")
            return self.get_fallback_recommendations(brands, budget, fuel, types, transmission)
    
    def get_fallback_recommendations(self, brands=None, budget=None, fuel=None, types=None, transmission=None):
        """Recomendaciones de respaldo"""
        print("Usando recomendaciones de respaldo")
        
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
                "features": ["Aire acondicionado", "Radio AM/FM", "Bluetooth"],
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
                "features": ["Pantalla táctil", "Bluetooth", "Control crucero"],
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
                "features": ["Piloto automático", "Pantalla táctil", "Supercargador"],
                "image": None
            }
        ]
        
        return fallback_cars

# Instancia global
_recommender_instance = None

def get_recommender_instance():
    """Obtener instancia del recomendador"""
    global _recommender_instance
    if _recommender_instance is None:
        # Configuración específica con tu contraseña
        configs = [
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
        ]
        
        for config in configs:
            try:
                print(f"Probando conexión: {config['uri']} con usuario {config['user']}")
                _recommender_instance = CarRecommender(config["uri"], config["user"], config["password"])
                print(f"✓ Conexión exitosa con configuración: {config}")
                break
            except Exception as e:
                print(f"✗ Falló configuración {config}: {e}")
                continue
        
        if _recommender_instance is None:
            print("⚠️ No se pudo conectar a Neo4j, usando modo de respaldo")
    
    return _recommender_instance

def get_recommendations(brands=None, budget=None, fuel=None, types=None, transmission=None):
    """Función principal para obtener recomendaciones"""
    recommender = get_recommender_instance()
    
    if recommender is None:
        print("No hay conexión a Neo4j, usando datos de ejemplo")
        return CarRecommender(None, None, None).get_fallback_recommendations(brands, budget, fuel, types, transmission)
    
    try:
        return recommender.get_recommendations(brands, budget, fuel, types, transmission)
    except Exception as e:
        print(f"Error en get_recommendations: {e}")
        return CarRecommender(None, None, None).get_fallback_recommendations(brands, budget, fuel, types, transmission)

def test_connection():
    """Probar conexión"""
    try:
        recommender = get_recommender_instance()
        return recommender is not None
    except:
        return False

if __name__ == "__main__":
    print("=== PRUEBA DEL SISTEMA DE RECOMENDACIONES ===")
    
    if test_connection():
        print("✓ Sistema funcionando")
        
        # Prueba básica
        recs = get_recommendations(brands=["Toyota"], budget="20000-30000")
        print(f"Encontradas {len(recs)} recomendaciones:")
        for i, car in enumerate(recs[:3], 1):
            print(f"{i}. {car['name']} - ${car['price']:,}")
    else:
        print("✗ No se pudo conectar, pero el sistema funcionará con datos de ejemplo")