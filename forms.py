from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, SelectMultipleField, RadioField, SubmitField
from wtforms.validators import DataRequired

from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class PedidoForm(FlaskForm):
    nombre = StringField("Nombre", validators=[DataRequired()])
    direccion = StringField("Dirección", validators=[DataRequired()])
    telefono = StringField("Teléfono", validators=[DataRequired()])
    fecha = DateField("Fecha", format="%Y-%m-%d", validators=[DataRequired()])

class PizzaForm(FlaskForm):
    tamano = SelectField("Tamaño", choices=[("Chica", "Chica"), ("Mediana", "Mediana"), ("Grande", "Grande")], validators=[DataRequired()])
    ingredientes = SelectMultipleField("Ingredientes", choices=[("Jamon", "Jamón"), ("Piña", "Piña"), ("Champiñones", "Champiñones")])
    cantidad = IntegerField("Número de Pizzas", validators=[DataRequired()])

class ReporteForm(FlaskForm):
    filtro = RadioField('Filtrar por', choices=[('dia', 'Día'), ('mes', 'Mes')], validators=[DataRequired()])
    fecha = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Generar Reporte')



class LoginForm(FlaskForm):
    username = StringField("Nombre de Usuario", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Iniciar Sesión")

class RegistroForm(FlaskForm):
    username = StringField("Nombre de Usuario", validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField("Contraseña", validators=[DataRequired()])
    submit = SubmitField("Registrarse")