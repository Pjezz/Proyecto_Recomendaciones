from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import traceback

# Importar el sistema de recomendaciones
try:
    from recommender_minimal import get_recommendations
    RECOMMENDER_AVAILABLE = True
    print("✅ Usando recommender_minimal.py")
except ImportError as e:
    try:
        from recommender import get_recommendations
        RECOMMENDER_AVAILABLE = True
        print("✅ Usando recommender.py")
    except ImportError as e2:
        print(f"❌ Warning: No se pudo importar sistema de recomendaciones: {e2}")
        RECOMMENDER_AVAILABLE = False

app = Flask(__name__)
CORS(app)
app.secret_key = 'tu_clave_secreta_aqui_cambiala_por_una_segura'

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")
        
        # Aquí puedes agregar validación real de usuario/contraseña
        if username and password:
            session['logged_in'] = True
            session['username'] = username
            print(f"✅ Usuario logueado: {username}")
            return jsonify({"success": True, "redirect": url_for("brands")})
        else:
            return jsonify({"success": False, "message": "Credenciales inválidas"})
    
    return render_template("login.html")

@app.route("/brands")
def brands():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("brands.html")

@app.route("/budget")
def budget():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not session.get('selected_brands'):
        return redirect(url_for('brands'))
    return render_template("budget.html")

@app.route("/fuel")
def fuel():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not session.get('selected_budget'):
        return redirect(url_for('budget'))
    return render_template("fuel.html")

@app.route("/type")
def type_page():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not session.get('selected_fuel'):
        return redirect(url_for('fuel'))
    return render_template("type.html")

@app.route("/transmission")
def transmission():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not session.get('selected_types'):
        return redirect(url_for('type_page'))
    return render_template("transmission.html")

@app.route("/recommendations")
def recommendations():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if not session.get('selected_transmission'):
        return redirect(url_for('transmission'))
    return render_template("recommendations.html")

# API Endpoints para guardar selecciones
@app.route("/api/save-brands", methods=["POST"])
def save_brands():
    try:
        data = request.get_json()
        brands_data = data.get('brands')
        print(f"🏷️ Guardando brands: {brands_data}")
        session['selected_brands'] = brands_data
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error guardando brands: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/save-budget", methods=["POST"])
def save_budget():
    try:
        data = request.get_json()
        budget_data = data.get('budget')
        print(f"💰 Guardando budget: {budget_data}")
        session['selected_budget'] = budget_data
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error guardando budget: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/save-fuel", methods=["POST"])
def save_fuel():
    try:
        data = request.get_json()
        fuel_data = data.get('fuel')
        print(f"⛽ Guardando fuel: {fuel_data}")
        session['selected_fuel'] = fuel_data
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error guardando fuel: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/save-types", methods=["POST"])
def save_types():
    try:
        data = request.get_json()
        types_data = data.get('types')
        print(f"🚗 Guardando types: {types_data}")
        session['selected_types'] = types_data
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error guardando types: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/save-transmission", methods=["POST"])
def save_transmission():
    try:
        data = request.get_json()
        transmission_data = data.get('transmission')
        print(f"⚙️ Guardando transmission: {transmission_data}")
        session['selected_transmission'] = transmission_data
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error guardando transmission: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/recommendations", methods=["GET"])
def api_recommendations():
    try:
        print("\n" + "="*60)
        print("🎯 API RECOMMENDATIONS - INICIANDO")
        print("="*60)
        
        # Obtener datos de la sesión
        brands = session.get('selected_brands')
        budget = session.get('selected_budget')
        fuel = session.get('selected_fuel')
        types = session.get('selected_types')
        transmission = session.get('selected_transmission')
        
        # Debug detallado
        print("📊 DATOS DE SESIÓN:")
        print(f"  🏷️  Brands: {brands} (tipo: {type(brands)})")
        print(f"  💰 Budget: {budget} (tipo: {type(budget)})")
        print(f"  ⛽ Fuel: {fuel} (tipo: {type(fuel)})")
        print(f"  🚗 Types: {types} (tipo: {type(types)})")
        print(f"  ⚙️  Transmission: {transmission} (tipo: {type(transmission)})")
        print(f"  👤 Usuario: {session.get('username', 'N/A')}")
        
        # Verificar que todos los datos estén presentes
        missing_data = []
        if not brands: missing_data.append("brands")
        if not budget: missing_data.append("budget")
        if not fuel: missing_data.append("fuel")
        if not types: missing_data.append("types")
        if not transmission: missing_data.append("transmission")
        
        if missing_data:
            print(f"❌ FALTAN DATOS: {', '.join(missing_data)}")
            return jsonify({
                "error": f"Faltan datos de selección: {', '.join(missing_data)}",
                "session_data": {
                    "brands": brands,
                    "budget": budget,
                    "fuel": fuel,
                    "types": types,
                    "transmission": transmission
                },
                "missing": missing_data
            }), 400
        
        print("✅ TODOS LOS DATOS PRESENTES")
        
        # Si el sistema de recomendaciones no está disponible, usar datos de ejemplo
        if not RECOMMENDER_AVAILABLE:
            print("⚠️ RECOMMENDER NO DISPONIBLE - Usando datos de ejemplo")
            sample_recommendations = [
                {
                    "id": "sample_1",
                    "name": "Toyota Corolla 2024",
                    "model": "Corolla",
                    "brand": "Toyota",
                    "year": 2024,
                    "price": 25000,
                    "type": "Sedán",
                    "fuel": "Gasolina",
                    "transmission": "Automática",
                    "features": ["Aire acondicionado", "Radio AM/FM", "Bluetooth"],
                    "similarity_score": 85.0,
                    "image": None
                },
                {
                    "id": "sample_2",
                    "name": "Honda Civic 2024",
                    "model": "Civic",
                    "brand": "Honda",
                    "year": 2024,
                    "price": 27000,
                    "type": "Sedán",
                    "fuel": "Gasolina",
                    "transmission": "Manual",
                    "features": ["Pantalla táctil", "Bluetooth", "Control crucero"],
                    "similarity_score": 80.0,
                    "image": None
                },
                {
                    "id": "sample_3",
                    "name": "BMW 3 Series 2024",
                    "model": "3 Series",
                    "brand": "BMW",
                    "year": 2024,
                    "price": 45000,
                    "type": "Sedán",
                    "fuel": "Gasolina",
                    "transmission": "Automática",
                    "features": ["Asientos de cuero", "Sistema premium", "Faros LED"],
                    "similarity_score": 75.0,
                    "image": None
                },
                {
                    "id": "sample_4",
                    "name": "Tesla Model Y 2024",
                    "model": "Model Y",
                    "brand": "Tesla",
                    "year": 2024,
                    "price": 48000,
                    "type": "SUV",
                    "fuel": "Eléctrico",
                    "transmission": "Automática",
                    "features": ["Piloto automático", "Techo panorámico", "Supercargador"],
                    "similarity_score": 70.0,
                    "image": None
                },
                {
                    "id": "sample_5",
                    "name": "Ford F-150 2024",
                    "model": "F-150",
                    "brand": "Ford",
                    "year": 2024,
                    "price": 45000,
                    "type": "Pickup",
                    "fuel": "Gasolina",
                    "transmission": "Automática",
                    "features": ["Tracción 4x4", "Caja de aluminio", "Remolque"],
                    "similarity_score": 68.0,
                    "image": None
                },
                {
                    "id": "sample_6",
                    "name": "Audi A4 2024",
                    "model": "A4",
                    "brand": "Audi",
                    "year": 2024,
                    "price": 42000,
                    "type": "Sedán",
                    "fuel": "Gasolina",
                    "transmission": "Automática",
                    "features": ["Quattro AWD", "Virtual cockpit", "Premium sound"],
                    "similarity_score": 65.0,
                    "image": None
                },
                {
                    "id": "sample_7",
                    "name": "Nissan Rogue 2024",
                    "model": "Rogue",
                    "brand": "Nissan",
                    "year": 2024,
                    "price": 35000,
                    "type": "SUV",
                    "fuel": "Gasolina",
                    "transmission": "Automática",
                    "features": ["ProPILOT Assist", "Bose audio", "Panoramic roof"],
                    "similarity_score": 62.0,
                    "image": None
                },
                {
                    "id": "sample_8",
                    "name": "Hyundai Sonata 2024",
                    "model": "Sonata",
                    "brand": "Hyundai",
                    "year": 2024,
                    "price": 28000,
                    "type": "Sedán",
                    "fuel": "Híbrido",
                    "transmission": "Automática",
                    "features": ["Digital key", "Wireless charging", "SmartSense"],
                    "similarity_score": 60.0,
                    "image": None
                }
            ]
            return jsonify(sample_recommendations)
        
        print("🔍 Llamando a get_recommendations...")
        print(f"  Parámetros enviados:")
        print(f"    brands={brands}")
        print(f"    budget={budget}")
        print(f"    fuel={fuel}")
        print(f"    types={types}")
        print(f"    transmission={transmission}")
        
        # Usar el sistema de recomendaciones real
        result = get_recommendations(brands, budget, fuel, types, transmission)
        
        print(f"📋 Resultado recibido:")
        print(f"  Tipo: {type(result)}")
        print(f"  Cantidad: {len(result) if isinstance(result, list) else 'N/A'}")
        if result and isinstance(result, list):
            print(f"  Primer elemento: {result[0].get('name', 'Sin nombre') if result[0] else 'Vacío'}")
        
        # Asegurar que el resultado sea una lista
        if not isinstance(result, list):
            print(f"⚠️ get_recommendations devolvió {type(result)}, esperaba lista")
            return jsonify([])
        
        print(f"🎉 ÉXITO: Devolviendo {len(result)} recomendaciones")
        print("="*60)
        
        return jsonify(result)
        
    except Exception as e:
        # Log completo del error
        error_traceback = traceback.format_exc()
        print(f"💥 ERROR en api_recommendations:")
        print(error_traceback)
        
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}",
            "details": "Revisa la consola del servidor para más información"
        }), 500

# Endpoint adicional para debug
@app.route("/api/debug/session", methods=["GET"])
def debug_session():
    session_data = dict(session)
    debug_info = {
        "session_data": session_data,
        "session_keys": list(session_data.keys()),
        "recommender_available": RECOMMENDER_AVAILABLE,
        "all_present": all([
            session.get('selected_brands'),
            session.get('selected_budget'),
            session.get('selected_fuel'),
            session.get('selected_types'),
            session.get('selected_transmission')
        ])
    }
    print(f"🔍 Debug session solicitado: {debug_info}")
    return jsonify(debug_info)

# Endpoint para limpiar la sesión (útil para testing)
@app.route("/api/debug/clear-session", methods=["POST"])
def clear_session():
    session.clear()
    print("🧹 Sesión limpiada")
    return jsonify({"success": True, "message": "Sesión limpiada"})

# Endpoint para verificar estado del sistema
@app.route("/api/debug/system-status", methods=["GET"])
def system_status():
    status = {
        "flask": "✅ Funcionando",
        "recommender": "✅ Disponible" if RECOMMENDER_AVAILABLE else "❌ No disponible",
        "session_active": "✅ Activa" if session.get('logged_in') else "❌ No logueado"
    }
    
    if RECOMMENDER_AVAILABLE:
        try:
            # Probar una recomendación simple
            test_result = get_recommendations(brands=["Toyota"], budget="20000-50000")
            status["recommender_test"] = f"✅ Funcionando ({len(test_result)} resultados)"
        except Exception as e:
            status["recommender_test"] = f"❌ Error: {str(e)}"
    
    return jsonify(status)

@app.route("/logout")
def logout():
    username = session.get('username', 'Usuario')
    session.clear()
    print(f"👋 Usuario {username} cerró sesión")
    return redirect(url_for('login'))

# Manejador de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO APLICACIÓN FLASK")
    print("=" * 60)
    print(f"✅ Recommender disponible: {RECOMMENDER_AVAILABLE}")
    print("📋 Endpoints disponibles:")
    print("  🏠 GET  / -> index/login")
    print("  🏷️  GET  /brands -> selección de marcas")
    print("  💰 GET  /budget -> selección de presupuesto")
    print("  ⛽ GET  /fuel -> selección de combustible")
    print("  🚗 GET  /type -> selección de tipo")
    print("  ⚙️  GET  /transmission -> selección de transmisión")
    print("  🎯 GET  /recommendations -> página de recomendaciones")
    print("  📊 GET  /api/recommendations -> obtener recomendaciones JSON")
    print("  🔍 GET  /api/debug/session -> ver datos de sesión")
    print("  📈 GET  /api/debug/system-status -> estado del sistema")
    print("=" * 60)
    app.run(debug=True, port=5000)