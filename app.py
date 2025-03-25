from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy.sql import func
from config import DevelopmentConfig
from models import db, Pedido, Pizza, Usuario
import forms
import os
import datetime

# Configuración de la aplicación Flask
app = Flask(__name__, template_folder="templates")
app.config.from_object(DevelopmentConfig)

# Protección CSRF
csrf = CSRFProtect(app)

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Inicializar SQLAlchemy
db.init_app(app)

# Obtener la ruta absoluta del directorio donde está app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_FILE = os.path.join(BASE_DIR, "pizzas.txt")  # Ruta absoluta

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# --- LOGIN Y REGISTRO ---
@app.route("/login", methods=["GET", "POST"])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Inicio de sesión exitoso", "success")
            return redirect(url_for("index"))
        flash("Usuario o contraseña incorrectos", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("login"))

@app.route("/registro", methods=["GET", "POST"])
def registro():
    form = forms.RegistroForm()
    if form.validate_on_submit():
        existing_user = Usuario.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash("El usuario ya existe", "danger")
        else:
            new_user = Usuario(username=form.username.data)
            new_user.set_password(form.password.data)
            db.session.add(new_user)
            db.session.commit()
            flash("Usuario registrado con éxito. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("login"))
    return render_template("registro.html", form=form)

# --- FUNCIONES PARA GUARDAR Y CARGAR PIZZAS ---
def guardar_pizzas_temporal(pizzas):
    try:
        with open(TEMP_FILE, "w", encoding="utf-8") as archivo:
            for pizza in pizzas:
                linea = f"{pizza['tamano']},{';'.join(pizza['ingredientes'])},{pizza['cantidad']},{pizza['subtotal']}\n"
                archivo.write(linea)
    except Exception as e:
        print(f" Error al guardar pizzas.txt: {e}")

def cargar_pizzas_temporal():
    pizzas = []
    if os.path.exists(TEMP_FILE):
        try:
            with open(TEMP_FILE, "r", encoding="utf-8") as archivo:
                lectura = archivo.readlines()
                for linea in lectura:
                    if linea.strip():
                        datos = linea.strip().split(",")
                        pizzas.append({
                            "tamano": datos[0],
                            "ingredientes": datos[1].split(";") if datos[1] else ["Sin ingredientes"],
                            "cantidad": int(datos[2]),
                            "subtotal": float(datos[3])
                        })
        except Exception as e:
            print(f" Error al leer pizzas.txt: {e}")
    return pizzas

# --- RUTAS PRINCIPALES ---
@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = forms.PedidoForm()
    form_reporte = forms.ReporteForm()
    pizzas = cargar_pizzas_temporal()
    
    # Obtener ventas del día
    ventas = Pedido.query.filter(func.date(Pedido.fecha) == func.current_date()).all()
    ventas_totales = sum(v.total for v in ventas)

    return render_template("index.html", form=form, form_reporte=form_reporte, pizzas=pizzas, ventas=ventas, ventas_totales=ventas_totales, usuario=current_user)

@app.route("/agregar_pizza", methods=["POST"])
@login_required
def agregar_pizza():
    pizzas = cargar_pizzas_temporal()
    tamano = request.form.get("tamano")
    ingredientes = request.form.getlist("ingredientes")
    cantidad = request.form.get("cantidad")

    if not tamano or not cantidad:
        flash("Debe seleccionar un tamaño y una cantidad válida.", "danger")
        return redirect(url_for("index"))

    try:
        cantidad = int(cantidad)
        if cantidad <= 0:
            raise ValueError
    except ValueError:
        flash("Cantidad inválida.", "danger")
        return redirect(url_for("index"))

    precios = {"Chica": 40, "Mediana": 80, "Grande": 120}
    subtotal = precios[tamano] * cantidad + len(ingredientes) * 10 * cantidad

    nueva_pizza = {
        "tamano": tamano,
        "ingredientes": ingredientes if ingredientes else ["Sin ingredientes"],
        "cantidad": cantidad,
        "subtotal": subtotal
    }

    pizzas.append(nueva_pizza)
    guardar_pizzas_temporal(pizzas)

    flash("Pizza agregada correctamente", "success")
    return redirect(url_for("index"))

@app.route("/quitar_pizza/<int:index>")
@login_required
def quitar_pizza(index):
    pizzas = cargar_pizzas_temporal()
    if 0 <= index < len(pizzas):
        pizzas.pop(index)
        guardar_pizzas_temporal(pizzas)
        flash("Pizza eliminada", "danger")
    return redirect(url_for("index"))

@app.route("/finalizar_pedido", methods=["POST"])
@login_required
def finalizar_pedido():
    pizzas = cargar_pizzas_temporal()

    if not pizzas:
        flash("Debe agregar al menos una pizza antes de finalizar el pedido.", "danger")
        return redirect(url_for("index"))

    nombre = request.form.get("nombre")
    direccion = request.form.get("direccion")
    telefono = request.form.get("telefono")
    fecha = datetime.datetime.now().date()

    if not nombre or not direccion or not telefono:
        flash("Todos los campos del cliente son obligatorios.", "danger")
        return redirect(url_for("index"))

    total = sum(p["subtotal"] for p in pizzas)

    nuevo_pedido = Pedido(nombre=nombre, direccion=direccion, telefono=telefono, fecha=fecha, total=total)
    db.session.add(nuevo_pedido)
    db.session.commit()

    for p in pizzas:
        nueva_pizza = Pizza(pedido_id=nuevo_pedido.id, tamano=p["tamano"], ingredientes=", ".join(p["ingredientes"]), cantidad=p["cantidad"], subtotal=p["subtotal"])
        db.session.add(nueva_pizza)

    db.session.commit()
    guardar_pizzas_temporal([])

    flash(f"Pedido registrado con éxito. Total: ${total:.2f}", "success")
    return redirect(url_for("index"))

@app.route("/reporte", methods=["POST"])
@login_required
def reporte():
    form_reporte = forms.ReporteForm()
    form = forms.PedidoForm()

    ventas = []
    ventas_totales = 0  

    if form_reporte.validate_on_submit():
        fecha = form_reporte.fecha.data
        if form_reporte.filtro.data == "dia":
            ventas = Pedido.query.filter(func.date(Pedido.fecha) == fecha).all()
        elif form_reporte.filtro.data == "mes":
            ventas = Pedido.query.filter(func.extract("month", Pedido.fecha) == fecha.month, func.extract("year", Pedido.fecha) == fecha.year).all()

    ventas_totales = sum(v.total for v in ventas)

    return render_template("index.html", form=form, form_reporte=form_reporte, ventas=ventas, ventas_totales=ventas_totales)

# --- INICIAR APLICACIÓN ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
