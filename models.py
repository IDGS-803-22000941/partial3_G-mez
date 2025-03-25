from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import UserMixin
from flask_bcrypt import generate_password_hash, check_password_hash


# Inicializar SQLAlchemy
db = SQLAlchemy()

# Modelo de Pedido
class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    total = db.Column(db.Float, nullable=False)

    # Relación con la tabla de Pizzas (un pedido tiene muchas pizzas)
    pizzas = db.relationship('Pizza', backref='pedido', cascade="all, delete-orphan")

    def __init__(self, nombre, direccion, telefono, fecha, total):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.fecha = fecha
        self.total = total

# Modelo de Pizza
class Pizza(db.Model):
    __tablename__ = 'pizzas'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id', ondelete="CASCADE"), nullable=False)
    tamano = db.Column(db.String(20), nullable=False)
    ingredientes = db.Column(db.String(200), nullable=False)  # Se guardarán como texto separado por comas
    cantidad = db.Column(db.Integer, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)

    def __init__(self, pedido_id, tamano, ingredientes, cantidad, subtotal):
        self.pedido_id = pedido_id
        self.tamano = tamano
        self.ingredientes = ingredientes
        self.cantidad = cantidad
        self.subtotal = subtotal



class Usuario(db.Model, UserMixin):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Genera el hash de la contraseña."""
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """Verifica la contraseña con el hash almacenado."""
        return check_password_hash(self.password_hash, password)