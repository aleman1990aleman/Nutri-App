from flask import Flask, render_template, request, redirect, url_for, flash, session
import requests

app = Flask(__name__)
app.secret_key = "1234567890"  
USUARIOS_REGISTRADOS = {}


@app.route('/')
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

@app.route('/macros', methods=['GET', 'POST'])
def macros():
    proteinas = grasas = carbohidratos = None

    if request.method == "POST":
        calorias = float(request.form.get("calorias"))

        proteinas = round((calorias * 0.30) / 4, 1)
        grasas = round((calorias * 0.25) / 9, 1)
        carbohidratos = round((calorias * 0.45) / 4, 1)

    return render_template(
        "macros.html",
        proteinas=proteinas,
        grasas=grasas,
        carbohidratos=carbohidratos
    )

@app.route('/imc', methods=['GET', 'POST'])
def imc():
    resultado = None
    categoria = None

    if request.method == 'POST':
        peso = float(request.form.get("peso"))
        altura_cm = float(request.form.get("altura"))   
        altura_m = altura_cm / 100                      

        resultado = round(peso / (altura_m ** 2), 2)

        if resultado < 18.5:
            categoria = "Bajo peso"
        elif resultado < 25:
            categoria = "Normal"
        elif resultado < 30:
            categoria = "Sobrepeso"
        else:
            categoria = "Obesidad"

    return render_template("calcuimc.html", resultado=resultado, categoria=categoria)


@app.route('/tbm', methods=['GET', 'POST'])
def tbm():
    resultado = None

    if request.method == 'POST':
        sexo = request.form.get("sexo")
        peso = float(request.form.get("peso"))
        altura_cm = float(request.form.get("altura"))   
        edad = int(request.form.get("edad"))

        if sexo == "hombre":
            resultado = 10 * peso + 6.25 * altura_cm - 5 * edad + 5
        else:
            resultado = 10 * peso + 6.25 * altura_cm - 5 * edad - 161

        resultado = round(resultado, 2)

    return render_template("calculartmb.html", resultado=resultado)


@app.route('/gct', methods=['GET', 'POST'])
def gct():
    resultado = None

    if request.method == 'POST':
        sexo = request.form.get("sexo")
        peso = float(request.form.get("peso"))
        altura_cm = float(request.form.get("altura"))  
        edad = int(request.form.get("edad"))
        actividad = request.form.get("actividad")

        if sexo == "hombre":
            tbm = 10 * peso + 6.25 * altura_cm - 5 * edad + 5
        else:
            tbm = 10 * peso + 6.25 * altura_cm - 5 * edad - 161

        factores = {
            "sedentario": 1.2,
            "ligero": 1.375,
            "moderado": 1.55,
            "alto": 1.725,
            "extremo": 1.9
        }

        resultado = round(tbm * factores.get(actividad, 1.2), 2)

    return render_template("calculadora_gct.html", resultado=resultado)


@app.route('/pci', methods=['GET', 'POST'])
def pci():
    resultado = None

    if request.method == 'POST':
        sexo = request.form.get("sexo")
        altura_cm = float(request.form.get("altura")) 

        if sexo == "hombre":
            resultado = 50 + 0.91 * (altura_cm - 152.4)
        else:
            resultado = 45.5 + 0.91 * (altura_cm - 152.4)

        resultado = round(resultado, 2)

    return render_template("pesoideal.html", resultado=resultado)



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