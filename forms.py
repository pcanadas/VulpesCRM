from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, FloatField, SelectField, DateField, DateTimeField
from wtforms.validators import DataRequired, Length, Optional
from datetime import datetime
import db

def get_choices(elemento):
    lista = []
    db_query = db.session.query(elemento).all()
    for item in db_query:
        tup = (item.id, item.nombre)
        lista.append(tup)
    return lista

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    surname = StringField('Apellido', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    password = PasswordField('Password', validators=[DataRequired(message='Este campo es obligatorio.')])
    email = StringField('Email', validators=[DataRequired(message='Este campo es obligatorio.')])
    is_admin = BooleanField('Administrador')
    submit = SubmitField('Registrar')

class NewOfferForm(FlaskForm):
    lista_empresas = []
    noferta = StringField('Número de Oferta', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=12)])
    fecha = DateTimeField('Fecha', format='%d/%m/%Y', default=datetime.today)
    id_empresa = SelectField('Empresa', choices=lista_empresas)
    cliente = StringField('Cliente', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    nombre = StringField('Nombre de contacto', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    ciudad = StringField('Ciudad', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    telefono = StringField('Teléfono', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    email = StringField('Correo Electrónico', validators=[DataRequired(message='Este campo es obligatorio.')])
    nombre_producto = StringField('Producto principal de la oferta', validators=[DataRequired(message='Este campo es obligatorio.')])
    marca = StringField('Marca', validators=[DataRequired(message='Este campo es obligatorio.')])
    importe = FloatField('Importe', validators=[DataRequired(message='Este campo es obligatorio.')])
    descuento = FloatField('Descuento', validators=[DataRequired(message='Este campo es obligatorio.')])
    fecha_demo = DateTimeField('Fecha DEMO', format='%d/%m/%Y', validators=(Optional(),))
    fecha_visita = DateTimeField('Fecha Visita', format='%d/%m/%Y', validators=(Optional(),))
    comentarios = StringField('Comentarios generales del pedido')
    fecha_compra = DateTimeField('Fecha compra prevista', format='%d/%m/%Y', validators=(Optional(),))
    resultado = SelectField('Resultado', choices=(" ","Perdido","Comprado"))
    fecha_resultado = DateTimeField('Fecha Resultado', format='%d/%m/%Y', validators=(Optional(),))
    probabilidad = SelectField('Probabilidad', choices=("10%", "25%", "50%", "75%", "90%"))
    via = SelectField('Proveniencia', choices=("Visita", "Leat Fabricante", "Web", "Campaña Emailing", "Llamada",
                                               "Cliente Contacta"))
    persona = StringField('Persona que realiza la oferta', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    grupo_marketing = SelectField('Grupo de interés para marketing', choices=(" ", "Alimentación", "Biotecnología",
                                                                              "Clínicos Laboratorios", "Dental",
                                                                              "Distribuidores", "Ensayos",
                                                                              "FarmaceuticasCRO", "Farmacias",
                                                                              "Generales", "Grupo1", "Grupo2", "IES",
                                                                              "Microdialisis", "Plantas", "Veterinarios"))
    submit = SubmitField('Guardar Oferta')


class NewClientForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    telefono = StringField('Teléfono', validators=[DataRequired(message='Este campo es obligatorio.'), Length(max=64)])
    email = StringField('Correo Electrónico', validators=[DataRequired(message='Este campo es obligatorio.')])
    comentarios = StringField('Comentarios')
    submit = SubmitField('Guardar Cliente')

class NewContactForm(FlaskForm):
    fecha_contacto = DateTimeField('Fecha de contacto', format='%d/%m/%Y', default=datetime.today, validators=[DataRequired()])
    modo = SelectField('Modo de contacto', choices=("Visita","Reunión Telemática","Llamada","Email"))
    comentarios_contacto = StringField('Comentarios')
    nueva_fecha = DateTimeField('Fecha próximo contacto', format='%d/%m/%Y', validators=[DataRequired()])
    submit = SubmitField('Guardar Contacto')
