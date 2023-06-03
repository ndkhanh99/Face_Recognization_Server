from flask import Blueprint
from flask import Flask, redirect, render_template, jsonify, url_for, request, flash, make_response, session
from flask_login import UserMixin, AnonymousUserMixin, login_manager, login_user, logout_user
import os, sys, random, uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from . import app
from . import db
from . import key
from . import UPLOAD_FOLDER
from .models import User, Student
from flask_cors import CORS, cross_origin
cors = CORS(app, resources={'/*': {'origins': '*'}})
auth_routes = Blueprint('auth_routes', __name__)

def token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        print(request.headers)
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        else:
            return token or (
             jsonify({'message': 'Token is missing !!'}), 401)
        try:
            data = jwt.decode(token, key, algorithms=['HS256'])
            current_user = User.query.filter_by(public_id=(data['public_id'])).first()
        except:
            return (jsonify({'message': 'Token is invalid !!'}),
             401)
            return f(current_user, *args, **kwargs)

    return decorated


@auth_routes.route('/user', methods=['POST'])
@token_required
def get_all_users(current_user):
    users = User.query.all()
    output = []
    for user in users:
        output.append({'public_id':user.public_id, 
         'name':user.name, 
         'email':user.email, 
         'current_user':current_user.student_code})

    return jsonify({'users': output})


@auth_routes.route('/login', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def login():
    print(request.form)
    auth = request.form
    if not (auth and auth.get('email') and auth.get('password')):
        return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm ="Login required !!"'})
        user = User.query.filter_by(email=(auth.get('email'))).first()
        if not user:
            return make_response('Could not verify', 401, {'WWW-Authenticate': 'Basic realm ="User does not exist !!"'})
        if check_password_hash(user.password, auth.get('password')):
            token = jwt.encode({'public_id':user.public_id, 
             'student_code':user.student_code, 
             'exp':datetime.utcnow() + timedelta(minutes=120)}, key)
            role = jwt.encode({'role':user.role, 
             'exp':datetime.utcnow() + timedelta(minutes=30)}, key)
            print(token)
            return make_response(jsonify({'token':token,  'role':user.role,  'name':user.name,  'email':user.email,  'role':user.role}), 201)
    return make_response('Could not verify', 403, {'WWW-Authenticate': 'Basic realm ="Wrong Password !!"'})


@auth_routes.route('/signup', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def signup():
    data = request.form
    print(data)
    name, student_code, email = data.get('name'), data.get('studentCode'), data.get('email')
    password = data.get('password')
    role = 'student'
    role_id = 2
    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(public_id=(str(uuid.uuid4())),
          email=email,
          name=name,
          student_code=student_code,
          teacher_code=None,
          password=(generate_password_hash(password)),
          role=role,
          role_id=role_id,
          status=1)
        db.session.add(user)
        db.session.commit()
        student = Student(name=name,
          student_code=student_code)
        db.session.add(student)
        db.session.commit()
        users = User.query.filter_by(email=email).first()
        print(users)
        output = {'public_id':user.public_id, 
         'name':user.name, 
         'studentCode':user.student_code}
        return make_response(jsonify(output))
    return make_response('1')