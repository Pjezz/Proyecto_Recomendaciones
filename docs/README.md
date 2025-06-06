# 🚗 Sistema de Recomendaciones de Autos

Sistema inteligente de recomendaciones de automóviles usando Neo4j y Flask.

## 🚀 Inicio Rápido

### Prerrequisitos
1. **Python 3.8+** instalado
2. **Neo4j Desktop** instalado y funcionando
3. Una base de datos Neo4j activa

### Paso 1: Configurar Neo4j
1. Abre **Neo4j Desktop**
2. Crea una nueva base de datos:
   - Nombre: `RecomendacionesAutos`
   - Contraseña: `estructura`
3. **Inicia** la base de datos (debe mostrar "ACTIVE")

### Paso 2: Instalar dependencias
```bash
pip install flask flask-cors neo4j
```

### Paso 3: Configurar la base de datos (PRIMERA VEZ)
```bash
# Opción 1: Configuración básica
python scripts/setup/setup_minimal.py

# Opción 2: Configuración completa
python setup_neo4j_database.py

# Opción 3: Si tienes problemas, usar fix
python scripts/setup/fix_database.py
```

### Opcional: Expandir con más autos
```bash
# Solo después de la configuración inicial
python scripts/setup/expand_database.py
```

### Paso 4: Ejecutar la aplicación
```bash
# Opción 1: Desde la carpeta raíz
python run.py

# Opción 2: Directamente desde app
cd app
python app.py
```

### Paso 5: Usar la aplicación
1. Ve a: http://localhost:5000
2. Inicia sesión con cualquier usuario/contraseña
3. Sigue el flujo de selección de preferencias
4. ¡Recibe tus recomendaciones personalizadas!

## 🛠️ Scripts Disponibles

### Configuración
- `python setup_neo4j_database.py` - Configuración inicial completa
- `python scripts/setup/setup_minimal.py` - Configuración básica  
- `python scripts/setup/fix_database.py` - Reparar/recrear base de datos
- `python scripts/setup/expand_database.py` - Agregar más autos (después de configuración inicial)

### Diagnóstico
- `python scripts/debug/debug_recommendations.py` - Probar sistema completo
- `python test_neo4j_connecction.py` - Diagnosticar conexión Neo4j

### Ejecución
- `python app.py` - Ejecutar desde carpeta app/ (método principal)
- `python run.py` - Ejecutar desde raíz del proyecto

## 📁 Estructura del Proyecto

```
├── app/                    # Aplicación Flask principal
│   ├── app.py             # Servidor Flask
│   ├── recommender.py     # Sistema de recomendaciones
│   ├── templates/         # Páginas HTML
│   └── static/           # CSS, JS, imágenes
├── scripts/              # Scripts de utilidad
│   ├── setup/           # Configuración inicial
│   ├── debug/           # Diagnóstico
│   └── maintenance/     # Mantenimiento
├── config/              # Archivos de configuración
├── docs/                # Documentación
└── run.py              # Script principal de ejecución
```

## 🔧 Solución de Problemas

### Error: "No module named 'flask_cors'"
```bash
pip install flask-cors
```

### Error: "No se puede conectar a Neo4j"
1. Verifica que Neo4j Desktop esté corriendo
2. Asegúrate de que tu base de datos esté ACTIVE
3. Ejecuta: `python test_neo4j_connecction.py`

### Error: "No se encontraron recomendaciones"
```bash
# Si es primera vez, configurar base de datos:
python setup_neo4j_database.py

# Si ya tienes datos pero quieres más autos:
python scripts/setup/expand_database.py
```

### La aplicación no inicia
```bash
# Método principal - desde la carpeta app
cd app
python app.py

# Método alternativo - desde raíz
python run.py

# Verifica que estés en la carpeta correcta del proyecto
```

## 🎯 Características

- **Interfaz intuitiva**: Flujo paso a paso para seleccionar preferencias
- **Recomendaciones inteligentes**: Basadas en marcas, presupuesto, combustible, etc.
- **Base de datos robusta**: 60+ autos con múltiples configuraciones
- **Sistema de puntuación**: Algoritmo que calcula compatibilidad
- **Responsive**: Funciona en móviles y desktop

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu característica
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📞 Soporte

Si tienes problemas:
1. Ejecuta `python scripts/debug/debug_recommendations.py`
2. Revisa la sección "Solución de Problemas"
3. Verifica que Neo4j esté funcionando correctamente