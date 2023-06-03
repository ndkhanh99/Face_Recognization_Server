from flask import Blueprint
from flask import Flask, jsonify, request, make_response, session
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from .auth_routes import token_required
from .models import User, Subject, Student, Student_to_subject, Teacher, Teacher_to_subject, Attendance
from . import db
from sqlalchemy import func
import random, uuid
from werkzeug.security import generate_password_hash, check_password_hash
admin_routes = Blueprint('admin_routes', __name__)

@admin_routes.route('/get-all', methods=['POST'])
@token_required
def get_all_users(current_user):
    if current_user.role_id == 1:
        student = Student.query.all()
        teacher = Teacher.query.all()
        subject = Subject.query.all()
        students = []
        for i in student:
            students.append({'id':i.id, 
             'name':i.name, 
             'student_code':i.student_code})

        teachers = []
        for itm in teacher:
            teachers.append({'id':itm.id, 
             'name':itm.name, 
             'teacher_code':itm.teacher_code})

        subjects = []
        for item in subject:
            subjects.append({'id':item.id, 
             'name':item.name, 
             'teacher':item.teacher, 
             'status':item.status})

    return jsonify({'subjects':subjects,  'teachers':teachers,  'students':students})


@admin_routes.route('/add-teacher', methods=['POST'])
@token_required
def add_teacher(current_user):
    if current_user.role_id == 1:
        print(request.json)
        user = User.query.filter_by(email=(request.json['email'])).first()
        codeRan = random.randint(0, 999)
        if not user:
            user = User(public_id=(str(uuid.uuid4())),
              email=(request.json['email']),
              name=(request.json['name']),
              student_code=None,
              teacher_code=codeRan,
              password=(generate_password_hash(request.json['password'])),
              role='teacher',
              role_id=3,
              status=1)
            db.session.add(user)
            db.session.commit()
            teacher = Teacher(name=(request.json['name']),
              teacher_code=codeRan)
            db.session.add(teacher)
            db.session.commit()
            teacherss = Teacher.query.all()
            teachers = []
            for itm in teacherss:
                teachers.append({'id':itm.id, 
                 'name':itm.name, 
                 'teacher_code':itm.teacher_code})

        else:
            return jsonify('user exist')
    return jsonify({'teachers': teachers})


@admin_routes.route('/add-subject', methods=['POST'])
@token_required
def add_subject(current_user):
    if current_user.role_id == 1:
        codeRan = random.randint(0, 999)
        subject = Subject.query.filter_by(name=(request.json['name']), subject_code=codeRan).first()
        if not subject:
            teacher = Teacher.query.filter_by(teacher_code=(request.json['teacher_code'])).first()
            print(teacher)
            newSubject = Subject(name=(request.json['name']),
              teacher=(teacher.name),
              online_links=None,
              status=1,
              subject_code=codeRan)
            db.session.add(newSubject)
            db.session.commit()
            max_id = db.session.query(func.max(Subject.id)).scalar()
            newTtoS = Teacher_to_subject(subject_id=max_id,
              teacher_id=(teacher.id))
            db.session.add(newTtoS)
            db.session.commit()
            subjectss = Subject.query.all()
            subjects = []
            for itm in subjectss:
                subjects.append({'id':itm.id, 
                 'name':itm.name, 
                 'teacher':itm.teacher, 
                 'status':itm.status})

        else:
            return jsonify('Subject exist')
    return jsonify({'subjects': subjects})


@admin_routes.route('/get-all-attendance', methods=['POST'])
@token_required
def getAttendance(current_user):
    if current_user.role_id == 1:
        attendances = Attendance.query.all()
        output = []
        for itm in attendances:
            subject = Subject.query.filter_by(id=(itm.subject_id)).first()
            student = Student.query.filter_by(student_code=(itm.student_code)).first()
            output.append({'id':itm.id, 
             'subject':subject.name, 
             'student':student.name, 
             'lesson':itm.lesson_id, 
             'year':itm.year, 
             'month':itm.month, 
             'day':itm.day, 
             'time_in':itm.time_in, 
             'time_out':itm.time_out, 
             'img_in':itm.img_in_path, 
             'img_out':itm.img_out_path})

    return jsonify({'attendances': output})