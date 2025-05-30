#!/usr/bin/env python3
"""
Script para arreglar completamente la base de datos Neo4j
Borra todo y recrea con relaciones correctas
"""

from neo4j import GraphDatabase

class DatabaseFixer:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "estructura"))
        
    def close(self):
        self.driver.close()
    
    def clear_everything(self):
        """Borrar toda la base de datos"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("✅ Base de datos completamente limpiada")
    
    def create_all_data(self):
        """Crear todos los datos con relaciones correctas"""
        with self.driver.session() as session:
            print("🔧 Creando datos completos...")
            
            # Crear todo en una sola transacción para garantizar consistencia
            session.run("""
                // Crear marcas
                CREATE (toyota:Marca {nombre: 'Toyota'})
                CREATE (honda:Marca {nombre: 'Honda'})
                CREATE (bmw:Marca {nombre: 'BMW'})
                CREATE (tesla:Marca {nombre: 'Tesla'})
                CREATE (ford:Marca {nombre: 'Ford'})
                
                // Crear tipos
                CREATE (sedan:Tipo {categoria: 'Sedán'})
                CREATE (suv:Tipo {categoria: 'SUV'})
                CREATE (hatchback:Tipo {categoria: 'Hatchback'})
                CREATE (pickup:Tipo {categoria: 'Pickup'})
                CREATE (coupe:Tipo {categoria: 'Coupé'})
                
                // Crear combustibles
                CREATE (gasolina:Combustible {tipo: 'Gasolina'})
                CREATE (diesel:Combustible {tipo: 'Diésel'})
                CREATE (electrico:Combustible {tipo: 'Eléctrico'})
                CREATE (hibrido:Combustible {tipo: 'Híbrido'})
                
                // Crear transmisiones
                CREATE (automatica:Transmision {tipo: 'Automática'})
                CREATE (manual:Transmision {tipo: 'Manual'})
                
                // Crear autos Toyota
                CREATE (corolla:Auto {
                    id: 'car_1', 
                    modelo: 'Corolla', 
                    año: 2024, 
                    precio: 25000,
                    caracteristicas: ['Aire acondicionado', 'Radio AM/FM', 'Bluetooth', 'Cámara trasera']
                })
                CREATE (camry:Auto {
                    id: 'car_2', 
                    modelo: 'Camry', 
                    año: 2024, 
                    precio: 32000,
                    caracteristicas: ['Sistema de navegación', 'Bluetooth', 'Sensores de estacionamiento', 'Pantalla táctil']
                })
                CREATE (rav4:Auto {
                    id: 'car_3', 
                    modelo: 'RAV4', 
                    año: 2024, 
                    precio: 35000,
                    caracteristicas: ['Tracción integral', 'Cámara 360°', 'Control crucero adaptativo']
                })
                
                // Crear autos Honda
                CREATE (civic:Auto {
                    id: 'car_4', 
                    modelo: 'Civic', 
                    año: 2024, 
                    precio: 27000,
                    caracteristicas: ['Pantalla táctil', 'Apple CarPlay', 'Sistema de sonido premium']
                })
                CREATE (accord:Auto {
                    id: 'car_5', 
                    modelo: 'Accord', 
                    año: 2024, 
                    precio: 31000,
                    caracteristicas: ['Asientos de cuero', 'Techo corredizo', 'Control crucero']
                })
                CREATE (crv:Auto {
                    id: 'car_6', 
                    modelo: 'CR-V', 
                    año: 2024, 
                    precio: 36000,
                    caracteristicas: ['Asientos calefaccionados', 'Sistema de navegación', 'Cámara trasera']
                })
                
                // Crear autos BMW
                CREATE (bmw3:Auto {
                    id: 'car_7', 
                    modelo: '3 Series', 
                    año: 2024, 
                    precio: 45000,
                    caracteristicas: ['Asientos de cuero', 'Sistema de sonido Harman Kardon', 'Faros LED']
                })
                CREATE (bmwx3:Auto {
                    id: 'car_8', 
                    modelo: 'X3', 
                    año: 2024, 
                    precio: 52000,
                    caracteristicas: ['Tracción integral xDrive', 'Pantalla iDrive', 'Asientos deportivos']
                })
                
                // Crear autos Tesla
                CREATE (model3:Auto {
                    id: 'car_9', 
                    modelo: 'Model 3', 
                    año: 2024, 
                    precio: 42000,
                    caracteristicas: ['Piloto automático', 'Pantalla táctil 15 pulgadas', 'Supercargador incluido', 'Actualizaciones OTA']
                })
                CREATE (modely:Auto {
                    id: 'car_10', 
                    modelo: 'Model Y', 
                    año: 2024, 
                    precio: 48000,
                    caracteristicas: ['Piloto automático', 'Techo panorámico', '7 asientos opcionales', 'Carga rápida']
                })
                
                // Crear autos Ford
                CREATE (mustang:Auto {
                    id: 'car_11', 
                    modelo: 'Mustang', 
                    año: 2024, 
                    precio: 38000,
                    caracteristicas: ['Motor V8', 'Asientos deportivos', 'Sistema de escape deportivo', 'Llantas de aleación']
                })
                CREATE (f150:Auto {
                    id: 'car_12', 
                    modelo: 'F-150', 
                    año: 2024, 
                    precio: 45000,
                    caracteristicas: ['Caja de carga de aluminio', 'Tracción 4x4', 'Remolque hasta 5000kg', 'Pantalla SYNC']
                })
                
                // CREAR TODAS LAS RELACIONES
                
                // Toyota - Relaciones
                CREATE (corolla)-[:ES_MARCA]->(toyota)
                CREATE (corolla)-[:ES_TIPO]->(sedan)
                CREATE (corolla)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (corolla)-[:TIENE_TRANSMISION]->(automatica)
                
                CREATE (camry)-[:ES_MARCA]->(toyota)
                CREATE (camry)-[:ES_TIPO]->(sedan)
                CREATE (camry)-[:USA_COMBUSTIBLE]->(hibrido)
                CREATE (camry)-[:TIENE_TRANSMISION]->(automatica)
                
                CREATE (rav4)-[:ES_MARCA]->(toyota)
                CREATE (rav4)-[:ES_TIPO]->(suv)
                CREATE (rav4)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (rav4)-[:TIENE_TRANSMISION]->(automatica)
                
                // Honda - Relaciones
                CREATE (civic)-[:ES_MARCA]->(honda)
                CREATE (civic)-[:ES_TIPO]->(sedan)
                CREATE (civic)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (civic)-[:TIENE_TRANSMISION]->(manual)
                
                CREATE (accord)-[:ES_MARCA]->(honda)
                CREATE (accord)-[:ES_TIPO]->(sedan)
                CREATE (accord)-[:USA_COMBUSTIBLE]->(hibrido)
                CREATE (accord)-[:TIENE_TRANSMISION]->(automatica)
                
                CREATE (crv)-[:ES_MARCA]->(honda)
                CREATE (crv)-[:ES_TIPO]->(suv)
                CREATE (crv)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (crv)-[:TIENE_TRANSMISION]->(automatica)
                
                // BMW - Relaciones
                CREATE (bmw3)-[:ES_MARCA]->(bmw)
                CREATE (bmw3)-[:ES_TIPO]->(sedan)
                CREATE (bmw3)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (bmw3)-[:TIENE_TRANSMISION]->(automatica)
                
                CREATE (bmwx3)-[:ES_MARCA]->(bmw)
                CREATE (bmwx3)-[:ES_TIPO]->(suv)
                CREATE (bmwx3)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (bmwx3)-[:TIENE_TRANSMISION]->(automatica)
                
                // Tesla - Relaciones
                CREATE (model3)-[:ES_MARCA]->(tesla)
                CREATE (model3)-[:ES_TIPO]->(sedan)
                CREATE (model3)-[:USA_COMBUSTIBLE]->(electrico)
                CREATE (model3)-[:TIENE_TRANSMISION]->(automatica)
                
                CREATE (modely)-[:ES_MARCA]->(tesla)
                CREATE (modely)-[:ES_TIPO]->(suv)
                CREATE (modely)-[:USA_COMBUSTIBLE]->(electrico)
                CREATE (modely)-[:TIENE_TRANSMISION]->(automatica)
                
                // Ford - Relaciones
                CREATE (mustang)-[:ES_MARCA]->(ford)
                CREATE (mustang)-[:ES_TIPO]->(coupe)
                CREATE (mustang)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (mustang)-[:TIENE_TRANSMISION]->(manual)
                
                CREATE (f150)-[:ES_MARCA]->(ford)
                CREATE (f150)-[:ES_TIPO]->(pickup)
                CREATE (f150)-[:USA_COMBUSTIBLE]->(gasolina)
                CREATE (f150)-[:TIENE_TRANSMISION]->(automatica)
            """)
            
            print("✅ Todos los datos y relaciones creados correctamente")
    
    def verify_data(self):
        """Verificar que todo esté creado correctamente"""
        with self.driver.session() as session:
            print("\n🔍 VERIFICANDO BASE DE DATOS:")
            
            # Contar nodos
            labels = ["Auto", "Marca", "Tipo", "Combustible", "Transmision"]
            for label in labels:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = result.single()["count"]
                print(f"  {label}: {count} nodos")
            
            # Contar relaciones
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            rel_count = result.single()["count"]
            print(f"  Relaciones: {rel_count} total")
            
            # Verificar que cada auto tenga todas sus relaciones
            print("\n🔗 VERIFICANDO RELACIONES POR AUTO:")
            result = session.run("""
                MATCH (a:Auto)
                OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                OPTIONAL MATCH (a)-[:ES_TIPO]->(t:Tipo)
                OPTIONAL MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                OPTIONAL MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                RETURN a.modelo as modelo, 
                       m.nombre as marca, 
                       t.categoria as tipo, 
                       c.tipo as combustible, 
                       tr.tipo as transmision
                ORDER BY a.modelo
            """)
            
            for record in result:
                modelo = record["modelo"]
                marca = record["marca"] or "❌ SIN MARCA"
                tipo = record["tipo"] or "❌ SIN TIPO"
                combustible = record["combustible"] or "❌ SIN COMBUSTIBLE"
                transmision = record["transmision"] or "❌ SIN TRANSMISION"
                
                status = "✅" if all([record["marca"], record["tipo"], record["combustible"], record["transmision"]]) else "❌"
                print(f"  {status} {modelo}: {marca} | {tipo} | {combustible} | {transmision}")
    
    def test_queries(self):
        """Probar consultas como las que usa el sistema de recomendaciones"""
        with self.driver.session() as session:
            print("\n🧪 PROBANDO CONSULTAS DE RECOMENDACIONES:")
            
            # Prueba 1: Buscar todos los autos
            result = session.run("""
                MATCH (a:Auto)
                OPTIONAL MATCH (a)-[:ES_MARCA]->(m:Marca)
                RETURN count(a) as total
            """)
            total = result.single()["total"]
            print(f"  Total de autos: {total}")
            
            # Prueba 2: Buscar autos Toyota
            result = session.run("""
                MATCH (a:Auto)-[:ES_MARCA]->(m:Marca {nombre: 'Toyota'})
                RETURN count(a) as total
            """)
            toyota_count = result.single()["total"]
            print(f"  Autos Toyota: {toyota_count}")
            
            # Prueba 3: Buscar sedanes
            result = session.run("""
                MATCH (a:Auto)-[:ES_TIPO]->(t:Tipo {categoria: 'Sedán'})
                RETURN count(a) as total
            """)
            sedan_count = result.single()["total"]
            print(f"  Autos Sedán: {sedan_count}")
            
            # Prueba 4: Buscar autos con gasolina
            result = session.run("""
                MATCH (a:Auto)-[:USA_COMBUSTIBLE]->(c:Combustible {tipo: 'Gasolina'})
                RETURN count(a) as total
            """)
            gas_count = result.single()["total"]
            print(f"  Autos a gasolina: {gas_count}")
            
            # Prueba 5: Consulta compleja (como la del sistema)
            result = session.run("""
                MATCH (a:Auto)
                WHERE a.precio >= 20000 AND a.precio <= 50000
                MATCH (a)-[:ES_MARCA]->(m:Marca)
                WHERE m.nombre IN ['Toyota', 'Honda']
                MATCH (a)-[:USA_COMBUSTIBLE]->(c:Combustible)
                WHERE c.tipo = 'Gasolina'
                MATCH (a)-[:ES_TIPO]->(t:Tipo)
                WHERE t.categoria = 'Sedán'
                MATCH (a)-[:TIENE_TRANSMISION]->(tr:Transmision)
                WHERE tr.tipo = 'Automática'
                RETURN count(a) as total
            """)
            complex_count = result.single()["total"]
            print(f"  Consulta compleja (Toyota/Honda, Sedán, Gasolina, Automática, $20k-50k): {complex_count}")

def main():
    print("🔧 ARREGLANDO BASE DE DATOS NEO4J")
    print("=" * 50)
    
    fixer = DatabaseFixer()
    
    try:
        # Paso 1: Limpiar todo
        print("1️⃣ Limpiando base de datos...")
        fixer.clear_everything()
        
        # Paso 2: Crear todo de nuevo
        print("\n2️⃣ Creando datos y relaciones...")
        fixer.create_all_data()
        
        # Paso 3: Verificar
        print("\n3️⃣ Verificando resultado...")
        fixer.verify_data()
        
        # Paso 4: Probar consultas
        print("\n4️⃣ Probando consultas...")
        fixer.test_queries()
        
        print("\n🎉 ¡BASE DE DATOS ARREGLADA COMPLETAMENTE!")
        print("=" * 50)
        print("✅ Ahora puedes ejecutar:")
        print("   python app.py")
        print("✅ Y el sistema de recomendaciones debería funcionar perfectamente")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        fixer.close()

if __name__ == "__main__":
    main()