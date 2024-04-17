from datetime import date

from sqlalchemy import func
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from werkzeug.urls import url_parse
from forms import SignupForm, LoginForm, NewOfferForm, get_choices, NewContactForm
import db
import json
from models import User, Producto, Empresa, Oferta, Contacto

# Creación objetos Flask
app = Flask(__name__) # En app se encuentra nuestro servidor web de Flask

# App.config:
app.config['SECRET_KEY'] = '(gK"&WCz/;1Tqq3P<bw8hf!0v{]",V0PF<k<E;n}gFniYE##$9:R|>Jv!Ki=w%7' # Clave random para formularios de Flask-WTF.

login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Ingrese en su cuenta para poder acceder al sistema.'
login_manager.login_message_category = 'info'

# Funciones:
@app.route('/')
def home():
    """ Función que lleva inicialmente a login_form.html """
    return redirect(url_for('login'))

@app.route('/login/', methods=['GET', 'POST']) # Página de ingreso en cuenta de usuario
def login():
    """ Función que lleva a index.html """
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    error = None
    if form.validate_on_submit():
        email = request.form.get('email')
        # Comprobamos que hay un usuario con ese email
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None and user.check_password(form.password.data): # Verificamos que la contraseña es correcta
            login_user(user, remember=form.remember_me.data) # Asignamos a login_user los datos verificados del formulario
            flash('Login correcto', 'success')

            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
        else:
            error = f'El nombre de usuario o contraseña no son correctos'
    return render_template('login_form.html', form=form, error=error)

@app.route('/logout') # Logout de usuario
@login_required
def logout():
    logout_user()
    flash("Ha salido de la aplicación, vuelva pronto!", 'success')
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).filter_by(id=user_id).first()

@login_manager.request_loader
def load_user(request):

    api_key = request.args.get('api_key')
    if api_key:
        user_load = User.query.filter_by(api_key=api_key).first()
        if user_load:
            return user_load

    return None

@login_manager.unauthorized_handler
def unauthorized():
    flash('No está autorizado a visitar esta página', 'error')
    return redirect(url_for('login'))

@app.route("/index/") # Página principal del programa
@login_required
def index():
    """ Función que lleva a index.html """
    # Consulta para saber el número de ofertas
    nofertas = db.session.query(Oferta).count()
    # Consulta para saber el número de ofertas ganadas
    comprado = db.session.query(Oferta).filter(Oferta.resultado == "Comprado").count()
    # Consulta para saber el porcentaje de éxito (comprados / cerrados)
    cerrados = nofertas - (db.session.query(Oferta).filter(Oferta.fecha_resultado == None).count())
    exito = round(((comprado * 100) / cerrados), 2)

    # Grafica offers -> Ofertas por meses
    offers = db.session.query(db.func.sum(Oferta.importe), (Oferta.mes_year)).group_by(Oferta.mes_year).order_by(
        Oferta.fecha).all()
    fechas = db.session.query(Oferta.mes_year).distinct().order_by(Oferta.fecha)
    offers_list = []
    fecha_list = []
    for registro, _ in offers:  # Generamos lista de datos para dashboard 'offers'
        offers_list.append(registro)
    for fecha in fechas:  # Generamos eje para dashboard 'offers'
        fecha_list.append(fecha[0])

    # Grafica ofertas_proveedor -> Ofertas por proveedor
    total = db.session.query(db.func.sum(Oferta.importe), (Oferta.marca)).group_by(Oferta.marca).\
         order_by(Oferta.marca).all()
    proveedores = db.session.query(Oferta.marca).distinct().order_by(Oferta.marca)

    total_list = []
    proveedores_list = []
    for registro, _ in total:  # Generamos lista de datos para dashboard 'ventas_proveedor'
         total_list.append(registro)
    for proveedor in proveedores:  # Generamos eje para dashboard 'ventas_proveedor'
         proveedores_list.append(proveedor[0])

    ofertas_abiertas = db.session.query(Oferta).filter(Oferta.fecha_resultado == None).order_by(Oferta.fecha.desc())
    abiertas = ofertas_abiertas.count()

    # Consulta para indicar el nombre de la empresa en vez de la id de la empresa
    empresaid = db.session.query(Oferta.id, Empresa.nombre).filter(Empresa.id == Oferta.id_empresa).all()
    # Consulta para indicar la nueva fecha de contacto
    nfecha = db.session.query(Contacto.id_oferta, func.max(Contacto.fecha_contacto)).group_by(Contacto.id_oferta)

    fecha = date.today()  # Asigna fecha actual
    lista_dias_desde_contacto = []
    lista_dias_hasta_contacto = []
    for oferta in ofertas_abiertas:
        ultimo_contacto = db.session.query(Contacto.fecha_contacto).filter(oferta.id == Contacto.id_oferta).order_by(
            Contacto.fecha_contacto.desc()).first()

        dias_desde_contacto = fecha - ultimo_contacto[0] # Resta las dos fechas
        resultado = str(dias_desde_contacto)
        if resultado != "0:00:00":
            dat = str(dias_desde_contacto).split(" ")
            dias_desde_contacto = (oferta.id, int(dat[0]))
        else:
            dias_desde_contacto = (oferta.id, 0)
        lista_dias_desde_contacto.append(dias_desde_contacto)

        proximo_contacto = db.session.query(Contacto.nueva_fecha).filter(oferta.id == Contacto.id_oferta).order_by(
            Contacto.fecha_contacto.desc()).first()

        dias_hasta_contacto = fecha - proximo_contacto[0]  # Resta las dos fechas
        resultado = str(dias_hasta_contacto)
        if resultado != "0:00:00":
            datos = str(dias_hasta_contacto).split(" ")
            dias_hasta_contacto = (oferta.id, int(datos[0]))
        else:
            dias_hasta_contacto = (oferta.id, 0)
        lista_dias_hasta_contacto.append(dias_hasta_contacto)


    return render_template("index.html", nofertas=nofertas, exito=exito, nfecha=nfecha, ofertas_abiertas=ofertas_abiertas,
                           lista_dias_hasta_contacto=lista_dias_hasta_contacto,
                           lista_dias_desde_contacto=lista_dias_desde_contacto,
                           empresaid=empresaid, dias_desde_contacto=dias_desde_contacto,
                           dias_hasta_contacto=dias_hasta_contacto, abiertas=abiertas, comprado=comprado,
                           offers_data=json.dumps(offers_list), fechas_data=json.dumps(fecha_list),
                           total_data=json.dumps(total_list), proveedores_data=json.dumps(proveedores_list)
                           )

@app.route("/signup/", methods=["GET", "POST"]) # Darse de alta como cliente
def show_signup_form():
    """ Función que lleva a signup_form.html """
    #if current_user.is_authenticated:
    #    return redirect(url_for('home'))
    form = SignupForm()
    error = None
    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = form.password.data
        # Comprobamos que no hay ya un usuario con ese email
        user = db.session.query(User).filter_by(email=email).first()
        if user is not None:
            error = f'El email {email} ya está siendo utilizado por otro usuario'
        else:
            # Creamos el usuario y lo guardamos
            user = User(name=name, surname=surname, email=email)
            user.set_password(password)
            user.save()
            flash('Usuario creado', 'success')
            # Dejamos al usuario logueado
            login_user(user, remember=True)
            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('home')
            return redirect(next_page)
    return render_template("signup_form.html", form=form, error=error)

@app.route("/crear-oferta", methods=['GET', 'POST']) # Alta de nueva oferta
@login_required
def crear_oferta():
    """ Función que lleva a new_offer.html """
    form = NewOfferForm()
    form2 = NewContactForm()
    error = None
    form.id_empresa.choices = get_choices(Empresa) #Establecemos los elementos del menú Empresas

    if form.validate_on_submit() and form2.validate_on_submit():
        noferta = form.noferta.data
        fecha = form.fecha.data
        id_empresa = form.id_empresa.data
        cliente = form.cliente.data
        nombre = form.nombre.data
        ciudad = form.ciudad.data
        telefono = form.telefono.data
        email = form.email.data
        nombre_producto = form.nombre_producto.data
        marca = form.marca.data
        importe = form.importe.data
        descuento = form.descuento.data
        fecha_demo = form.fecha_demo.data
        fecha_visita = form.fecha_visita.data
        comentarios = request.form['comentarios']
        fecha_compra = form.fecha_compra.data
        resultado = form.resultado.data
        fecha_resultado = form.fecha_resultado.data
        probabilidad = form.probabilidad.data
        via = form.via.data
        persona = form.persona.data
        grupo_marketing = form.grupo_marketing.data
        mes_year = fecha.strftime("%m/%Y")

        fecha_contacto = form2.fecha_contacto.data
        modo = form2.modo.data
        comentarios_contacto = form2.comentarios_contacto.data
        nueva_fecha = form2.nueva_fecha.data

        # Comprobamos que no hay ya una oferta con esa referencia
        oferta = db.session.query(Oferta).filter_by(noferta=noferta).first()
        if oferta is not None:
            error = f'La oferta con referencia {noferta} ya está introducido en el sistema'
        else:
            # Creamos la oferta y lo guardamos
            oferta = Oferta(id_empresa=id_empresa, fecha=fecha, noferta=noferta, cliente=cliente, nombre=nombre,
                            telefono=telefono, ciudad=ciudad, email=email, nombre_producto=nombre_producto,
                            marca=marca, importe=importe, descuento=descuento,
                            fecha_demo=fecha_demo, fecha_visita=fecha_visita, comentarios=comentarios,
                            fecha_compra=fecha_compra, resultado=resultado,
                            fecha_resultado=fecha_resultado, probabilidad=probabilidad, via=via, persona=persona,
                            grupo_marketing=grupo_marketing, mes_year=mes_year)
            oferta.save()
            flash('Oferta creada', 'success')

            id_oferta = oferta.id


            # Creamos el contacto y lo guardamos
            contacto = Contacto(id_oferta=id_oferta, fecha_contacto=fecha_contacto, modo=modo,
                                comentarios_contacto=comentarios_contacto, nueva_fecha=nueva_fecha)
            contacto.save()

            next_page = request.args.get('next', None)
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('historial')
            return redirect(next_page)
    return render_template("new_offer.html", form=form, form2=form2, error=error)

@app.route("/new_contact/<int:entrada_id>", methods=['GET', 'POST']) # Creación de nuevo contacto de seguimiento de oferta
@login_required
def new_contact(entrada_id):
    """ Función que lleva a new_contact.html """
    form = NewContactForm()
    contactos = db.session.query(Contacto).filter_by(id_oferta=entrada_id).all()

    if request.method == 'POST' and form.validate_on_submit():
        id_oferta = entrada_id
        fecha_contacto = form.fecha_contacto.data
        modo = form.modo.data
        comentarios_contacto = form.comentarios_contacto.data
        nueva_fecha = form.nueva_fecha.data

        # Creamos el contacto y lo guardamos
        contacto = Contacto(id_oferta=id_oferta, fecha_contacto=fecha_contacto, modo=modo,
                            comentarios_contacto=comentarios_contacto, nueva_fecha=nueva_fecha)
        contacto.save()
        flash('Contacto creado', 'success')
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('historial')
        return redirect(next_page)
    return render_template("new_contact.html", form=form, entrada_id=entrada_id, contactos=contactos)

@app.route("/historial") # Listado de ofertas
@login_required
def historial():
    """ Función que lleva a offer_history.html """
    entradas = db.session.query(Oferta).order_by(Oferta.fecha.asc()).all()
    print(type(entradas))
    for entrada in entradas:
        print(entrada)
    # Buscamos los últimos registros de contacto de la oferta
    registros = db.session.query(Contacto.id_oferta, func.max(Contacto.fecha_contacto), Contacto.modo).group_by(Contacto.id_oferta)
    # Consulta para indicar el nombre de la empresa en vez de la id de la empresa
    empresaid = db.session.query(Oferta.id, Empresa.nombre).filter(Empresa.id == Oferta.id_empresa).all()
    sortparams = {'sortby': 'column_name', 'sortdir': 'asc'}
    return render_template("offer_history.html", entradas=entradas, registros=registros, empresaid=empresaid, sortparams=sortparams)

@app.route("/usuarios") # Listado de usuarios
@login_required
def usuarios():
    """ Función que lleva a users.html """
    users = db.session.query(User).all()
    sortparams = {'sortby': 'column_name', 'sortdir': 'asc'}
    return render_template("users.html", users=users, sortparams=sortparams)

@app.route('/view/<int:entrada_id>', methods=['GET']) # Visualización de contactos
@login_required
def view_contact(entrada_id):
    """ Función que lleva a show_contact.html """
    form = NewContactForm()
    contactos = db.session.query(Contacto).filter_by(id_oferta=entrada_id).order_by(Contacto.fecha_contacto.desc()).all()
    for contacto in contactos:
        print(contacto)


    # Adjudicamos a una variable el nº de la oferta
    noferta = db.session.query(Oferta.noferta).filter_by(id=entrada_id).first()
    print(noferta)
    if noferta is None:
        noferta = 0000
    else:
        noferta = noferta[0]

    return render_template('show_contact.html', contactos=contactos, form=form, noferta=noferta, entrada_id=entrada_id)

@app.route('/viewu/<int:entrada_id>', methods=['GET']) # Visualización de usuario
@login_required
def view_user(entrada_id):
    """ Función que lleva a show_item.html """
    form = SignupForm()
    view_item = 'ver_cliente' # Variable para seleccionar que datos mostrar
    users = db.session.query(User).filter_by(id=entrada_id)
    return render_template('show_item.html', view_item=view_item, users=users, form=form)

@app.route("/edit/<int:entrada_id>", methods=['GET', 'POST']) # Edición de oferta
@login_required
def edit(entrada_id):
    """ Función que lleva a edit.html """
    form = NewOfferForm()
    edit_item = 'editar_oferta'  # Variable para seleccionar que datos mostrar
    form.id_empresa.choices = get_choices(Empresa)  # Establecemos los elementos del menú Empresas
    oferta = db.session.query(Oferta).filter_by(id=entrada_id).first()
    if request.method == 'POST' and form.validate_on_submit():
        oferta.id = request.form['id']
        # Modificamos los registros de la oferta y lo guardamos
        oferta.noferta = form.noferta.data
        oferta.fecha = form.fecha.data
        oferta.id_empresa = form.id_empresa.data
        oferta.cliente = form.cliente.data
        oferta.nombre = form.nombre.data
        oferta.ciudad = form.ciudad.data
        oferta.telefono = form.telefono.data
        oferta.email = form.email.data
        oferta.nombre_producto = form.nombre_producto.data
        oferta.marca = form.marca.data
        oferta.importe = form.importe.data
        oferta.descuento = form.descuento.data
        oferta.fecha_demo = form.fecha_demo.data
        oferta.fecha_visita = form.fecha_visita.data
        oferta.comentarios = form.comentarios.data
        oferta.fecha_compra = form.fecha_compra.data
        oferta.resultado = form.resultado.data
        oferta.fecha_resultado = form.fecha_resultado.data
        oferta.probabilidad = form.probabilidad.data
        oferta.via = form.via.data
        oferta.persona = form.persona.data
        oferta.grupo_marketing = form.grupo_marketing.data
        oferta.mes_year = form.fecha.data.strftime("%m/%Y")
        db.session.commit()
        flash('Oferta editada con éxito', 'success')
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('historial')
        return redirect(next_page)
    return render_template('edit.html', edit_item=edit_item, oferta=oferta, form=form, entrada_id=entrada_id)

@app.route('/editu/<int:entrada_id>', methods=['GET', 'POST']) # Edición de usuario
@login_required
def editu(entrada_id):
    """ Función que lleva a edit.html """
    form = SignupForm()
    edit_item = 'editar_usuario'  # Variable para seleccionar que datos mostrar
    users = db.session.query(User).filter_by(id=entrada_id).first()
    if request.method == 'POST' and form.validate_on_submit():
        users.id = request.form['id']
        # Modificamos los registros del usuario y lo guardamos
        users.name = form.name.data
        users.surname = form.surname.data
        users.email = form.email.data
        users.password = request.form['password']
        users.is_admin = form.is_admin.data
        db.session.commit()
        flash('Cliente editado con éxito', 'success')
        next_page = request.args.get('next', None)
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('usuarios')
        return redirect(next_page)
    return render_template('edit.html', edit_item=edit_item, users=users, form=form, entrada_id=entrada_id)

@app.route("/delete/<int:entrada_id>") # Borrar oferta
@login_required
def delete(entrada_id):
    """ Función que borra una oferta """
    oferta = db.session.query(Oferta).filter_by(id=entrada_id).first()
    contactos = db.session.query(Contacto).filter_by(id_oferta=oferta.id).all()

    db.session.delete(oferta)
    for contacto in contactos:
        db.session.delete(contacto)
    db.session.commit()
    flash('Oferta borrada con éxito', 'success')
    return redirect(url_for('historial'))

@app.route("/delete_contact/<int:entrada_id>") # Borrar contacto
@login_required
def delete_contact(entrada_id):
    """ Función que borra un contacto """
    contacto = db.session.query(Contacto).filter_by(id=entrada_id).first()

    db.session.delete(contacto)
    db.session.commit()
    flash('Contacto borrado con éxito', 'success')
    return redirect(url_for('view_contact', entrada_id=contacto.id_oferta))

@app.route("/dashboard/") # Página de informes
@login_required
def dashboard():
    """ Función que lleva a dashboard.html """
    # Consulta para saber el número de Ofertas
    numofertas = db.session.query(Oferta).count()
    # Consulta para saber el número de fabricantes
    numfabricantes = db.session.query(Oferta.marca).distinct().count()
    # Grafica offers -> Ofertas por meses
    offers = db.session.query(db.func.sum(Oferta.importe), (Oferta.mes_year)).group_by(Oferta.mes_year).order_by(
        Oferta.fecha).all()
    fechas = db.session.query(Oferta.mes_year).distinct().order_by(Oferta.fecha)
    offers_list = []
    fecha_list = []
    for registro, _ in offers: # Generamos lista de datos para dashboard 'offers'
        offers_list.append(registro)
    for fecha in fechas: #Generamos eje para dashboard 'offers'
        fecha_list.append(fecha[0])

    # Grafica num_ofertas -> Nº de ofertas cerradas por meses
    nofertas = db.session.query(db.func.sum(Oferta.importe), Oferta.mes_year).group_by(Oferta.mes_year).filter(
        Oferta.resultado=="Comprado").order_by(Oferta.fecha).all()
    oofertas_list = []
    fofertas_list = []
    nofertas_list = []

    for registro in nofertas:
        oofertas_list.append((registro[0], registro[1]))
    for fecha in fecha_list:
        for registro in oofertas_list:
            if registro[1] in fecha:
                fofertas_list.append(fecha)
    for registro, _ in nofertas:
        nofertas_list.append(registro)

    #lista = list(e for e in fecha_list if e not in fofertas_list)  # Código para insertar meses sin ofertas cerradas
    #print(lista)

    #for item in lista:
    #    nofertas_list.append((0, item))

    # Grafica Ofertas por Comercial -> Ofertas por Comercial
    ofertas_comercial = db.session.query(db.func.sum(Oferta.importe), (Oferta.persona)).group_by(Oferta.persona).order_by(Oferta.persona)
    comercial = db.session.query(Oferta.persona).distinct().order_by(Oferta.persona)
    ofertas_comercial_list = []
    comercial_list = []
    for oferta in ofertas_comercial:  # Generamos lista de datos para dashboard 'stock'
        ofertas_comercial_list.append(oferta[0])
    for item in comercial:  # Generamos eje para dashboard 'stock'
        comercial_list.append(item[0])


    # Grafica ofertas_proveedor -> Ofertas por proveedor
    total = db.session.query(db.func.sum(Oferta.importe), Oferta.marca).group_by(Oferta.marca).\
        order_by(Oferta.marca).all()
    proveedores = db.session.query(Oferta.marca).order_by(Oferta.marca).distinct()
    total_comprado = db.session.query(db.func.sum(Oferta.importe), Oferta.marca).filter(
        Oferta.resultado == "Comprado").group_by(Oferta.marca).order_by(Oferta.marca).all()
    total_list = []
    proveedores_list = []
    comprado_list = []
    for registro, _ in total:  # Generamos lista de datos para dashboard 'ventas_proveedor'
        total_list.append(registro)
    for proveedor in proveedores:  # Generamos eje para dashboard 'ventas_proveedor'
        proveedores_list.append(proveedor[0])
    for j in proveedores_list:
        comprado_list.append((j, 0))
    total_comprado_list = []
    for item in comprado_list:
        item = list(item)
        total_comprado_list.append(item)

    for item in total_comprado:  # Generamos eje para dashboard 'ventas_proveedor'
        for register in total_comprado_list:
            if register[0] == item[1]:
                dato = register[1] + item[0]
                register[1] = dato


    # Gráfica descuento_proveedor -> Descuento medio por proveedor
    dproveedor = db.session.query(Oferta.marca, Oferta.importe, Oferta.descuento).order_by(Oferta.marca).all()
    dproveedor_list = []

    for proveedor in proveedores:
        descuento = 0
        importes = 0
        ndescuento = 0
        for data in dproveedor:
            if data[0] == proveedor[0]:
                importes += data[1]
                descuento += data[2]
                if data[2]:
                    ndescuento += 1

        if ndescuento != 0:
            descuento = round(descuento / ndescuento, 2)
        dproveedor_list.append(descuento)

    #Porcentaje de ofertas por vía

    #Ofertas Abiertas / Cerradas por mes

    #Ofertas Ganadas / Perdidas

    return render_template("dashboard.html", offers_data=json.dumps(offers_list), fechas_data=json.dumps(fecha_list),
                           nofertas_data=json.dumps(nofertas_list), fofertas_data=json.dumps(fofertas_list),
                           ofertas_comercial_data=json.dumps(ofertas_comercial_list),
                           comercial_data=json.dumps(comercial_list), dproveedor_data=json.dumps(dproveedor_list),
                           total_data=json.dumps(total_list), proveedores_data=json.dumps(proveedores_list),
                           numofertas=numofertas, total_comprado_data=json.dumps(total_comprado_list),
                           numfabricantes=numfabricantes)

@app.errorhandler(401)
def status_401(error):
    return redirect(url_for('home'))

@app.errorhandler(404)
def status_404(error):
    return '<h1>Página no encontrada</h1>', 404

if __name__ == '__main__':
    # En la siguiente línea estamos indicando a SQLAlchemy que cree, si no existe, las tablas
    # de todos los modelos que encuentre en models.py
    db.Base.metadata.create_all(db.engine)
    app.register_error_handler(401, status_401)
    app.register_error_handler(404, status_404)
    app.run(debug=True) # El debug=True hace que cada vez que reiniciemos el servidor, o modifiquemos el código, el
    #servidor de Flask se reinicie solo. Es un modo de producción que nos va a dar más datos.
    #Debug=True es lo que habilita el depurador y analiza mejor cada línea de código en busca de errores.
    # Al terminar habrá que quitarlo.

