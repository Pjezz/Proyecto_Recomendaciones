#!/usr/bin/env python3
"""
Script para reorganizar automáticamente la estructura del proyecto
Mueve archivos a carpetas apropiadas según su función
"""

import os
import shutil
from pathlib import Path

class ProjectReorganizer:
    def __init__(self):
        self.root = Path.cwd()
        
        # Definir estructura objetivo
        self.structure = {
            'app/': [
                'app.py',
                'recommender_minimal.py',
                'recommender.py',
                'templates/',
                'static/'
            ],
            'scripts/setup/': [
                'expand_database.py',
                'setup_minimal.py',
                'fix_database.py'
            ],
            'scripts/debug/': [
                'debug_recommendations.py',
                'test_neo4j_connection.py',
                'find_neo4j_password.py'
            ],
            'scripts/maintenance/': [
                # Scripts futuros de mantenimiento
            ],
            'docs/': [
                'README.md',
                'DOCS.md', 
                'CHANGELOG.md'
            ],
            'config/': [
                'requirements_minimal.txt',
                'requirements.txt'
            ],
            'tests/': [
                # Tests futuros
            ]
        }
    
    def create_directories(self):
        """Crear estructura de directorios"""
        print("📁 Creando estructura de directorios...")
        
        for directory in self.structure.keys():
            dir_path = self.root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"   ✅ {directory}")
    
    def move_files(self):
        """Mover archivos a sus ubicaciones correctas"""
        print("\n📦 Moviendo archivos...")
        
        for target_dir, files in self.structure.items():
            for file_item in files:
                source = self.root / file_item
                target = self.root / target_dir / file_item
                
                if source.exists():
                    if source.is_dir():
                        if target.exists():
                            shutil.rmtree(target)
                        shutil.move(str(source), str(target))
                        print(f"   📁 {file_item} → {target_dir}")
                    else:
                        if target.exists():
                            target.unlink()
                        shutil.move(str(source), str(target))
                        print(f"   📄 {file_item} → {target_dir}")
                else:
                    print(f"   ⚠️  {file_item} no encontrado")
    
    def create_new_main_script(self):
        """Crear nuevo script principal simplificado"""
        print("\n🚀 Creando script principal...")
        
        main_script = '''#!/usr/bin/env python3
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
'''
        
        with open(self.root / "run.py", "w", encoding="utf-8") as f:
            f.write(main_script)
        
        print("   ✅ run.py creado")
    
    def update_setup_script(self):
        """Actualizar setup.py para nueva estructura"""
        print("\n🔧 Actualizando setup.py...")
        
        setup_updates = '''
# Actualizar rutas en setup.py
# Cambiar referencias de archivos a nueva estructura:
# expand_database.py → scripts/setup/expand_database.py
# debug_recommendations.py → scripts/debug/debug_recommendations.py
'''
        
        print("   📝 Actualización manual requerida para setup.py")
        print("   Ver comentarios en el archivo para los cambios necesarios")
    
    def create_gitignore(self):
        """Crear archivo .gitignore apropiado"""
        print("\n🙈 Creando .gitignore...")
        
        gitignore_content = '''# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv/
pip-log.txt
pip-delete-this-directory.txt

# Flask
instance/
.webassets-cache

# Neo4j
*.db
*.log

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db
.env

# Testing
.coverage
.pytest_cache/
.tox/

# Logs
*.log
logs/

# Backup files
*.bak
*.backup
*.tmp

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
'''
        
        with open(self.root / ".gitignore", "w", encoding="utf-8") as f:
            f.write(gitignore_content)
        
        print("   ✅ .gitignore creado")
    
    def create_readme_update(self):
        """Crear README actualizado para nueva estructura"""
        print("\n📖 Creando README actualizado...")
        
        readme_update = '''# 🚗 Sistema de Recomendaciones de Autos

> **Nota**: Este proyecto ha sido reorganizado para mejor estructura y mantenimiento.

## 🚀 Inicio rápido

```bash
# 1. Configuración automática
python setup.py

# 2. Ejecutar aplicación
python run.py
```

## 📁 Estructura del proyecto

```
├── app/                    # Aplicación principal
├── scripts/               # Scripts de utilidad
│   ├── setup/            # Configuración inicial
│   ├── debug/            # Diagnóstico
│   └── maintenance/      # Mantenimiento
├── docs/                 # Documentación
├── config/               # Configuración
└── tests/                # Tests automatizados
```

## 🔧 Scripts disponibles

### Configuración
- `python scripts/setup/expand_database.py` - Popular base de datos
- `python scripts/debug/debug_recommendations.py` - Diagnosticar sistema

### Ejecución
- `python run.py` - Ejecutar aplicación principal
- `python setup.py` - Configuración automática inicial

Ver documentación completa en `docs/README.md`
'''
        
        with open(self.root / "README.md", "w", encoding="utf-8") as f:
            f.write(readme_update)
        
        print("   ✅ README.md actualizado")
    
    def show_summary(self):
        """Mostrar resumen de cambios"""
        print("\n" + "="*60)
        print("🎉 REORGANIZACIÓN COMPLETADA")
        print("="*60)
        print()
        print("📋 Cambios realizados:")
        print("   ✅ Estructura de directorios creada")
        print("   ✅ Archivos movidos a carpetas apropiadas")  
        print("   ✅ Script principal simplificado (run.py)")
        print("   ✅ .gitignore creado")
        print("   ✅ README actualizado")
        print()
        print("🔄 Acciones manuales requeridas:")
        print("   📝 Actualizar setup.py para nuevas rutas")
        print("   📝 Actualizar imports en app.py si es necesario")
        print("   📝 Revisar documentación en docs/")
        print()
        print("🚀 Para ejecutar:")
        print("   python run.py")
        print()
        print("🧹 Beneficios de la nueva estructura:")
        print("   • Código principal separado de scripts utilitarios")
        print("   • Documentación organizada")
        print("   • Fácil mantenimiento y escalabilidad")
        print("   • Estructura profesional estándar")
    
    def reorganize(self):
        """Ejecutar reorganización completa"""
        print("🔄 REORGANIZANDO PROYECTO...")
        print("="*50)
        
        try:
            self.create_directories()
            self.move_files()
            self.create_new_main_script()
            self.update_setup_script()
            self.create_gitignore()
            self.create_readme_update()
            self.show_summary()
            
        except Exception as e:
            print(f"\n❌ Error durante reorganización: {e}")
            print("💡 Revisa permisos de archivos y directorios")

def main():
    """Función principal"""
    print("🚗 REORGANIZADOR DE PROYECTO - Sistema de Recomendaciones")
    print()
    
    reorganizer = ProjectReorganizer()
    
    # Confirmar acción
    response = input("¿Reorganizar estructura del proyecto? (s/n): ").lower()
    
    if response.startswith('s'):
        reorganizer.reorganize()
    else:
        print("❌ Reorganización cancelada")

if __name__ == "__main__":
    main()