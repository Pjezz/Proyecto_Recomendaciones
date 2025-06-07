from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
import traceback
import hashlib
import json
from datetime import datetime

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

# Simulación de base de datos de usuarios (en producción usar Neo4j)
USERS_DB = {}
USER_PROFILES = {}
USER_FAVORITES = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        
        # Validaciones básicas
        if not email or not password:
            return jsonify({"success": False, "message": "Email y contraseña son requeridos"})
        
        if len(password) < 6:
            return jsonify({"success": False, "message": "La contraseña debe tener al menos 6 caracteres"})
        
        if email in USERS_DB:
            return jsonify({"success": False, "message": "El usuario ya existe"})
        
        # Crear usuario
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        USERS_DB[email] = {
            "password": password_hash,
            "created_at": datetime.now().isoformat()
        }
        
        # Inicializar perfil y favoritos
        USER_PROFILES[email] = {}
        USER_FAVORITES[email] = []
        
        session['logged_in'] = True
        session['user_email'] = email
        print(f"✅ Usuario registrado: {email}")
        
        return jsonify({"success": True, "redirect": url_for("profile_setup")})
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        email = data.get("username")  # Puede ser email o username
        password = data.get("password")
        
        # Para demo, aceptar cualquier usuario/contraseña
        if email and password:
            # Verificar si existe en BD
            if email in USERS_DB:
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if USERS_DB[email]["password"] == password_hash:
                    session['logged_in'] = True
                    session['user_email'] = email
                    print(f"✅ Usuario logueado: {email}")
                    
                    # Verificar si tiene perfil configurado
                    if email in USER_PROFILES and USER_PROFILES[email].get('displayName'):
                        return jsonify({"success": True, "redirect": url_for("brands")})
                    else:
                        return jsonify({"success": True, "redirect": url_for("profile_setup")})
                else:
                    return jsonify({"success": False, "message": "Contraseña incorrecta"})
            else:
                # Para demo, crear usuario automáticamente
                if len(password) >= 6:
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    USERS_DB[email] = {
                        "password": password_hash,
                        "created_at": datetime.now().isoformat()
                    }
                    USER_PROFILES[email] = {}
                    USER_FAVORITES[email] = []
                    
                    session['logged_in'] = True
                    session['user_email'] = email
                    print(f"✅ Usuario creado y logueado: {email}")
                    return jsonify({"success": True, "redirect": url_for("profile_setup")})
                else:
                    return jsonify({"success": False, "message": "La contraseña debe tener al menos 6 caracteres"})
        else:
            return jsonify({"success": False, "message": "Email y contraseña son requeridos"})
    
    return render_template("login.html")

@app.route("/profile-setup")
def profile_setup():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template("profile_setup.html")

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

# ===== API ENDPOINTS PARA USUARIO =====

@app.route("/api/save-profile", methods=["POST"])
def save_profile():
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        user_email = session.get('user_email')
        
        profile_data = {
            'displayName': data.get('displayName'),
            'gender': data.get('gender'),
            'ageRange': data.get('ageRange'),
            'updated_at': datetime.now().isoformat()
        }
        
        USER_PROFILES[user_email] = profile_data
        session['user_profile'] = profile_data
        
        print(f"👤 Perfil guardado para {user_email}: {profile_data}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error guardando perfil: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/user-info", methods=["GET"])
def user_info():
    if not session.get('logged_in'):
        return jsonify({"error": "No autenticado"}), 401
    
    user_email = session.get('user_email')
    profile = USER_PROFILES.get(user_email, {})
    
    return jsonify({
        "email": user_email,
        "username": user_email.split('@')[0],
        "displayName": profile.get('displayName'),
        "gender": profile.get('gender'),
        "ageRange": profile.get('ageRange')
    })

@app.route("/api/user-profile", methods=["GET"])
def user_profile():
    if not session.get('logged_in'):
        return jsonify({"error": "No autenticado"}), 401
    
    user_email = session.get('user_email')
    profile = USER_PROFILES.get(user_email, {})
    user_data = USERS_DB.get(user_email, {})
    
    return jsonify({
        "email": user_email,
        "displayName": profile.get('displayName'),
        "gender": profile.get('gender'),
        "ageRange": profile.get('ageRange'),
        "createdAt": user_data.get('created_at')
    })

@app.route("/api/user-favorites", methods=["GET"])
def user_favorites():
    if not session.get('logged_in'):
        return jsonify({"error": "No autenticado"}), 401
    
    user_email = session.get('user_email')
    favorites = USER_FAVORITES.get(user_email, [])
    
    return jsonify({"favorites": favorites})

@app.route("/api/add-favorite", methods=["POST"])
def add_favorite():
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        user_email = session.get('user_email')
        car_data = data.get('car')
        
        if user_email not in USER_FAVORITES:
            USER_FAVORITES[user_email] = []
        
        # Verificar si ya está en favoritos
        existing = next((f for f in USER_FAVORITES[user_email] if f.get('id') == car_data.get('id')), None)
        if existing:
            return jsonify({"success": False, "message": "Ya está en favoritos"})
        
        USER_FAVORITES[user_email].append(car_data)
        print(f"❤️ Favorito agregado para {user_email}: {car_data.get('name')}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error agregando favorito: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/remove-favorite", methods=["POST"])
def remove_favorite():
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        user_email = session.get('user_email')
        car_id = data.get('carId')
        
        if user_email in USER_FAVORITES:
            USER_FAVORITES[user_email] = [f for f in USER_FAVORITES[user_email] if f.get('id') != car_id]
            print(f"💔 Favorito eliminado para {user_email}: {car_id}")
        
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Error eliminando favorito: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/save-theme", methods=["POST"])
def save_theme():
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    try:
        data = request.get_json()
        theme = data.get('theme')
        user_email = session.get('user_email')
        
        if user_email not in USER_PROFILES:
            USER_PROFILES[user_email] = {}
        
        USER_PROFILES[user_email]['theme'] = theme
        print(f"🎨 Tema guardado para {user_email}: {theme}")
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/user-theme", methods=["GET"])
def user_theme():
    if not session.get('logged_in'):
        return jsonify({"theme": "light"})
    
    user_email = session.get('user_email')
    profile = USER_PROFILES.get(user_email, {})
    
    return jsonify({"theme": profile.get('theme', 'light')})

# ===== API ENDPOINTS EXISTENTES =====

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
        print("🎯 API RECOMMENDATIONS - INICIANDO (FILTRADOS + RECOMENDACIONES)")
        print("="*60)
        
        # Obtener datos de la sesión
        brands = session.get('selected_brands')
        budget = session.get('selected_budget')
        fuel = session.get('selected_fuel')
        types = session.get('selected_types')
        transmission = session.get('selected_transmission')
        user_email = session.get('user_email')
        
        # Debug detallado
        print("📊 DATOS DE SESIÓN:")
        print(f"  🏷️  Brands: {brands} (tipo: {type(brands)})")
        print(f"  💰 Budget: {budget} (tipo: {type(budget)})")
        print(f"  ⛽ Fuel: {fuel} (tipo: {type(fuel)})")
        print(f"  🚗 Types: {types} (tipo: {type(types)})")
        print(f"  ⚙️  Transmission: {transmission} (tipo: {type(transmission)})")
        print(f"  👤 Usuario: {user_email}")
        
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
        
        # Obtener perfil del usuario para personalización
        user_profile = USER_PROFILES.get(user_email, {})
        gender = user_profile.get('gender')
        age_range = user_profile.get('ageRange')
        
        print(f"👤 PERFIL DE USUARIO:")
        print(f"  Género: {gender}")
        print(f"  Edad: {age_range}")
        
        # Obtener recomendaciones completas
        if not RECOMMENDER_AVAILABLE:
            print("⚠️ RECOMMENDER NO DISPONIBLE - Usando datos de ejemplo")
            all_recommendations = get_sample_recommendations()
        else:
            print("🔍 Llamando a get_recommendations...")
            all_recommendations = get_recommendations(brands, budget, fuel, types, transmission, gender, age_range)
            
            print(f"📋 Resultado recibido:")
            print(f"  Tipo: {type(all_recommendations)}")
            print(f"  Cantidad: {len(all_recommendations) if isinstance(all_recommendations, list) else 'N/A'}")
            
            if not isinstance(all_recommendations, list):
                print(f"⚠️ get_recommendations devolvió {type(all_recommendations)}, esperaba lista")
                all_recommendations = get_sample_recommendations()
        
        # Aplicar personalización demográfica adicional si no se hizo en recommender
        if gender and age_range and not any('demographic_bonus' in car for car in all_recommendations):
            all_recommendations = apply_demographic_scoring(all_recommendations, gender, age_range)
            print(f"🎯 Personalización adicional aplicada por género: {gender}, edad: {age_range}")
        
        # Los resultados ya vienen separados del recommender_minimal.py
        # Solo necesitamos verificar que tengan el campo match_type
        for car in all_recommendations:
            if 'match_type' not in car:
                # Si no tiene match_type, asignar basado en score
                if car.get('similarity_score', 0) >= 85:
                    car['match_type'] = 'filtered'
                else:
                    car['match_type'] = 'recommended'
        
        # Contar por tipo
        filtered_count = len([car for car in all_recommendations if car.get('match_type') == 'filtered'])
        recommended_count = len([car for car in all_recommendations if car.get('match_type') == 'recommended'])
        
        print(f"📊 RESULTADOS PROCESADOS:")
        print(f"  🔍 Filtrados exactos: {filtered_count}")
        print(f"  🎯 Recomendaciones inteligentes: {recommended_count}")
        
        print(f"🎉 ÉXITO: Devolviendo {len(all_recommendations)} resultados totales")
        print("="*60)
        
        return jsonify(all_recommendations)
        
    except Exception as e:
        # Log completo del error
        error_traceback = traceback.format_exc()
        print(f"💥 ERROR en api_recommendations:")
        print(error_traceback)
        
        return jsonify({
            "error": f"Error interno del servidor: {str(e)}",
            "details": "Revisa la consola del servidor para más información"
        }), 500

def get_sample_recommendations():
    """Obtener recomendaciones de ejemplo con separación de tipos"""
    sample_data = [
        # Resultados filtrados (score alto, coincidencia exacta)
        {
            "id": "sample_filtered_1",
            "name": "Toyota Corolla 2024",
            "model": "Corolla",
            "brand": "Toyota",
            "year": 2024,
            "price": 25000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Aire acondicionado", "Radio AM/FM", "Bluetooth", "Cámara trasera", "Seguridad Toyota Safety"],
            "similarity_score": 92.0,
            "match_type": "filtered",
            "image": None
        },
        {
            "id": "sample_filtered_2",
            "name": "Honda CR-V 2024",
            "model": "CR-V",
            "brand": "Honda",
            "year": 2024,
            "price": 35000,
            "type": "SUV",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Espacio familiar", "Asientos cómodos", "Honda Sensing", "Amplio maletero"],
            "similarity_score": 90.0,
            "match_type": "filtered",
            "image": None
        },
        {
            "id": "sample_filtered_3",
            "name": "Mazda CX-5 2024",
            "model": "CX-5",
            "brand": "Mazda",
            "year": 2024,
            "price": 32000,
            "type": "SUV",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Diseño premium", "Tecnología i-ACTIVSENSE", "Interior espacioso"],
            "similarity_score": 88.0,
            "match_type": "filtered",
            "image": None
        },
        
        # Recomendaciones inteligentes (score menor, sugerencias basadas en IA)
        {
            "id": "sample_recommended_1",
            "name": "BMW 3 Series 2024",
            "model": "3 Series",
            "brand": "BMW",
            "year": 2024,
            "price": 45000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Motor turbo", "Deportivo", "Asientos sport", "Performance premium"],
            "similarity_score": 78.0,
            "match_type": "recommended",
            "image": None
        },
        {
            "id": "sample_recommended_2",
            "name": "Tesla Model Y 2024",
            "model": "Model Y",
            "brand": "Tesla",
            "year": 2024,
            "price": 55000,
            "type": "SUV",
            "fuel": "Eléctrico",
            "transmission": "Automática",
            "features": ["Piloto automático", "Pantalla táctil", "Carga rápida", "Tecnología verde"],
            "similarity_score": 75.0,
            "match_type": "recommended",
            "image": None
        },
        {
            "id": "sample_recommended_3",
            "name": "Mercedes-Benz C-Class 2024",
            "model": "C-Class",
            "brand": "Mercedes-Benz",
            "year": 2024,
            "price": 48000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Lujo alemán", "Asientos de cuero premium", "Tecnología avanzada", "Confort superior"],
            "similarity_score": 72.0,
            "match_type": "recommended",
            "image": None
        },
        {
            "id": "sample_recommended_4",
            "name": "Ford Mustang GT 2024",
            "model": "Mustang GT",
            "brand": "Ford",
            "year": 2024,
            "price": 48000,
            "type": "Coupé",
            "fuel": "Gasolina",
            "transmission": "Manual",
            "features": ["Motor V8", "Deportivo", "Diseño icónico", "Performance sport"],
            "similarity_score": 70.0,
            "match_type": "recommended",
            "image": None
        },
        {
            "id": "sample_recommended_5",
            "name": "Audi A4 2024",
            "model": "A4",
            "brand": "Audi",
            "year": 2024,
            "price": 42000,
            "type": "Sedán",
            "fuel": "Gasolina",
            "transmission": "Automática",
            "features": ["Quattro AWD", "Virtual cockpit", "Premium sound"],
            "similarity_score": 68.0,
            "match_type": "recommended",
            "image": None
        }
    ]
    
    return sample_data

def apply_demographic_scoring(recommendations, gender, age_range):
    """Aplicar puntuación demográfica según género y edad"""
    
    # Definir grupos de edad
    age_group = get_age_group(age_range)
    
    for car in recommendations:
        demographic_bonus = 0
        car_type = car.get('type', '').lower()
        car_brand = car.get('brand', '').lower()
        car_name = car.get('name', '').lower()
        features_text = str(car.get('features', [])).lower()
        
        # Lógica para mujeres
        if gender == 'femenino':
            if age_group == 'young':  # 18-25: igual que hombres jóvenes
                if car_type in ['coupé', 'convertible'] or any(sport_word in car_name for sport_word in ['sport', 'gt', 'turbo', 'mustang', 'm3']):
                    demographic_bonus += 5
            elif age_group == 'reproductive':  # 26-45: preferencia familiar
                if car_type in ['suv']:
                    demographic_bonus += 15
                elif car_type == 'sedán' and any(family_word in features_text for family_word in ['familia', 'seguridad', 'espacio', 'asientos']):
                    demographic_bonus += 10
            elif age_group == 'mature':  # 46+: comfort y luxury
                if any(luxury_brand in car_brand for luxury_brand in ['mercedes', 'bmw', 'audi', 'lexus']):
                    demographic_bonus += 12
                if any(premium_word in features_text for premium_word in ['premium', 'lujo', 'cuero']):
                    demographic_bonus += 8
        
        # Lógica para hombres
        elif gender == 'masculino':
            if age_group == 'young':  # 18-25: deportivos
                if car_type in ['coupé', 'convertible'] or any(sport_word in car_name for sport_word in ['sport', 'gt', 'turbo', 'mustang', 'm3']):
                    demographic_bonus += 8
            elif age_group == 'mature':  # 46+: comfort y luxury
                if any(luxury_brand in car_brand for luxury_brand in ['mercedes', 'bmw', 'audi', 'lexus']):
                    demographic_bonus += 12
                if any(premium_word in features_text for premium_word in ['premium', 'lujo', 'cuero']):
                    demographic_bonus += 8
        
        # Para todos: bonificación por características de comfort en edad madura
        if age_group == 'mature':
            comfort_features = ['cuero', 'premium', 'lujo', 'confort']
            for feature in comfort_features:
                if feature in features_text:
                    demographic_bonus += 3
                    break
        
        # Aplicar bonificación
        if demographic_bonus > 0:
            original_score = car.get('similarity_score', 0)
            car['similarity_score'] = original_score + demographic_bonus
            car['demographic_bonus'] = demographic_bonus
    
    # Reordenar por puntuación actualizada
    recommendations.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
    
    return recommendations

def get_age_group(age_range):
    """Convertir rango de edad a grupo demográfico"""
    if age_range in ['18-25']:
        return 'young'
    elif age_range in ['26-35', '36-45']:
        return 'reproductive'
    elif age_range in ['46-55', '56+']:
        return 'mature'
    else:
        return 'unknown'

# Endpoints adicionales para debug
@app.route("/api/debug/session", methods=["GET"])
def debug_session():
    session_data = dict(session)
    debug_info = {
        "session_data": session_data,
        "session_keys": list(session_data.keys()),
        "recommender_available": RECOMMENDER_AVAILABLE,
        "users_count": len(USERS_DB),
        "profiles_count": len(USER_PROFILES),
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

@app.route("/api/debug/clear-session", methods=["POST"])
def clear_session():
    session.clear()
    print("🧹 Sesión limpiada")
    return jsonify({"success": True, "message": "Sesión limpiada"})

@app.route("/api/debug/system-status", methods=["GET"])
def system_status():
    status = {
        "flask": "✅ Funcionando",
        "recommender": "✅ Disponible" if RECOMMENDER_AVAILABLE else "❌ No disponible",
        "session_active": "✅ Activa" if session.get('logged_in') else "❌ No logueado",
        "users_count": len(USERS_DB),
        "profiles_count": len(USER_PROFILES),
        "favorites_count": sum(len(favs) for favs in USER_FAVORITES.values()),
        "demographic_features": "✅ Activas",
        "filtered_and_recommended_separation": "✅ Implementado"
    }
    
    if RECOMMENDER_AVAILABLE:
        try:
            # Probar una recomendación simple con personalización
            test_result = get_recommendations(
                brands=["Toyota"], 
                budget="20000-50000",
                fuel=["Gasolina"],
                types=["Sedán"],
                transmission=["Automática"],
                gender="femenino",
                age_range="26-35"
            )
            status["recommender_test"] = f"✅ Funcionando ({len(test_result)} resultados con personalización)"
        except Exception as e:
            status["recommender_test"] = f"❌ Error: {str(e)}"
    
    return jsonify(status)

@app.route("/logout")
def logout():
    user_email = session.get('user_email', 'Usuario')
    session.clear()
    print(f"👋 Usuario {user_email} cerró sesión")
    return redirect(url_for('login'))

# Manejadores de errores
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint no encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

@app.route("/api/debug/check-session", methods=["GET"])
def check_session():
    return jsonify({
        "session_data": dict(session),
        "selected_brands": session.get('selected_brands'),
        "selected_budget": session.get('selected_budget'),
        "selected_fuel": session.get('selected_fuel'),
        "selected_types": session.get('selected_types'),
        "selected_transmission": session.get('selected_transmission'),
        "user_email": session.get('user_email'),
        "logged_in": session.get('logged_in')
    })

@app.route("/api/clear-favorites", methods=["POST"])
def clear_favorites():
    if not session.get('logged_in'):
        return jsonify({"success": False, "error": "No autenticado"}), 401
    
    user_email = session.get('user_email')
    if user_email in USER_FAVORITES:
        USER_FAVORITES[user_email] = []
    
    return jsonify({"success": True})

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 INICIANDO APLICACIÓN FLASK CON FILTRADOS Y RECOMENDACIONES")
    print("=" * 60)
    print(f"✅ Recommender disponible: {RECOMMENDER_AVAILABLE}")
    print("📋 Endpoints principales:")
    print("  🏠 GET  / -> index/login")
    print("  📝 GET  /register -> registro de usuarios")
    print("  👤 GET  /profile-setup -> configuración inicial")
    print("  🏷️  GET  /brands -> selección de marcas")
    print("  💰 GET  /budget -> selección de presupuesto")
    print("  ⛽ GET  /fuel -> selección de combustible")
    print("  🚗 GET  /type -> selección de tipo")
    print("  ⚙️  GET  /transmission -> selección de transmisión")
    print("  🎯 GET  /recommendations -> página de recomendaciones")
    print("  📊 GET  /api/recommendations -> obtener recomendaciones JSON")
    print("  👤 POST /api/save-profile -> guardar perfil de usuario")
    print("  ❤️  POST /api/add-favorite -> agregar favorito")
    print("  🎨 POST /api/save-theme -> guardar tema preferido")
    print("  🔍 GET  /api/debug/system-status -> estado del sistema")
    print("\n🎯 FUNCIONALIDADES AVANZADAS:")
    print("  🔍 Resultados Filtrados: Coincidencias exactas con criterios (Score 85-100)")
    print("  🎯 Recomendaciones IA: Sugerencias inteligentes personalizadas (Score 50-84)")
    print("  👩 Mujeres jóvenes (18-25): Deportivos permitidos")
    print("  👩‍👧‍👦 Mujeres reproductivas (26-45): +15 SUVs, +10 sedanes familiares")
    print("  👨 Hombres jóvenes (18-25): +8 deportivos")
    print("  🧓 Personas maduras (46+): +12 marcas premium, +8 comfort")
    print("  📱 Interfaz moderna con separación clara de resultados")
    print("  ❤️  Sistema de favoritos integrado")
    print("  🎨 Notificaciones en tiempo real")
    print("=" * 60)
    app.run(debug=True, port=5000)