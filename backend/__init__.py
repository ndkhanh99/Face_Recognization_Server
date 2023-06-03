from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from flask_marshmallow import Marshmallow
from flask_login import UserMixin, AnonymousUserMixin, login_manager
import os
from flask_cors import CORS
marsh = Marshmallow()
db = SQLAlchemy()
key = '$2y$10$HOP85MUzr39.uJcQoGyMOerF0yXU1RuWyYoUcqINGR4A0FILFLSDC'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static', 'Data', 'raw')
app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app, origins='*')
vuejs_config = {'origins':[
  'http://localhost:8080'], 
 'methods':[
  'OPTIONS', 'GET', 'POST'], 
 'allow_headers':[
  'Authorization']}
app.config['SECRET_KEY'] = key
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:duykhanh12345@localhost/attendancesystest'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CORS_HEADERS'] = 'Content-Type'
db.init_app(app)
marsh.init_app(app)

def create_app():
    CORS(app, resources={'/*': {'origins': '*'}})
    from .routes import routes
    app.register_blueprint(routes, url_prefix='/')
    from .admin_routes import admin_routes
    app.register_blueprint(admin_routes, url_prefix='/admin')
    from .attendance_routes import attendance_routes
    app.register_blueprint(attendance_routes, url_prefix='/attendance')
    from .auth_routes import auth_routes
    app.register_blueprint(auth_routes, url_prefix='/auth')
    from .detect_routes import detect_routes
    app.register_blueprint(detect_routes, url_prefix='/detect')
    from .stream_routes import stream_routes
    app.register_blueprint(stream_routes, url_prefix ='/stream')
    from .subject_routes import subject_routes
    app.register_blueprint(subject_routes, url_prefix='/subject')
    from .training_routes import training_routes
    app.register_blueprint(training_routes, url_prefix='/training')
    from .models import User, Role, userSchema, roleSchema
    connect_database(app)
    return app


def connect_database(app):
    with app.app_context():
        db.create_all()
    print('created database sucessfully!')


def add_column(engine, table_name, created):
    column_name = created.compile(dialect=(engine.dialect))
    column_type = created.type.compile(engine.dialect)
    engine.execute('ALTER TABLE %s ADD COLUMN %s %s' % (table_name, column_name, column_type))
    print('add new column' + table_name + 'successfully')