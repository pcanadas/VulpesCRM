from sqlalchemy import Column, Integer, Boolean, String, Date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

import db

class User(db.Base, UserMixin):
    __tablename__ = "usuarios"
    __table_args__ = {'sqlite_autoincrement': True}  # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    surname = Column(String(80), nullable=False)
    email = Column(String(256), nullable=False)
    password = Column(String(128), nullable=False)
    is_admin = Column(Boolean, default=False)
    def __repr__(self):
        return f'<User {self.email}>'
    def set_password(self, password):
        self.password = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Empresa(db.Base):

    __tablename__ = "empresas"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False) # nullable hace que el campo nombre NO pueda estar vacío.

    def __repr__(self):
        return f'<Empresa {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Producto(db.Base):

    __tablename__ = "productos"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    nombre = Column(String(200), nullable=False) # nullable hace que el campo nombre NO pueda estar vacío.
    id_oferta = Column(Integer, nullable=False)
    principal = Column(Boolean, default=False)

    def __repr__(self):
        return f'<Producto {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Oferta(db.Base):

    __tablename__ = "ofertas"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    id_empresa = Column(Integer, nullable=False)
    fecha = Column(Date, nullable=False)
    noferta = Column(Integer, nullable=False) # Número de oferta
    cliente = Column(String(200), nullable=False)
    nombre = Column(String(200), nullable=False)  # Nombre de contacto con el cliente
    ciudad = Column(String(60), nullable=False)
    telefono = Column(Integer, nullable=False)
    email = Column(String(100), nullable=False)
    nombre_producto = Column(String(100), nullable=False)
    marca = Column(String(100), nullable=False)
    importe = Column(Integer)
    descuento = Column(Integer)
    fecha_demo = Column(Date)
    fecha_visita = Column(Date)
    comentarios = Column(String)
    fecha_compra = Column(Date)
    resultado = Column(String)
    fecha_resultado = Column(Date)
    probabilidad = Column(Integer)
    via = Column(String)
    persona = Column(String)
    grupo_marketing = Column(String)
    mes_year = Column(Integer)

    def __repr__(self):
        return f'<Oferta {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class Contacto(db.Base):

    __tablename__ = "contactos"
    __table_args__ = {'sqlite_autoincrement': True} # Autoincrementa la primary_key de la tabla.
    id = Column(Integer, primary_key=True)
    id_oferta = Column(Integer, nullable=False) # Número de oferta de la tabla 'ofertas', corresponde con Oferta.id
    fecha_contacto = Column(Date, nullable=False) # Fecha en la que se establece contacto con el cliente
    modo = Column(String(24), nullable=False) # Forma por la que se establece contacto con el cliente
    comentarios_contacto = Column(String(600))
    nueva_fecha = Column(Date, nullable=False) # Fecha en la que se volverá a contactar con el cliente

    def __repr__(self):
        return f'<Contacto {self.id}>'

    def save(self):
        if not self.id:
            db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise
