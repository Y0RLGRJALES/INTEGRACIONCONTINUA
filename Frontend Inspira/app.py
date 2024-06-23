from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inspira.db'
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Cambia esto por una clave secreta
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

class Frase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.String(255), nullable=False)
    autor = db.Column(db.String(80), nullable=False)

@app.route('/')
def hello():
    return "Bienvenido a Inspira!"

@app.route('/api/frases', methods=['GET'])
def obtener_frases():
    frases = Frase.query.all()
    return jsonify([{"id": f.id, "contenido": f.contenido, "autor": f.autor} for f in frases])

@app.route('/api/frase', methods=['POST'])
@jwt_required()
def crear_frase():
    datos = request.get_json()
    nueva_frase = Frase(contenido=datos['contenido'], autor=datos['autor'])
    db.session.add(nueva_frase)
    db.session.commit()
    return jsonify({"mensaje": "Frase creada!"}), 201

@app.route('/api/registro', methods=['POST'])
def registrar_usuario():
    datos = request.get_json()
    hashed_password = bcrypt.generate_password_hash(datos['password']).decode('utf-8')
    nuevo_usuario = Usuario(nombre=datos['nombre'], password=hashed_password)
    db.session.add(nuevo_usuario)
    db.session.commit()
    return jsonify({"mensaje": "Usuario registrado!"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    datos = request.get_json()
    usuario = Usuario.query.filter_by(nombre=datos['nombre']).first()
    if usuario and bcrypt.check_password_hash(usuario.password, datos['password']):
        access_token = create_access_token(identity={'nombre': usuario.nombre})
        return jsonify(access_token=access_token)
    return jsonify({"mensaje": "Credenciales incorrectas"}), 401

@app.route('/api/protegido', methods=['GET'])
@jwt_required()
def ruta_protegida():
    identidad = get_jwt_identity()
    return jsonify(logged_in_as=identidad), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

