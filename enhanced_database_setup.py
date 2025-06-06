#!/usr/bin/env python3
"""
Script para configurar una base de datos Neo4j expandida con capacidades de recomendación
Incluye información contextual, similitudes entre marcas, perfiles demográficos y algoritmos de recomendación
"""

from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedDatabaseSetup:
    def __init__(self):
        # Configuraciones de conexión a probar
        self.configs = [
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "estructura"},
            {"uri": "bolt://localhost:7687", "user": "neo4j", "password": "proyectoNEO4J"},
        ]
        self.driver = None
        self.connect()
        
        # Datos expandidos para recomendaciones inteligentes
        self.brand_data = {
            # Marcas japonesas - Confiabilidad, eficiencia
            "Toyota": {"origen": "Japón", "caracteristicas": ["Confiable", "Eficiente", "Familiar"], "target_age": "25-55", "price_range": "medio", "reliability": 9},
            "Honda": {"origen": "Japón", "caracteristicas": ["Confiable", "Deportivo", "Eficiente"], "target_age": "20-50", "price_range": "medio", "reliability": 9},
            "Nissan": {"origen": "Japón", "caracteristicas": ["Innovador", "Confiable", "Tecnológico"], "target_age": "25-50", "price_range": "medio", "reliability": 8},
            "Mazda": {"origen": "Japón", "caracteristicas": ["Deportivo", "Elegante", "Eficiente"], "target_age": "22-45", "price_range": "medio", "reliability": 8},
            "Subaru": {"origen": "Japón", "caracteristicas": ["Aventurero", "Seguro", "AWD"], "target_age": "25-50", "price_range": "medio-alto", "reliability": 8},
            "Mitsubishi": {"origen": "Japón", "caracteristicas": ["Aventurero", "Robusto", "Accesible"], "target_age": "22-45", "price_range": "medio-bajo", "reliability": 7},
            "Lexus": {"origen": "Japón", "caracteristicas": ["Lujo", "Confiable", "Refinado"], "target_age": "35-65", "price_range": "alto", "reliability": 9},
            
            # Marcas alemanas - Ingeniería, performance, lujo
            "BMW": {"origen": "Alemania", "caracteristicas": ["Deportivo", "Lujo", "Performance"], "target_age": "25-55", "price_range": "alto", "reliability": 7},
            "Mercedes-Benz": {"origen": "Alemania", "caracteristicas": ["Lujo", "Elegante", "Tecnológico"], "target_age": "30-65", "price_range": "alto", "reliability": 7},
            "Audi": {"origen": "Alemania", "caracteristicas": ["Deportivo", "Tecnológico", "Lujo"], "target_age": "25-55", "price_range": "alto", "reliability": 7},
            "Volkswagen": {"origen": "Alemania", "caracteristicas": ["Familiar", "Confiable", "Europeo"], "target_age": "25-55", "price_range": "medio", "reliability": 7},
            "Porsche": {"origen": "Alemania", "caracteristicas": ["Deportivo", "Lujo", "Performance"], "target_age": "30-60", "price_range": "muy-alto", "reliability": 8},
            
            # Marcas americanas - Potencia, espacio, tradición
            "Ford": {"origen": "Estados Unidos", "caracteristicas": ["Potente", "Robusto", "Americano"], "target_age": "25-65", "price_range": "medio", "reliability": 6},
            "Chevrolet": {"origen": "Estados Unidos", "caracteristicas": ["Potente", "Deportivo", "Americano"], "target_age": "20-60", "price_range": "medio", "reliability": 6},
            "Tesla": {"origen": "Estados Unidos", "caracteristicas": ["Innovador", "Ecológico", "Tecnológico"], "target_age": "25-50", "price_range": "alto", "reliability": 7},
            "Jeep": {"origen": "Estados Unidos", "caracteristicas": ["Aventurero", "Robusto", "Off-road"], "target_age": "25-55", "price_range": "medio-alto", "reliability": 6},
            
            # Marcas coreanas - Valor, garantía, modernas
            "Hyundai": {"origen": "Corea del Sur", "caracteristicas": ["Accesible", "Moderno", "Garantía"], "target_age": "20-50", "price_range": "medio-bajo", "reliability": 8},
            "Kia": {"origen": "Corea del Sur", "caracteristicas": ["Accesible", "Estiloso", "Garantía"], "target_age": "18-45", "price_range": "medio-bajo", "reliability": 8},
            "Genesis": {"origen": "Corea del Sur", "caracteristicas": ["Lujo", "Moderno", "Valor"], "target_age": "30-60", "price_range": "alto", "reliability": 8},
            
            # Marcas europeas - Elegancia, diseño
            "Volvo": {"origen": "Suecia", "caracteristicas": ["Seguro", "Familiar", "Elegante"], "target_age": "30-60", "price_range": "alto", "reliability": 8},
            "Peugeot": {"origen": "Francia", "caracteristicas": ["Elegante", "Europeo", "Eficiente"], "target_age": "25-55", "price_range": "medio", "reliability": 7},
            "Renault": {"origen": "Francia", "caracteristicas": ["Compacto", "Urbano", "Europeo"], "target_age": "20-50", "price_range": "medio-bajo", "reliability": 6},
        }
        
        # Perfiles demográficos detallados
        self.demographic_profiles = {
            "hombre_18_25": {
                "preferencias": ["Deportivo", "Performance", "Estiloso", "Accesible"],
                "tipos_vehiculo": ["Coupé", "Hatchback", "Sedán"],
                "marcas_recomendadas": ["Honda", "Mazda", "Hyundai", "Kia", "Chevrolet"],
                "caracteristicas_importantes": ["Potencia", "Diseño", "Precio"]
            },
            "hombre_26_35": {
                "preferencias": ["Versátil", "Confiable", "Tecnológico", "Deportivo"],
                "tipos_vehiculo": ["Sedán", "SUV", "Crossover"],
                "marcas_recomendadas": ["Toyota", "Honda", "BMW", "Audi", "Tesla"],
                "caracteristicas_importantes": ["Confiabilidad", "Tecnología", "Performance"]
            },
            "hombre_36_50": {
                "preferencias": ["Familiar", "Confiable", "Espacioso", "Lujo"],
                "tipos_vehiculo": ["SUV", "Sedán", "Pickup"],
                "marcas_recomendadas": ["Toyota", "Honda", "BMW", "Mercedes-Benz", "Volvo"],
                "caracteristicas_importantes": ["Espacio", "Seguridad", "Confort"]
            },
            "hombre_51_plus": {
                "preferencias": ["Lujo", "Confort", "Confiable", "Prestigio"],
                "tipos_vehiculo": ["Sedán", "SUV"],
                "marcas_recomendadas": ["Mercedes-Benz", "BMW", "Lexus", "Volvo", "Genesis"],
                "caracteristicas_importantes": ["Lujo", "Confort", "Prestigio"]
            },
            "mujer_18_25": {
                "preferencias": ["Estiloso", "Compacto", "Eficiente", "Accesible"],
                "tipos_vehiculo": ["Hatchback", "Sedán", "Crossover"],
                "marcas_recomendadas": ["Honda", "Toyota", "Mazda", "Hyundai", "Kia"],
                "caracteristicas_importantes": ["Diseño", "Eficiencia", "Facilidad de manejo"]
            },
            "mujer_26_35": {
                "preferencias": ["Seguro", "Confiable", "Familiar", "Eficiente"],
                "tipos_vehiculo": ["SUV", "Crossover", "Sedán"],
                "marcas_recomendadas": ["Toyota", "Honda", "Subaru", "Volvo", "Mazda"],
                "caracteristicas_importantes": ["Seguridad", "Confiabilidad", "Espacio"]
            },
            "mujer_36_50": {
                "preferencias": ["Familiar", "Seguro", "Espacioso", "Confiable"],
                "tipos_vehiculo": ["SUV", "Minivan", "Crossover"],
                "marcas_recomendadas": ["Toyota", "Honda", "Subaru", "Volvo", "Lexus"],
                "caracteristicas_importantes": ["Seguridad", "Espacio familiar", "Confiabilidad"]
            },
            "mujer_51_plus": {
                "preferencias": ["Confort", "Lujo", "Fácil manejo", "Confiable"],
                "tipos_vehiculo": ["Sedán", "SUV"],
                "marcas_recomendadas": ["Lexus", "Mercedes-Benz", "Volvo", "BMW", "Genesis"],
                "caracteristicas_importantes": ["Confort", "Facilidad de uso", "Lujo"]
            }
        }
        
        # Similitudes entre marcas para recomendaciones
        self.brand_similarities = {
            "Toyota": ["Honda", "Nissan", "Mazda", "Subaru", "Lexus"],
            "Honda": ["Toyota", "Mazda", "Nissan", "Subaru", "Hyundai"],
            "BMW": ["Audi", "Mercedes-Benz", "Lexus", "Genesis", "Volvo"],
            "Mercedes-Benz": ["BMW", "Audi", "Lexus", "Genesis", "Volvo"],
            "Audi": ["BMW", "Mercedes-Benz", "Lexus", "Volvo", "Genesis"],
            "Tesla": ["BMW", "Audi", "Mercedes-Benz", "Genesis", "Volvo"],
            "Ford": ["Chevrolet", "Jeep", "Toyota", "Honda", "Nissan"],
            "Chevrolet": ["Ford", "Jeep", "Hyundai", "Kia", "Nissan"],
            "Hyundai": ["Kia", "Honda", "Toyota", "Nissan", "Chevrolet"],
            "Kia": ["Hyundai", "Honda", "Mazda", "Toyota", "Nissan"],
            "Nissan": ["Toyota", "Honda", "Mazda", "Hyundai", "Subaru"],
            "Mazda": ["Honda", "Toyota", "Nissan", "Subaru", "Kia"],
            "Subaru": ["Toyota", "Honda", "Mazda", "Volvo", "Nissan"],
            "Volvo": ["BMW", "Mercedes-Benz", "Audi", "Subaru", "Lexus"],
            "Lexus": ["Mercedes-Benz", "BMW", "Audi", "Genesis", "Volvo"],
            "Genesis": ["BMW", "Mercedes-Benz", "Audi", "Lexus", "Volvo"],
            "Porsche": ["BMW", "Audi", "Mercedes-Benz", "Lexus", "Tesla"],
            "Jeep": ["Ford", "Chevrolet", "Subaru", "Toyota", "Nissan"],
            "Mitsubishi": ["Nissan", "Subaru", "Honda", "Hyundai", "Kia"],
            "Peugeot": ["Renault", "Volkswagen", "Honda", "Toyota", "Hyundai"],
            "Renault": ["Peugeot", "Volkswagen", "Hyundai", "Kia", "Honda"],
            "Volkswagen": ["Audi", "BMW", "Honda", "Toyota", "Peugeot"],
        }
    
    def connect(self):
        """Establecer conexión con Neo4j"""
        for config in self.configs:
            try:
                self.driver = GraphDatabase.driver(config["uri"], auth=(config["user"], config["password"]))
                with self.driver.session() as session:
                    session.run("RETURN 1")
                logger.info(f"Conexión exitosa con {config['password']}")
                return
            except Exception as e:
                continue
        raise Exception("No se pudo conectar a Neo4j")
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def clear_database(self):
        """Limpiar toda la base de datos"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Base de datos limpiada")
    
    def create_enhanced_schema(self):
        """Crear esquema mejorado con nodos para recomendaciones"""
        with self.driver.session() as session:
            # Crear marcas con información extendida
            for brand, info in self.brand_data.items():
                session.run("""
                    CREATE (m:Marca {
                        nombre: $nombre,
                        origen: $origen,
                        caracteristicas: $caracteristicas,
                        target_age: $target_age,
                        price_range: $price_range,
                        reliability: $reliability
                    })
                """, nombre=brand, **info)
            
            # Crear perfiles demográficos
            for profile_id, profile_data in self.demographic_profiles.items():
                session.run("""
                    CREATE (p:PerfilDemografico {
                        id: $profile_id,
                        preferencias: $preferencias,
                        tipos_vehiculo: $tipos_vehiculo,
                        marcas_recomendadas: $marcas_recomendadas,
                        caracteristicas_importantes: $caracteristicas_importantes
                    })
                """, profile_id=profile_id, **profile_data)
            
            # Crear tipos de vehículo con información contextual
            vehicle_types_data = {
                "Sedán": {"target_demographic": ["familia", "profesional"], "uso_principal": "urbano", "capacidad": 5},
                "SUV": {"target_demographic": ["familia", "aventurero"], "uso_principal": "mixto", "capacidad": 7},
                "Hatchback": {"target_demographic": ["joven", "urbano"], "uso_principal": "ciudad", "capacidad": 5},
                "Pickup": {"target_demographic": ["trabajador", "aventurero"], "uso_principal": "trabajo", "capacidad": 5},
                "Coupé": {"target_demographic": ["joven", "deportivo"], "uso_principal": "recreativo", "capacidad": 4},
                "Convertible": {"target_demographic": ["joven", "deportivo"], "uso_principal": "recreativo", "capacidad": 4},
                "Crossover": {"target_demographic": ["familia", "urbano"], "uso_principal": "mixto", "capacidad": 5},
                "Minivan": {"target_demographic": ["familia_grande"], "uso_principal": "familiar", "capacidad": 8}
            }
            
            for vehicle_type, type_info in vehicle_types_data.items():
                session.run("""
                    CREATE (t:Tipo {
                        categoria: $categoria,
                        target_demographic: $target_demographic,
                        uso_principal: $uso_principal,
                        capacidad: $capacidad
                    })
                """, categoria=vehicle_type, **type_info)
            
            # Crear combustibles
            fuels = ["Gasolina", "Diésel", "Eléctrico", "Híbrido"]
            for fuel in fuels:
                session.run("CREATE (c:Combustible {tipo: $tipo})", tipo=fuel)
            
            # Crear transmisiones
            transmissions = ["Automática", "Manual", "Semiautomática"]
            for transmission in transmissions:
                session.run("CREATE (tr:Transmision {tipo: $tipo})", tipo=transmission)
            
            logger.info("Esquema mejorado creado")
    
    def create_brand_similarities(self):
        """Crear relaciones de similitud entre marcas"""
        with self.driver.session() as session:
            for brand, similar_brands in self.brand_similarities.items():
                for similar_brand in similar_brands:
                    # Calcular peso de similitud basado en características comunes
                    weight = self.calculate_similarity_weight(brand, similar_brand)
                    session.run("""
                        MATCH (m1:Marca {nombre: $brand1})
                        MATCH (m2:Marca {nombre: $brand2})
                        CREATE (m1)-[:SIMILAR_A {peso: $weight}]->(m2)
                    """, brand1=brand, brand2=similar_brand, weight=weight)
            
            logger.info("Relaciones de similitud entre marcas creadas")
    
    def calculate_similarity_weight(self, brand1, brand2):
        """Calcular peso de similitud entre dos marcas"""
        if brand1 not in self.brand_data or brand2 not in self.brand_data:
            return 0.5
        
        data1 = self.brand_data[brand1]
        data2 = self.brand_data[brand2]
        
        weight = 0.0
        
        # Mismo origen (+0.3)
        if data1["origen"] == data2["origen"]:
            weight += 0.3
        
        # Características similares (+0.1 por cada coincidencia)
        common_characteristics = set(data1["caracteristicas"]) & set(data2["caracteristicas"])
        weight += len(common_characteristics) * 0.1
        
        # Rango de precio similar (+0.2)
        if data1["price_range"] == data2["price_range"]:
            weight += 0.2
        
        # Confiabilidad similar (+0.1)
        reliability_diff = abs(data1["reliability"] - data2["reliability"])
        if reliability_diff <= 1:
            weight += 0.1
        
        return min(weight, 1.0)  # Máximo 1.0
    
    def create_comprehensive_cars(self):
        """Crear una base de datos completa de autos"""
        cars_data = []
        car_id = 1
        
        # Modelos por marca expandidos
        models_by_brand = {
            "Toyota": [
                {"modelo": "Corolla", "tipo": "Sedán", "precio_base": 25000, "segmento": "compacto"},
                {"modelo": "Camry", "tipo": "Sedán", "precio_base": 30000, "segmento": "medio"},
                {"modelo": "RAV4", "tipo": "SUV", "precio_base": 35000, "segmento": "compacto"},
                {"modelo": "Highlander", "tipo": "SUV", "precio_base": 40000, "segmento": "grande"},
                {"modelo": "Prius", "tipo": "Hatchback", "precio_base": 28000, "segmento": "híbrido"},
                {"modelo": "Sienna", "tipo": "Minivan", "precio_base": 35000, "segmento": "familiar"},
                {"modelo": "Yaris", "tipo": "Hatchback", "precio_base": 18000, "segmento": "económico"},
                {"modelo": "Avalon", "tipo": "Sedán", "precio_base": 38000, "segmento": "lujo"},
            ],
            "Honda": [
                {"modelo": "Civic", "tipo": "Sedán", "precio_base": 27000, "segmento": "compacto"},
                {"modelo": "Accord", "tipo": "Sedán", "precio_base": 31000, "segmento": "medio"},
                {"modelo": "CR-V", "tipo": "SUV", "precio_base": 36000, "segmento": "compacto"},
                {"modelo": "Pilot", "tipo": "SUV", "precio_base": 42000, "segmento": "grande"},
                {"modelo": "Fit", "tipo": "Hatchback", "precio_base": 20000, "segmento": "económico"},
                {"modelo": "Odyssey", "tipo": "Minivan", "precio_base": 38000, "segmento": "familiar"},
                {"modelo": "HR-V", "tipo": "Crossover", "precio_base": 24000, "segmento": "compacto"},
                {"modelo": "Ridgeline", "tipo": "Pickup", "precio_base": 40000, "segmento": "medio"},
            ],
            "BMW": [
                {"modelo": "3 Series", "tipo": "Sedán", "precio_base": 45000, "segmento": "lujo"},
                {"modelo": "5 Series", "tipo": "Sedán", "precio_base": 55000, "segmento": "lujo"},
                {"modelo": "X3", "tipo": "SUV", "precio_base": 50000, "segmento": "lujo"},
                {"modelo": "X5", "tipo": "SUV", "precio_base": 65000, "segmento": "lujo"},
                {"modelo": "2 Series", "tipo": "Coupé", "precio_base": 40000, "segmento": "deportivo"},
                {"modelo": "Z4", "tipo": "Convertible", "precio_base": 55000, "segmento": "deportivo"},
                {"modelo": "X1", "tipo": "Crossover", "precio_base": 38000, "segmento": "lujo"},
                {"modelo": "i3", "tipo": "Hatchback", "precio_base": 48000, "segmento": "eléctrico"},
            ],
            "Tesla": [
                {"modelo": "Model 3", "tipo": "Sedán", "precio_base": 42000, "segmento": "eléctrico"},
                {"modelo": "Model S", "tipo": "Sedán", "precio_base": 75000, "segmento": "lujo_eléctrico"},
                {"modelo": "Model Y", "tipo": "SUV", "precio_base": 48000, "segmento": "eléctrico"},
                {"modelo": "Model X", "tipo": "SUV", "precio_base": 85000, "segmento": "lujo_eléctrico"},
                {"modelo": "Cybertruck", "tipo": "Pickup", "precio_base": 60000, "segmento": "eléctrico"},
            ],
            "Ford": [
                {"modelo": "Focus", "tipo": "Hatchback", "precio_base": 22000, "segmento": "compacto"},
                {"modelo": "Fusion", "tipo": "Sedán", "precio_base": 28000, "segmento": "medio"},
                {"modelo": "Mustang", "tipo": "Coupé", "precio_base": 38000, "segmento": "deportivo"},
                {"modelo": "Explorer", "tipo": "SUV", "precio_base": 40000, "segmento": "grande"},
                {"modelo": "F-150", "tipo": "Pickup", "precio_base": 45000, "segmento": "trabajo"},
                {"modelo": "Escape", "tipo": "Crossover", "precio_base": 28000, "segmento": "compacto"},
                {"modelo": "Bronco", "tipo": "SUV", "precio_base": 35000, "segmento": "aventura"},
                {"modelo": "Edge", "tipo": "SUV", "precio_base": 38000, "segmento": "medio"},
            ],
            # Agregar más marcas...
            "Mercedes-Benz": [
                {"modelo": "C-Class", "tipo": "Sedán", "precio_base": 48000, "segmento": "lujo"},
                {"modelo": "E-Class", "tipo": "Sedán", "precio_base": 58000, "segmento": "lujo"},
                {"modelo": "GLC", "tipo": "SUV", "precio_base": 55000, "segmento": "lujo"},
                {"modelo": "GLE", "tipo": "SUV", "precio_base": 68000, "segmento": "lujo"},
                {"modelo": "A-Class", "tipo": "Hatchback", "precio_base": 35000, "segmento": "lujo_compacto"},
                {"modelo": "S-Class", "tipo": "Sedán", "precio_base": 95000, "segmento": "ultra_lujo"},
            ],
            "Hyundai": [
                {"modelo": "Elantra", "tipo": "Sedán", "precio_base": 22000, "segmento": "económico"},
                {"modelo": "Sonata", "tipo": "Sedán", "precio_base": 28000, "segmento": "medio"},
                {"modelo": "Tucson", "tipo": "SUV", "precio_base": 28000, "segmento": "compacto"},
                {"modelo": "Santa Fe", "tipo": "SUV", "precio_base": 35000, "segmento": "medio"},
                {"modelo": "Kona", "tipo": "Crossover", "precio_base": 25000, "segmento": "compacto"},
                {"modelo": "Ioniq", "tipo": "Hatchback", "precio_base": 30000, "segmento": "híbrido"},
                {"modelo": "Palisade", "tipo": "SUV", "precio_base": 38000, "segmento": "familiar"},
            ],
            "Kia": [
                {"modelo": "Forte", "tipo": "Sedán", "precio_base": 20000, "segmento": "económico"},
                {"modelo": "Optima", "tipo": "Sedán", "precio_base": 26000, "segmento": "medio"},
                {"modelo": "Sportage", "tipo": "SUV", "precio_base": 26000, "segmento": "compacto"},
                {"modelo": "Sorento", "tipo": "SUV", "precio_base": 33000, "segmento": "medio"},
                {"modelo": "Soul", "tipo": "Crossover", "precio_base": 22000, "segmento": "urbano"},
                {"modelo": "Stinger", "tipo": "Sedán", "precio_base": 38000, "segmento": "deportivo"},
                {"modelo": "Telluride", "tipo": "SUV", "precio_base": 36000, "segmento": "familiar"},
            ]
        }
        
        # Generar autos para cada marca
        for brand, models in models_by_brand.items():
            for model_info in models:
                # Crear variaciones del modelo (diferentes años, trim levels)
                for year in [2022, 2023, 2024]:
                    for trim_level in ["Base", "Premium", "Sport"]:
                        price_modifier = {"Base": 0, "Premium": 5000, "Sport": 8000}
                        final_price = model_info["precio_base"] + price_modifier[trim_level]
                        
                        # Determinar combustible basado en marca y modelo
                        if brand == "Tesla":
                            fuel = "Eléctrico"
                        elif "Prius" in model_info["modelo"] or "Ioniq" in model_info["modelo"]:
                            fuel = "Híbrido"
                        elif "Sport" in trim_level and model_info["tipo"] in ["Coupé", "Convertible"]:
                            fuel = "Gasolina"
                        else:
                            fuel = self.select_fuel_by_probability(model_info["tipo"])
                        
                        # Determinar transmisión
                        if fuel == "Eléctrico":
                            transmission = "Automática"
                        elif trim_level == "Sport" and model_info["tipo"] in ["Coupé", "Sedán"]:
                            transmission = "Manual" if car_id % 3 == 0 else "Automática"
                        else:
                            transmission = "Automática"
                        
                        # Generar características basadas en trim level y marca
                        features = self.generate_features(brand, model_info, trim_level)
                        
                        car = {
                            "id": f"car_{car_id}",
                            "modelo": f"{model_info['modelo']} {trim_level}",
                            "año": year,
                            "precio": final_price,
                            "marca": brand,
                            "tipo": model_info["tipo"],
                            "combustible": fuel,
                            "transmision": transmission,
                            "caracteristicas": features,
                            "segmento": model_info["segmento"],
                            "trim_level": trim_level
                        }
                        
                        cars_data.append(car)
                        car_id += 1
        
        # Crear autos en la base de datos
        with self.driver.session() as session:
            for i, car in enumerate(cars_data, 1):
                if i % 20 == 0:
                    logger.info(f"Creando auto {i}/{len(cars_data)}")
                
                # Crear auto
                session.run("""
                    CREATE (a:Auto {
                        id: $id,
                        modelo: $modelo,
                        año: $año,
                        precio: $precio,
                        caracteristicas: $caracteristicas,
                        segmento: $segmento,
                        trim_level: $trim_level
                    })
                """, **car)
                
                # Crear relaciones
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (m:Marca {nombre: $marca})
                    MERGE (a)-[:ES_MARCA]->(m)
                """, id=car["id"], marca=car["marca"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (t:Tipo {categoria: $tipo})
                    MERGE (a)-[:ES_TIPO]->(t)
                """, id=car["id"], tipo=car["tipo"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (c:Combustible {tipo: $combustible})
                    MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                """, id=car["id"], combustible=car["combustible"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (tr:Transmision {tipo: $transmision})
                    MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                """, id=car["id"], transmision=car["transmision"])
        
        logger.info(f"Creados {len(cars_data)} autos con relaciones completas")
    
    def select_fuel_by_probability(self, vehicle_type):
        """Seleccionar combustible basado en probabilidades por tipo"""
        import random
        
        fuel_probabilities = {
            "Sedán": {"Gasolina": 0.6, "Híbrido": 0.3, "Eléctrico": 0.1},
            "SUV": {"Gasolina": 0.7, "Híbrido": 0.2, "Eléctrico": 0.1},
            "Hatchback": {"Gasolina": 0.5, "Híbrido": 0.3, "Eléctrico": 0.2},
            "Pickup": {"Gasolina": 0.8, "Diésel": 0.2},
            "Coupé": {"Gasolina": 0.9, "Eléctrico": 0.1},
            "Convertible": {"Gasolina": 0.95, "Eléctrico": 0.05},
            "Crossover": {"Gasolina": 0.6, "Híbrido": 0.3, "Eléctrico": 0.1},
            "Minivan": {"Gasolina": 0.8, "Híbrido": 0.2}
        }
        
        probs = fuel_probabilities.get(vehicle_type, {"Gasolina": 0.7, "Híbrido": 0.2, "Eléctrico": 0.1})
        choices = list(probs.keys())
        weights = list(probs.values())
        
        return random.choices(choices, weights=weights)[0]
    
    def generate_features(self, brand, model_info, trim_level):
        """Generar características realistas basadas en marca, modelo y trim"""
        base_features = ["Aire acondicionado", "Radio AM/FM", "Bluetooth"]
        
        premium_features = {
            "Base": [],
            "Premium": ["Pantalla táctil", "Cámara trasera", "Control crucero", "Asientos de tela premium"],
            "Sport": ["Asientos deportivos", "Volante deportivo", "Suspensión deportiva", "Llantas de aleación"]
        }
        
        luxury_brand_features = {
            "BMW": ["iDrive", "Asientos de cuero", "Faros LED", "Sistema de sonido premium"],
            "Mercedes-Benz": ["MBUX", "Asientos de cuero Artico", "Faros LED Inteligentes", "Sonido Burmester"],
            "Audi": ["MMI", "Asientos de cuero", "Faros Matrix LED", "Sistema Bang & Olufsen"],
            "Tesla": ["Piloto automático", "Pantalla táctil 15\"", "Actualizaciones OTA", "Supercargador"],
            "Lexus": ["Lexus Safety System", "Asientos de cuero", "Sistema Mark Levinson", "Faros LED"]
        }
        
        type_specific_features = {
            "SUV": ["Tracción integral", "Control de descenso", "Barras de techo"],
            "Pickup": ["Caja de carga", "Gancho de remolque", "Tracción 4x4"],
            "Coupé": ["Suspensión deportiva", "Frenos de alto rendimiento", "Escape deportivo"],
            "Convertible": ["Techo convertible", "Barra antivuelco", "Asientos con calefacción"],
            "Hatchback": ["Asientos traseros abatibles", "Portón trasero", "Diseño compacto"],
            "Minivan": ["Puertas corredizas", "Asientos capitán", "8 asientos", "Entretenimiento trasero"]
        }
        
        features = base_features.copy()
        features.extend(premium_features.get(trim_level, []))
        features.extend(luxury_brand_features.get(brand, []))
        features.extend(type_specific_features.get(model_info["tipo"], []))
        
        # Eliminar duplicados y limitar características
        features = list(set(features))[:8]
        
        return features
    
    def create_more_brands_and_cars(self):
        """Crear marcas y autos adicionales para completar la base de datos"""
        additional_models = {
            "Nissan": [
                {"modelo": "Sentra", "tipo": "Sedán", "precio_base": 20000, "segmento": "económico"},
                {"modelo": "Altima", "tipo": "Sedán", "precio_base": 26000, "segmento": "medio"},
                {"modelo": "Rogue", "tipo": "SUV", "precio_base": 28000, "segmento": "compacto"},
                {"modelo": "Pathfinder", "tipo": "SUV", "precio_base": 36000, "segmento": "grande"},
                {"modelo": "Leaf", "tipo": "Hatchback", "precio_base": 32000, "segmento": "eléctrico"},
                {"modelo": "Titan", "tipo": "Pickup", "precio_base": 38000, "segmento": "trabajo"},
                {"modelo": "370Z", "tipo": "Coupé", "precio_base": 35000, "segmento": "deportivo"},
            ],
            "Mazda": [
                {"modelo": "Mazda3", "tipo": "Hatchback", "precio_base": 23000, "segmento": "compacto"},
                {"modelo": "Mazda6", "tipo": "Sedán", "precio_base": 28000, "segmento": "medio"},
                {"modelo": "CX-3", "tipo": "Crossover", "precio_base": 22000, "segmento": "compacto"},
                {"modelo": "CX-5", "tipo": "SUV", "precio_base": 28000, "segmento": "compacto"},
                {"modelo": "CX-9", "tipo": "SUV", "precio_base": 36000, "segmento": "grande"},
                {"modelo": "MX-5", "tipo": "Convertible", "precio_base": 28000, "segmento": "deportivo"},
            ],
            "Subaru": [
                {"modelo": "Impreza", "tipo": "Hatchback", "precio_base": 20000, "segmento": "compacto"},
                {"modelo": "Legacy", "tipo": "Sedán", "precio_base": 24000, "segmento": "medio"},
                {"modelo": "Outback", "tipo": "SUV", "precio_base": 28000, "segmento": "aventura"},
                {"modelo": "Forester", "tipo": "SUV", "precio_base": 26000, "segmento": "compacto"},
                {"modelo": "Ascent", "tipo": "SUV", "precio_base": 34000, "segmento": "familiar"},
                {"modelo": "WRX", "tipo": "Sedán", "precio_base": 32000, "segmento": "deportivo"},
            ],
            "Audi": [
                {"modelo": "A3", "tipo": "Sedán", "precio_base": 35000, "segmento": "lujo_compacto"},
                {"modelo": "A4", "tipo": "Sedán", "precio_base": 42000, "segmento": "lujo"},
                {"modelo": "A6", "tipo": "Sedán", "precio_base": 58000, "segmento": "lujo"},
                {"modelo": "Q3", "tipo": "SUV", "precio_base": 38000, "segmento": "lujo_compacto"},
                {"modelo": "Q5", "tipo": "SUV", "precio_base": 50000, "segmento": "lujo"},
                {"modelo": "Q7", "tipo": "SUV", "precio_base": 68000, "segmento": "lujo_grande"},
                {"modelo": "TT", "tipo": "Coupé", "precio_base": 48000, "segmento": "deportivo"},
            ],
            "Chevrolet": [
                {"modelo": "Spark", "tipo": "Hatchback", "precio_base": 15000, "segmento": "económico"},
                {"modelo": "Cruze", "tipo": "Sedán", "precio_base": 20000, "segmento": "compacto"},
                {"modelo": "Malibu", "tipo": "Sedán", "precio_base": 25000, "segmento": "medio"},
                {"modelo": "Equinox", "tipo": "SUV", "precio_base": 26000, "segmento": "compacto"},
                {"modelo": "Traverse", "tipo": "SUV", "precio_base": 32000, "segmento": "grande"},
                {"modelo": "Silverado", "tipo": "Pickup", "precio_base": 35000, "segmento": "trabajo"},
                {"modelo": "Camaro", "tipo": "Coupé", "precio_base": 28000, "segmento": "deportivo"},
            ],
            "Volkswagen": [
                {"modelo": "Jetta", "tipo": "Sedán", "precio_base": 21000, "segmento": "compacto"},
                {"modelo": "Passat", "tipo": "Sedán", "precio_base": 26000, "segmento": "medio"},
                {"modelo": "Golf", "tipo": "Hatchback", "precio_base": 23000, "segmento": "compacto"},
                {"modelo": "Tiguan", "tipo": "SUV", "precio_base": 28000, "segmento": "compacto"},
                {"modelo": "Atlas", "tipo": "SUV", "precio_base": 34000, "segmento": "grande"},
                {"modelo": "ID.4", "tipo": "SUV", "precio_base": 40000, "segmento": "eléctrico"},
            ],
            "Volvo": [
                {"modelo": "S60", "tipo": "Sedán", "precio_base": 40000, "segmento": "lujo"},
                {"modelo": "S90", "tipo": "Sedán", "precio_base": 52000, "segmento": "lujo"},
                {"modelo": "XC40", "tipo": "SUV", "precio_base": 36000, "segmento": "lujo_compacto"},
                {"modelo": "XC60", "tipo": "SUV", "precio_base": 44000, "segmento": "lujo"},
                {"modelo": "XC90", "tipo": "SUV", "precio_base": 58000, "segmento": "lujo_grande"},
            ],
            "Lexus": [
                {"modelo": "IS", "tipo": "Sedán", "precio_base": 42000, "segmento": "lujo"},
                {"modelo": "ES", "tipo": "Sedán", "precio_base": 46000, "segmento": "lujo"},
                {"modelo": "NX", "tipo": "SUV", "precio_base": 40000, "segmento": "lujo_compacto"},
                {"modelo": "RX", "tipo": "SUV", "precio_base": 48000, "segmento": "lujo"},
                {"modelo": "GX", "tipo": "SUV", "precio_base": 58000, "segmento": "lujo_grande"},
                {"modelo": "LS", "tipo": "Sedán", "precio_base": 78000, "segmento": "ultra_lujo"},
            ]
        }
        
        cars_data = []
        car_id = 1000  # Comenzar desde ID alto para evitar conflictos
        
        # Generar autos para marcas adicionales
        for brand, models in additional_models.items():
            for model_info in models:
                # Crear variaciones del modelo
                for year in [2022, 2023, 2024]:
                    for trim_level in ["Base", "Premium"]:
                        price_modifier = {"Base": 0, "Premium": 4000}
                        final_price = model_info["precio_base"] + price_modifier[trim_level]
                        
                        # Determinar combustible
                        if "eléctrico" in model_info["segmento"]:
                            fuel = "Eléctrico"
                        elif model_info["modelo"] in ["Prius", "Insight", "Accord", "Camry"]:
                            fuel = "Híbrido"
                        else:
                            fuel = self.select_fuel_by_probability(model_info["tipo"])
                        
                        # Determinar transmisión
                        transmission = "Automática" if fuel == "Eléctrico" else ("Manual" if car_id % 4 == 0 else "Automática")
                        
                        # Generar características
                        features = self.generate_features(brand, model_info, trim_level)
                        
                        car = {
                            "id": f"car_{car_id}",
                            "modelo": f"{model_info['modelo']} {trim_level}",
                            "año": year,
                            "precio": final_price,
                            "marca": brand,
                            "tipo": model_info["tipo"],
                            "combustible": fuel,
                            "transmision": transmission,
                            "caracteristicas": features,
                            "segmento": model_info["segmento"],
                            "trim_level": trim_level
                        }
                        
                        cars_data.append(car)
                        car_id += 1
        
        # Crear autos en la base de datos
        with self.driver.session() as session:
            for i, car in enumerate(cars_data, 1):
                if i % 25 == 0:
                    logger.info(f"Creando auto adicional {i}/{len(cars_data)}")
                
                # Crear auto
                session.run("""
                    CREATE (a:Auto {
                        id: $id,
                        modelo: $modelo,
                        año: $año,
                        precio: $precio,
                        caracteristicas: $caracteristicas,
                        segmento: $segmento,
                        trim_level: $trim_level
                    })
                """, **car)
                
                # Crear relaciones
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (m:Marca {nombre: $marca})
                    MERGE (a)-[:ES_MARCA]->(m)
                """, id=car["id"], marca=car["marca"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (t:Tipo {categoria: $tipo})
                    MERGE (a)-[:ES_TIPO]->(t)
                """, id=car["id"], tipo=car["tipo"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (c:Combustible {tipo: $combustible})
                    MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                """, id=car["id"], combustible=car["combustible"])
                
                session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (tr:Transmision {tipo: $transmision})
                    MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                """, id=car["id"], transmision=car["transmision"])
        
        logger.info(f"Creados {len(cars_data)} autos adicionales")
    
    def create_demographic_relationships(self):
        """Crear relaciones entre perfiles demográficos y marcas/tipos"""
        with self.driver.session() as session:
            for profile_id, profile_data in self.demographic_profiles.items():
                # Conectar perfil con marcas recomendadas
                for brand in profile_data["marcas_recomendadas"]:
                    session.run("""
                        MATCH (p:PerfilDemografico {id: $profile_id})
                        MATCH (m:Marca {nombre: $brand})
                        CREATE (p)-[:RECOMIENDA_MARCA {peso: 0.8}]->(m)
                    """, profile_id=profile_id, brand=brand)
                
                # Conectar perfil con tipos de vehículo
                for vehicle_type in profile_data["tipos_vehiculo"]:
                    session.run("""
                        MATCH (p:PerfilDemografico {id: $profile_id})
                        MATCH (t:Tipo {categoria: $vehicle_type})
                        CREATE (p)-[:RECOMIENDA_TIPO {peso: 0.7}]->(t)
                    """, profile_id=profile_id, vehicle_type=vehicle_type)
        
        logger.info("Relaciones demográficas creadas")
    
    def setup_complete_enhanced_database(self):
        """Configurar completamente la base de datos mejorada"""
        logger.info("Iniciando configuración de base de datos mejorada...")
        
        self.clear_database()
        self.create_enhanced_schema()
        self.create_brand_similarities()
        self.create_comprehensive_cars()
        self.create_more_brands_and_cars()
        self.create_demographic_relationships()
        
        logger.info("¡Base de datos mejorada configurada completamente!")
        self.show_enhanced_stats()
    
    def show_enhanced_stats(self):
        """Mostrar estadísticas de la base de datos mejorada"""
        with self.driver.session() as session:
            stats = {}
            
            # Contar nodos
            labels = ["Auto", "Marca", "Tipo", "Combustible", "Transmision", "PerfilDemografico"]
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                stats[label] = result.single()["count"]
            
            # Contar relaciones
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats["Relaciones"] = rel_result.single()["count"]
            
            # Estadísticas específicas
            similarity_result = session.run("MATCH ()-[r:SIMILAR_A]->() RETURN count(r) as count")
            stats["Similitudes entre marcas"] = similarity_result.single()["count"]
            
            demo_result = session.run("MATCH ()-[r:RECOMIENDA_MARCA]->() RETURN count(r) as count")
            stats["Recomendaciones demográficas"] = demo_result.single()["count"]
            
            logger.info("=== ESTADÍSTICAS DE BASE DE DATOS MEJORADA ===")
            for key, value in stats.items():
                logger.info(f"{key}: {value}")
            
            # Mostrar muestra de similitudes
            sample_similarities = session.run("""
                MATCH (m1:Marca)-[r:SIMILAR_A]->(m2:Marca)
                RETURN m1.nombre as marca1, m2.nombre as marca2, r.peso as peso
                ORDER BY r.peso DESC
                LIMIT 5
            """)
            
            logger.info("\n=== MUESTRA DE SIMILITUDES ENTRE MARCAS ===")
            for record in sample_similarities:
                logger.info(f"{record['marca1']} -> {record['marca2']} (peso: {record['peso']:.2f})")
            
            # Mostrar distribución de autos por marca
            brands_distribution = session.run("""
                MATCH (a:Auto)-[:ES_MARCA]->(m:Marca)
                RETURN m.nombre as marca, count(a) as total_autos
                ORDER BY total_autos DESC
                LIMIT 10
            """)
            
            logger.info("\n=== DISTRIBUCIÓN DE AUTOS POR MARCA (TOP 10) ===")
            for record in brands_distribution:
                logger.info(f"{record['marca']}: {record['total_autos']} autos")
            
            # Mostrar autos por segmento de precio
            price_segments = session.run("""
                MATCH (a:Auto)
                WITH 
                    CASE 
                        WHEN a.precio < 25000 THEN 'Económico (<$25k)'
                        WHEN a.precio < 40000 THEN 'Medio ($25k-$40k)'
                        WHEN a.precio < 60000 THEN 'Premium ($40k-$60k)'
                        ELSE 'Lujo ($60k+)'
                    END as segmento,
                    count(a) as total
                RETURN segmento, total
                ORDER BY total DESC
            """)
            
            logger.info("\n=== DISTRIBUCIÓN POR SEGMENTO DE PRECIO ===")
            for record in price_segments:
                logger.info(f"{record['segmento']}: {record['total']} autos")
            
            logger.info("================================================")

def main():
    print("🚀 CONFIGURANDO BASE DE DATOS MEJORADA PARA RECOMENDACIONES INTELIGENTES")
    print("=" * 80)
    
    setup = EnhancedDatabaseSetup()
    
    try:
        setup.setup_complete_enhanced_database()
        
        print("\n🎉 ¡BASE DE DATOS MEJORADA CONFIGURADA EXITOSAMENTE!")
        print("=" * 80)
        print("✅ Marcas con información contextual (origen, características, confiabilidad)")
        print("✅ Perfiles demográficos detallados por género y edad")
        print("✅ Relaciones de similitud entre marcas")
        print("✅ 300+ autos con múltiples variaciones y segmentos")
        print("✅ Sistema preparado para recomendaciones inteligentes")
        print("\n🔄 Siguiente paso: Actualizar el sistema de recomendaciones")
        print("Ejecuta: python app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        setup.close()

if __name__ == "__main__":
    main()
                
                # Crear relaciones
    session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (m:Marca {nombre: $marca})
                    MERGE (a)-[:ES_MARCA]->(m)
                """, id=car["id"], marca=car["marca"])
                
    session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (t:Tipo {categoria: $tipo})
                    MERGE (a)-[:ES_TIPO]->(t)
                """, id=car["id"], tipo=car["tipo"])
                
    session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (c:Combustible {tipo: $combustible})
                    MERGE (a)-[:USA_COMBUSTIBLE]->(c)
                """, id=car["id"], combustible=car["combustible"])
                
    session.run("""
                    MATCH (a:Auto {id: $id})
                    MATCH (tr:Transmision {tipo: $transmision})
                    MERGE (a)-[:TIENE_TRANSMISION]->(tr)
                """, id=car["id"], transmision=car["transmision"])
        
    logger.info(f"Creados {len(cars_data)} autos con relaciones completas")
    
    def select_fuel_by_probability(self, vehicle_type):
        """Seleccionar combustible basado en probabilidades por tipo"""
        import random
        
        fuel_probabilities = {
            "Sedán": {"Gasolina": 0.6, "Híbrido": 0.3, "Eléctrico": 0.1},
            "SUV": {"Gasolina": 0.7, "Híbrido": 0.2, "Eléctrico": 0.1},
            "Hatchback": {"Gasolina": 0.5, "Híbrido": 0.3, "Eléctrico": 0.2},
            "Pickup": {"Gasolina": 0.8, "Diésel": 0.2},
            "Coupé": {"Gasolina": 0.9, "Eléctrico": 0.1},
            "Convertible": {"Gasolina": 0.95, "Eléctrico": 0.05},
            "Crossover": {"Gasolina": 0.6, "Híbrido": 0.3, "Eléctrico": 0.1},
            "Minivan": {"Gasolina": 0.8, "Híbrido": 0.2}
        }
        
        probs = fuel_probabilities.get(vehicle_type, {"Gasolina": 0.7, "Híbrido": 0.2, "Eléctrico": 0.1})
        choices = list(probs.keys())
        weights = list(probs.values())
        
        return random.choices(choices, weights=weights)[0]
    
    def generate_features(self, brand, model_info, trim_level):
        """Generar características realistas basadas en marca, modelo y trim"""
        base_features = ["Aire acondicionado", "Radio AM/FM", "Bluetooth"]
        
        premium_features = {
            "Base": [],
            "Premium": ["Pantalla táctil", "Cámara trasera", "Control crucero", "Asientos de tela premium"],
            "Sport": ["Asientos deportivos", "Volante deportivo", "Suspensión deportiva", "Llantas de aleación"]
        }
        
        luxury_brand_features = {
            "BMW": ["iDrive", "Asientos de cuero", "Faros LED", "Sistema de sonido premium"],
            "Mercedes-Benz": ["MBUX", "Asientos de cuero Artico", "Faros LED Inteligentes", "Sonido Burmester"],
            "Audi": ["MMI", "Asientos de cuero", "Faros Matrix LED", "Sistema Bang & Olufsen"],
            "Tesla": ["Piloto automático", "Pantalla táctil 15\"", "Actualizaciones OTA", "Supercargador"],
            "Lexus": ["Lexus Safety System", "Asientos de cuero", "Sistema Mark Levinson", "Faros LED"]
        }
        
        type_specific_features = {
            "SUV": ["Tracción integral", "Control de descenso", "Barras de techo"],
            "Pickup": ["Caja de carga", "Gancho de remolque", "Tracción 4x4"],
            "Coupé": ["Suspensión deportiva", "Frenos de alto rendimiento", "Escape deportivo"],
            "Convertible": ["Techo convertible", "Barra antivuelco", "Asientos con calefacción"],
            "Hatchback": ["Asientos traseros abatibles", "Portón trasero", "Diseño compacto"],
            "Minivan": ["Puertas corredizas", "Asientos capitán", "8 asientos", "Entretenimiento trasero"]
        }
        
        features = base_features.copy()
        features.extend(premium_features.get(trim_level, []))
        features.extend(luxury_brand_features.get(brand, []))
        features.extend(type_specific_features.get(model_info["tipo"], []))
        
        # Eliminar duplicados y limitar características
        features = list(set(features))[:8]
        
        return features
    
    def create_demographic_relationships(self):
        """Crear relaciones entre perfiles demográficos y marcas/tipos"""
        with self.driver.session() as session:
            for profile_id, profile_data in self.demographic_profiles.items():
                # Conectar perfil con marcas recomendadas
                for brand in profile_data["marcas_recomendadas"]:
                    session.run("""
                        MATCH (p:PerfilDemografico {id: $profile_id})
                        MATCH (m:Marca {nombre: $brand})
                        CREATE (p)-[:RECOMIENDA_MARCA {peso: 0.8}]->(m)
                    """, profile_id=profile_id, brand=brand)
                
                # Conectar perfil con tipos de vehículo
                for vehicle_type in profile_data["tipos_vehiculo"]:
                    session.run("""
                        MATCH (p:PerfilDemografico {id: $profile_id})
                        MATCH (t:Tipo {categoria: $vehicle_type})
                        CREATE (p)-[:RECOMIENDA_TIPO {peso: 0.7}]->(t)
                    """, profile_id=profile_id, vehicle_type=vehicle_type)
        
        logger.info("Relaciones demográficas creadas")
    
    def setup_complete_enhanced_database(self):
        """Configurar completamente la base de datos mejorada"""
        logger.info("Iniciando configuración de base de datos mejorada...")
        
        self.clear_database()
        self.create_enhanced_schema()
        self.create_brand_similarities()
        self.create_comprehensive_cars()
        self.create_demographic_relationships()
        
        logger.info("¡Base de datos mejorada configurada completamente!")
        self.show_enhanced_stats()
    
    def show_enhanced_stats(self):
        """Mostrar estadísticas de la base de datos mejorada"""
        with self.driver.session() as session:
            stats = {}
            
            # Contar nodos
            labels = ["Auto", "Marca", "Tipo", "Combustible", "Transmision", "PerfilDemografico"]
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                stats[label] = result.single()["count"]
            
            # Contar relaciones
            rel_result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            stats["Relaciones"] = rel_result.single()["count"]
            
            # Estadísticas específicas
            similarity_result = session.run("MATCH ()-[r:SIMILAR_A]->() RETURN count(r) as count")
            stats["Similitudes entre marcas"] = similarity_result.single()["count"]
            
            demo_result = session.run("MATCH ()-[r:RECOMIENDA_MARCA]->() RETURN count(r) as count")
            stats["Recomendaciones demográficas"] = demo_result.single()["count"]
            
            logger.info("=== ESTADÍSTICAS DE BASE DE DATOS MEJORADA ===")
            for key, value in stats.items():
                logger.info(f"{key}: {value}")
            
            # Mostrar muestra de similitudes
            sample_similarities = session.run("""
                MATCH (m1:Marca)-[r:SIMILAR_A]->(m2:Marca)
                RETURN m1.nombre as marca1, m2.nombre as marca2, r.peso as peso
                ORDER BY r.peso DESC
                LIMIT 5
            """)
            
            logger.info("\n=== MUESTRA DE SIMILITUDES ENTRE MARCAS ===")
            for record in sample_similarities:
                logger.info(f"{record['marca1']} -> {record['marca2']} (peso: {record['peso']:.2f})")
            
            logger.info("================================================")

def main():
    print("🚀 CONFIGURANDO BASE DE DATOS MEJORADA PARA RECOMENDACIONES INTELIGENTES")
    print("=" * 80)
    
    setup = EnhancedDatabaseSetup()
    
    try:
        setup.setup_complete_enhanced_database()
        
        print("\n🎉 ¡BASE DE DATOS MEJORADA CONFIGURADA EXITOSAMENTE!")
        print("=" * 80)
        print("✅ Marcas con información contextual (origen, características, confiabilidad)")
        print("✅ Perfiles demográficos detallados por género y edad")
        print("✅ Relaciones de similitud entre marcas")
        print("✅ 200+ autos con múltiples variaciones")
        print("✅ Sistema preparado para recomendaciones inteligentes")
        print("\n🔄 Siguiente paso: Actualizar el sistema de recomendaciones")
        print("Ejecuta: python app.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        setup.close()

if __name__ == "__main__":
    main()