from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from calendar import monthrange

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///usuarios.db'
db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.String(200), nullable=False)

@app.route('/')
def inicio():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    user = Usuario.query.filter_by(username=username, password=password).first()
    if user:
        return redirect(url_for('calendar', username=username))
    else:
        return "Usuario o contraseña incorrectos. Volver a intentar"

@app.route('/olvido_contrasena')
def olvido_contrasena():
    return "Página en construcción"

@app.route('/olvido_usuario')
def olvido_usuario():
    return "Página en construcción"

@app.route('/registro')
def registro():
    return render_template('registro.html', registrado=False)

@app.route('/registro', methods=['POST'])
def do_registro():
    username = request.form['username']
    password = request.form['password']
    if not Usuario.query.filter_by(username=username).first():
        nuevo_usuario = Usuario(username=username, password=password)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('registro_exitoso'))
    else:
        return "El usuario ya existe. Intentar nuevamente"

@app.route('/registro_exitoso')
def registro_exitoso():
    return render_template('registro.html', registrado=True)

def do_registro():
    mensaje = "Registro exitoso. Inicia sesión"
    return render_template('registro.html', mensaje=mensaje)

@app.route('/calendar/<username>')
def calendar(username):
    now = datetime.now()
    month = now.month
    year = now.year
    first_day = now.replace(day=1)
    last_day = now.replace(day=monthrange(year, month)[1])
    days = (last_day - first_day).days + 1
    usuario = Usuario.query.filter_by(username=username).first()
    eventos = Evento.query.filter_by(usuario_id=usuario.id).all() if usuario else []

    first_week_day = first_day.weekday()

    return render_template('calendario.html', username=username, month=month, year=year, eventos=eventos, now=now, days=days, first_week_day=first_week_day)

@app.route('/agregar_evento', methods=['POST'])
def agregar_evento():
    username = request.form['username']
    fecha_str = request.form['fecha']
    descripcion = request.form['descripcion']
    fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    usuario = Usuario.query.filter_by(username=username).first()
    if usuario:
        nuevo_evento = Evento(usuario_id=usuario.id, fecha=fecha, descripcion=descripcion)
        db.session.add(nuevo_evento)
        db.session.commit()
        return redirect(url_for('calendar', username=username))

@app.route('/eliminar_evento/<int:evento_id>', methods=['POST'])
def eliminar_evento(evento_id):
    evento = Evento.query.get(evento_id)
    if evento:
        db.session.delete(evento)
        db.session.commit()
    return redirect(url_for('calendar', username=request.form['username']))

@app.route('/logout', methods=['POST'])
def logout():
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
