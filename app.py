from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

app = Flask(__name__)
app.secret_key = "1234567890"  
USUARIOS_REGISTRADOS = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not email or not password:
            flash('Por favor ingresa email y contraseña', 'error')
            return redirect(url_for('login'))

        if email not in USUARIOS_REGISTRADOS:
            flash('El usuario no existe', 'error')
            return redirect(url_for('login'))

        usuario = USUARIOS_REGISTRADOS[email]

        if usuario['password'] != password:
            flash('Contraseña incorrecta', 'error')
            return redirect(url_for('login'))

        session['usuario_email'] = email
        session['usuario_nombre'] = usuario['nombre']
        session['logueado'] = True

        flash(f'Bienvenido {usuario["nombre"]}!', 'success')
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for('login'))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombres"]
        apellido = request.form["apellido"]
        fecha_nacimiento = request.form["fecha_nacimiento"]
        email = request.form["email"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        genero = request.form.get("genero")

        peso = request.form.get("peso")
        altura = request.form.get("altura")
        nivel_actividad = request.form.get("nivel_actividad")
        objetivo = request.form.get("objetivo")
        preferencias = request.form.get("preferencias")
        nivel_experiencia = request.form.get("nivel_experiencia")

        if password != confirm_password:
            flash("Las contraseñas no coinciden", "error")
            return render_template("registro.html")

        if email in USUARIOS_REGISTRADOS:
            flash("Este correo ya está registrado", "error")
            return render_template("registro.html")

        USUARIOS_REGISTRADOS[email] = {
            "nombre": nombre,
            "apellido": apellido,
            "fecha_nacimiento": fecha_nacimiento,
            "genero": genero,
            "peso": peso,
            "altura": altura,
            "nivel_actividad": nivel_actividad,
            "objetivo": objetivo,
            "preferencias": preferencias,
            "nivel_experiencia": nivel_experiencia,
            "password": password
        }

        flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
        return redirect(url_for("login"))

    return render_template("registro.html")

@app.route('/imc')
def imc():
    return render_template("imc.html")

@app.route('/tbm')
def tbm():
    return render_template("tbm.html")


@app.route('/gct')
def gct():
    return render_template("gct.html")

@app.route('/pci')
def pci():
    return render_template("pci.html")


@app.route('/busqueda')
def busqueda():
    return render_template("busqueda.html")

@app.route('/educacion')
def educacion():
    return render_template("educacion.html")

@app.route("/analizador_recetas", methods=["GET", "POST"])
def analizador_recetas():
    nutrientes = None

    if request.method == "POST":
        receta = request.form.get("receta")

        if not receta:
            flash("Por favor ingresa una receta.", "error")
            return render_template("analizador_recetas.html")

        API_KEY = "ao0tNQgF9iwaVSi3tV2ms7odgQ6e2D2Wl0q4bnmS"
        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={API_KEY}"

        payload = {
            "query": receta,
            "dataType": ["SR Legacy", "Foundation", "Branded"],
            "pageSize": 5
        }

        try:
            respuesta = requests.post(url, json=payload)
            data = respuesta.json()

            if "foods" not in data or len(data["foods"]) == 0:
                flash("No se encontraron nutrientes para esta receta.", "error")
            else:
                nutrientes = data["foods"][0].get("foodNutrients", [])
        except Exception as e:
            flash("Error al conectar con la API.", "error")
            print("Error:", e)

    return render_template("analizador_recetas.html", nutrientes=nutrientes)

if __name__ == "__main__":
    app.run(debug=True)