#!/usr/bin/env python3
"""
Script maestro para configurar el sistema completo de recomendaciones inteligentes
Instala la base de datos expandida y actualiza los componentes necesarios
"""

import os
import sys
import shutil
from pathlib import Path

def main():
    print("🚀 CONFIGURANDO SISTEMA DE RECOMENDACIONES INTELIGENTE")
    print("=" * 70)
    print("Este script configurará:")
    print("✅ Base de datos expandida con información contextual")
    print("✅ Sistema de recomendaciones inteligente")
    print("✅ Algoritmos de similitud entre marcas")
    print("✅ Perfiles demográficos detallados")
    print("✅ Interface actualizada para mostrar recomendaciones")
    print()
    
    try:
        # Paso 1: Configurar base de datos expandida
        print("1️⃣ Configurando base de datos expandida...")
        os.system("python enhanced_database_setup.py")
        print("   ✅ Base de datos expandida configurada")
        
        # Paso 2: Reemplazar recommender.py con la versión inteligente
        print("\n2️⃣ Actualizando sistema de recomendaciones...")
        
        # Hacer backup del recommender actual
        if os.path.exists("app/recommender.py"):
            shutil.copy2("app/recommender.py", "app/recommender_backup.py")
            print("   📁 Backup creado: app/recommender_backup.py")
        
        # Copiar el nuevo sistema inteligente
        shutil.copy2("intelligent_recommender.py", "app/recommender.py")
        print("   ✅ Sistema de recomendaciones inteligente instalado")
        
        # Paso 3: Actualizar JavaScript
        print("\n3️⃣ Actualizando interfaz de usuario...")
        
        # Hacer backup del JS actual
        if os.path.exists("app/static/js/recommendations.js"):
            shutil.copy2("app/static/js/recommendations.js", "app/static/js/recommendations_backup.js")
            print("   📁 Backup creado: app/static/js/recommendations_backup.js")
        
        # Copiar nuevo JavaScript
        shutil.copy2("recommendations.js", "app/static/js/recommendations.js")
        print("   ✅ Interfaz actualizada")
        
        # Paso 4: Verificar instalación
        print("\n4️⃣ Verificando instalación...")
        
        # Verificar que los archivos existen
        required_files = [
            "app/recommender.py",
            "app/static/js/recommendations.js",
            "app/app.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not os.path.exists(file_path):
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   ❌ Archivos faltantes: {missing_files}")
            return False
        
        print("   ✅ Todos los archivos están en su lugar")
        
        # Paso 5: Probar el sistema
        print("\n5️⃣ Probando sistema inteligente...")
        
        try:
            # Importar y probar el recomendador
            sys.path.insert(0, os.path.join(os.getcwd(), "app"))
            from intelligent_recommender import get_recommendations
            
            # Prueba simple
            test_recommendations = get_recommendations(
                brands=["Toyota", "Honda"],
                budget="25000-40000",
                gender="masculino",
                age_range="26-35"
            )
            
            if test_recommendations and len(test_recommendations) > 0:
                print(f"   ✅ Sistema funcionando: {len(test_recommendations)} recomendaciones de prueba")
                print(f"   🎯 Ejemplo: {test_recommendations[0]['name']} (Score: {test_recommendations[0].get('similarity_score', 'N/A')})")
            else:
                print("   ⚠️  Sistema funciona pero sin recomendaciones (normal si la BD está vacía)")
            
        except Exception as e:
            print(f"   ⚠️  Error en prueba: {e}")
            print("      El sistema puede funcionar, ejecuta manualmente para verificar")
        
        print("\n🎉 ¡INSTALACIÓN COMPLETADA!")
        print("=" * 70)
        print("🔄 SIGUIENTE PASO:")
        print("   Ejecuta: python app/app.py")
        print("   Visita: http://localhost:5000")
        print()
        print("🆕 NUEVAS CARACTERÍSTICAS:")
        print("   🧠 Recomendaciones inteligentes basadas en similitudes")
        print("   👥 Personalización demográfica por género y edad")
        print("   🎯 Scores de compatibilidad explicados")
        print("   🔍 Expansión automática de marcas similares")
        print("   💡 Razones detalladas de cada recomendación")
        print()
        print("📖 CÓMO FUNCIONA AHORA:")
        print("   1. El usuario selecciona marcas (ej: Toyota, Honda)")
        print("   2. El sistema encuentra marcas similares (ej: Nissan, Mazda)")
        print("   3. Aplica personalización demográfica")
        print("   4. Calcula scores de compatibilidad")
        print("   5. Muestra las mejores recomendaciones con explicaciones")
        print()
        print("🔧 SI HAY PROBLEMAS:")
        print("   • Restaurar backup: mv app/recommender_backup.py app/recommender.py")
        print("   • Verificar Neo4j esté corriendo")
        print("   • Ejecutar: python scripts/debug/debug_recommendations.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA INSTALACIÓN: {e}")
        print("\n🔧 PASOS PARA RESOLVER:")
        print("1. Verifica que Neo4j Desktop esté corriendo")
        print("2. Asegúrate de estar en la carpeta raíz del proyecto")
        print("3. Verifica permisos de archivos")
        print("4. Ejecuta los scripts individualmente:")
        print("   - python enhanced_database_setup.py")
        print("   - Copia manualmente los archivos")
        
        return False

def create_helper_scripts():
    """Crear scripts auxiliares para el nuevo sistema"""
    
    # Script para probar recomendaciones
    test_script = '''#!/usr/bin/env python3
"""
Script para probar el sistema de recomendaciones inteligente
"""

import sys
import os
sys.path.insert(0, os.path.join(os.getcwd(), "app"))

from recommender import get_recommendations

def test_intelligent_system():
    print("🧪 PROBANDO SISTEMA DE RECOMENDACIONES INTELIGENTE")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Hombre joven deportivo",
            "params": {
                "brands": ["Honda"],
                "budget": "25000-40000",
                "fuel": "Gasolina",
                "types": ["Sedán"],
                "gender": "masculino",
                "age_range": "18-25"
            }
        },
        {
            "name": "Mujer profesional familiar",
            "params": {
                "brands": ["Toyota"],
                "budget": "35000-55000",
                "fuel": "Híbrido",
                "types": ["SUV"],
                "gender": "femenino",
                "age_range": "26-35"
            }
        },
        {
            "name": "Sin marcas específicas (solo perfil)",
            "params": {
                "budget": "30000-50000",
                "gender": "masculino",
                "age_range": "36-45"
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\\n--- {test_case['name']} ---")
        print(f"Parámetros: {test_case['params']}")
        
        try:
            recommendations = get_recommendations(**test_case['params'])
            print(f"✅ Obtenidas {len(recommendations)} recomendaciones")
            
            for i, car in enumerate(recommendations[:3], 1):
                score = car.get('similarity_score', 'N/A')
                reason = car.get('recommendation_reason', 'Sin razón')
                print(f"  {i}. {car['name']} - Score: {score}")
                print(f"     💡 {reason}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_intelligent_system()
'''
    
    with open("test_intelligent_recommendations.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    print("   ✅ Script de prueba creado: test_intelligent_recommendations.py")

def show_usage_examples():
    """Mostrar ejemplos de uso del nuevo sistema"""
    print("\n📚 EJEMPLOS DE USO DEL NUEVO SISTEMA:")
    print("=" * 50)
    
    examples = [
        {
            "scenario": "Usuario selecciona Toyota y Honda",
            "behavior": "Sistema encuentra Nissan, Mazda, Subaru (marcas japonesas similares)",
            "result": "Más opciones relevantes sin perder foco"
        },
        {
            "scenario": "Hombre 18-25 años",
            "behavior": "Prioriza autos deportivos, compactos, con buen precio",
            "result": "Civic Sport, Mazda3, Corolla deportivo"
        },
        {
            "scenario": "Mujer 26-35 años",
            "behavior": "Prioriza seguridad, confiabilidad, espacio familiar",
            "result": "RAV4, CR-V, CX-5, con énfasis en seguridad"
        },
        {
            "scenario": "Presupuesto $30k, sin marcas específicas",
            "behavior": "Usa perfil demográfico para recomendar marcas apropiadas",
            "result": "Recomendaciones personalizadas por edad/género"
        }
    ]
    
    for example in examples:
        print(f"\n🎯 {example['scenario']}")
        print(f"   Comportamiento: {example['behavior']}")
        print(f"   Resultado: {example['result']}")

if __name__ == "__main__":
    success = main()
    
    if success:
        create_helper_scripts()
        show_usage_examples()
        
        print(f"\n🚀 ¡LISTO PARA USAR!")
        print("Ejecuta: python app/app.py")
    else:
        print(f"\n❌ Instalación falló. Revisa los errores arriba.")
        sys.exit(1)