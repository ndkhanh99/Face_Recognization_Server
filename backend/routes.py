from crypt import methods
from flask import Blueprint
from flask import redirect, render_template, jsonify, url_for, request, flash, make_response, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os, sys, uuid
from datetime import datetime, timedelta
from . import db
from . import key
from . import UPLOAD_FOLDER
from .models import Role, User, userSchema, roleSchema
from .auth_routes import token_required
routes = Blueprint('routes', __name__)
users_sche = userSchema(many=True)
roles_sche = roleSchema(many=True)

@routes.route('/')
def index():
    return render_template('index.html')