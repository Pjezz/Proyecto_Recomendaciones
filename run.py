#!/usr/bin/env python3
"""
Script principal para ejecutar el Sistema de Recomendaciones de Autos
"""

import sys
import os
from pathlib import Path

# Agregar la carpeta app al path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

try:
    from app import app
    
    if __name__ == "__main__":
        print("🚗 Iniciando Sistema de Recomendaciones de Autos...")
        print("🌐 Disponible en: http://localhost:5000")
        print("🛑 Para detener: Ctrl+C")
        print()
        
        app.run(debug=True, port=5000)
        
except ImportError as e:
    print(f"❌ Error importando la aplicación: {e}")
    print("💡 Asegúrate de haber ejecutado: python setup.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error ejecutando la aplicación: {e}")
    sys.exit(1)
