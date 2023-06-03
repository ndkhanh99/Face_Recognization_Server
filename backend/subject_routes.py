from flask import Blueprint
from flask import Flask, jsonify, request, make_response, session
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from .auth_routes import token_required
from .models import User, Subject, Student, Student_to_subject, Teacher, Teacher_to_subject, Online_lesson
from . import db
import datetime, base64
from PIL import Image
import os
from io import BytesIO
subject_routes = Blueprint('subject_routes', __name__)

@subject_routes.route('/get-all-subjects', methods=['GET'])
@token_required
def get_all_users(current_user):
    if current_user.role_id == 2:

        student = Student.query.filter_by(student_code=(current_user.student_code)).first()
        studentId = student.id
        subjects_of_student = Student_to_subject.query.filter_by(student_id=studentId).all()
        output = []
        for i in subjects_of_student:
            subject = Subject.query.filter_by(id=(i.subject_id)).first()
            output.append({'id':subject.id, 
                'name':subject.name, 
                'teacher':subject.teacher, 
                'status':subject.status})
    # return jsonify({'subjects': output})

    if current_user.role_id == 3:
        teacher = Teacher.query.filter_by(teacher_code=(current_user.teacher_code)).first()
        teacherId = teacher.id
        subjects_of_teacher = Teacher_to_subject.query.filter_by(teacher_id=teacherId).all()
        output = []
        for i in subjects_of_teacher:
            subject = Subject.query.filter_by(id=(i.subject_id)).first()
            output.append({'id':subject.id, 
             'name':subject.name, 
             'teacher':subject.teacher, 
             'status':subject.status})

    return jsonify({'subjects': output})


@subject_routes.route('/details/<int:id>', methods=['GET', 'OPTIONS'])
@cross_origin()
@token_required
def get_subject_details(current_user, id):
    print(id)
    users = Subject.query.filter_by(id=id)
    output = []
    for user in users:
        output.append({'id':user.id, 
         'name':user.name, 
         'teacher':user.teacher, 
         'status':user.status})

    online_classes = Online_lesson.query.filter_by(subject_id=id).all()
    classes = []
    if current_user.role_id == 2:
        for i in online_classes:
            classes.append({'id':i.id, 
             'subject_id':i.subject_id, 
             'lesson':i.lesson})

    if current_user.role_id == 3:
        for i in online_classes:
            classes.append({'id':i.id, 
             'subject_id':i.subject_id, 
             'lesson':i.lesson, 
             'url':i.online_url, 
             'year':i.year, 
             'month':i.month, 
             'day':i.day, 
             'hour_in':i.hour_in, 
             'minute_in':i.minute_in, 
             'hour_out':i.hour_out, 
             'minute_out':i.minute_out})

    print(online_classes)
    return jsonify({'subjects':output,  'online_classes':classes})


@subject_routes.route('/get-subjects-register', methods=['GET'])
@token_required
def get_subjects_register(current_user):
    if current_user.role_id == 2:
        student = Student.query.filter_by(student_code=(current_user.student_code)).first()
        studentId = student.id
        subjects_of_student = Student_to_subject.query.filter_by(student_id=studentId).all()
        check = []
        for itm in subjects_of_student:
            check.append(int(itm.subject_id))

        print(check)
        subjects = Subject.query.all()
        output = []
        for i in subjects:
            if i.id in set(check):
                output.append({'id':i.id, 
                 'name':i.name, 
                 'teacher':i.teacher, 
                 'status':i.status, 
                 'check':True})
            else:
                output.append({'id':i.id, 
                 'name':i.name, 
                 'teacher':i.teacher, 
                 'status':i.status, 
                 'check':False})

        return jsonify({'subjects': output})
    return jsonify({'message': ' no permission'}, 403)


@subject_routes.route('/add-url', methods=['POST'])
@token_required
def add_url(current_user):
    if current_user.role_id == 3:
        form = request.json['form']
        id = request.json['courseId']
        print(form)
        subject = Subject.query.filter_by(id=(int(id))).first()
        teacher = Teacher.query.filter_by(teacher_code=(current_user.teacher_code)).first()
        print(teacher.id)
        permission_add_subject = Teacher_to_subject.query.filter_by(subject_id=id, teacher_id=(teacher.id)).first()
        if not subject or not permission_add_subject: return make_response(jsonify('no permission'), 403)
        classes = Online_lesson(subject_id=id,
            lesson=(form['lesson']),
            online_url=(form['onlineUrl']),
            year=(form['year']),
            month=(form['month']),
            day=(form['day']),
            hour_in=(form['hour_in']),
            minute_in=(form['minute_in']),
            hour_out=(form['hour_out']),
            minute_out=(form['minute_out']))
        db.session.add(classes)
        db.session.commit()
        return jsonify({'url': form['onlineUrl']})
    # return make_response(jsonify('no permission'), 403)


@subject_routes.route('/subject-to-student', methods=['POST'])
@token_required
def subjects_to_student(current_user):
    if current_user.role_id == 2:
        subject_id = request.json['id']
        student = Student.query.filter_by(student_code=(current_user.student_code)).first()
        studentId = student.id
        newSTS = Student_to_subject(subject_id=subject_id,
          student_id=studentId)
        db.session.add(newSTS)
        db.session.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': ' no permission'}, 403)


@subject_routes.route('/test-datetime', methods=['GET'])
def get_time():
    today = datetime.datetime.now()
    year1 = today.year
    print(year1)
    day1 = today.day
    month1 = today.month
    hour1 = today.hour
    minutes = today.minute
    second = today.second
    year2 = today.strftime('%Y')
    timenow = today.strftime('%H:%M:%S')
    return jsonify(year1, month1, day1, hour1, minutes, second)


@subject_routes.route('/test-upload', methods=['POST'])
@token_required
def test_upload(current_user):
    photo = request.form.get('testImage')
    image_path = os.path.join('/Users/macbook/Desktop/attendanceServer/backend/static/images', 'newimage.png')
    starter = photo.find(',')
    image_data = photo[starter + 1:]
    image_data = bytes(image_data, encoding='ascii')
    im = Image.open(BytesIO(base64.b64decode(image_data)))
    im.save(image_path)
    return jsonify({'msg': 'success'})