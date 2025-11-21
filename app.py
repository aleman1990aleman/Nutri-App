from flask import Flask, render_template, request, redirect, url_for, flash, session

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

@app.route("/tasa", methods=["GET", "POST"])
def tasa():
    tmb = None
    get_total = None

    if request.method == "POST":
        peso = float(request.form.get("peso"))
        altura = float(request.form.get("altura"))   
        edad = float(request.form.get("edad"))
        genero = request.form.get("genero")
        actividad = request.form.get("actividad")

        if genero == "Hombre":
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
        else:
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) - 161

        factores = {
            "seden": 1.2,
            "ligera": 1.375,
            "moderada": 1.55,
            "alta": 1.725,
        }

        get_total = tmb * factores.get(actividad, 1)

        tmb = round(tmb, 2)
        get_total = round(get_total, 2)

    return render_template("calculartmb.html", tmb=tmb, get_total=get_total)


@app.route("/imc", methods=["GET", "POST"])
def imc():
    imc = None
    categoria = None

    if request.method == "POST":
        peso = float(request.form.get("peso"))
        altura = float(request.form.get("altura")) / 100  

        imc_valor = peso / (altura ** 2)
        imc = round(imc_valor, 2)

        if imc < 18.5:
            categoria = "Bajo peso"
        elif imc < 25:
            categoria = "Peso normal"
        elif imc < 30:
            categoria = "Sobrepeso"
        elif imc < 35:
            categoria = "Obesidad grado I"
        elif imc < 40:
            categoria = "Obesidad grado II"
        else:
            categoria = "Obesidad grado III (mórbida)"

    return render_template("calcuimc.html", imc=imc, categoria=categoria)

@app.route("/pesoideal", methods=["GET", "POST"])
def pesoideal():
    resultado = None

    if request.method == "POST":
        altura = float(request.form.get("altura"))  
        genero = request.form.get("genero")

        altura_pulg = altura / 2.54  

        if genero == "Hombre":
            resultado = 50 + 2.3 * (altura_pulg - 60)
        else:
            resultado = 45.5 + 2.3 * (altura_pulg - 60)

        resultado = round(resultado, 2)

    return render_template("pesoideal.html", resultado=resultado)


@app.route("/macros", methods=["GET", "POST"])
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

if __name__ == '__main__':
    app.run(debug=True)