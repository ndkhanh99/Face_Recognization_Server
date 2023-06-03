from flask import Blueprint
from flask import Flask, jsonify, request, make_response, session
import datetime
from flask_cors import CORS, cross_origin
from .auth_routes import token_required
from .models import Subject, Teacher, Teacher_to_subject, Attendance, Student, Online_lesson, Student_to_subject
from . import db
attendance_routes = Blueprint('attendance_routes', __name__)

@attendance_routes.route('/get-all-subjects', methods=['GET'])
@token_required
def get_all_users(current_user):
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
    return jsonify('no permission', 403)


@attendance_routes.route('/list/<int:id>', methods=['GET', 'OPTIONS'])
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

    attend_students = Attendance.query.filter_by(subject_id=id).all()
    listAttendance = []
    if current_user.role_id == 3:
        for i in attend_students:
            listAttendance.append({'id':i.id, 
             'student_code':i.student_code, 
             'lesson_id':i.lesson_id, 
             'time_in':i.time_in, 
             'time_out':i.time_out, 
             'status':i.status})

    oneline_class = Online_lesson.query.filter_by(subject_id=id).all()
    onlineClasses = []
    for itm in oneline_class:
        onlineClasses.append({'id':itm.id, 
         'subject_id':itm.subject_id, 
         'lesson':itm.lesson})

    return jsonify({'subjects':output,  'list_attendance':listAttendance,  'online_classes':onlineClasses})


@attendance_routes.route('/add-attendance', methods=['POST'])
@token_required
def subjects_to_student(current_user):
    if current_user.role_id == 3:
        courseId = request.json['courseId']
        lessonId = request.json['lesson']
        stundentCode = request.json['student_code']
        student = Student.query.filter_by(student_code=stundentCode).first()
        student_to_subject = Student_to_subject.query.filter_by(student_id=(student.id), subject_id=courseId).first()
        if not student_to_subject:
            return jsonify({'message': 'no permission'}, 403)
        student_id = student.student_code
        today = datetime.datetime.now()
        newAttend = Attendance(subject_id=courseId,
          lesson_id=lessonId,
          student_code=student_id,
          year=(today.year),
          month=(today.month),
          day=(today.day),
          time_in=(today.strftime('%H:%M:%S')),
          late_time='diem danh bu',
          img_in_path=None,
          time_out=(today.strftime('%H:%M:%S')),
          img_out_path=None,
          status=u'\u0111i\u1ec3m danh b\xf9')
        db.session.add(newAttend)
        db.session.commit()
        return jsonify({'message': 'success'})
    return jsonify({'message': ' no permission'}, 403)


@attendance_routes.route('/update', methods=['POST'])
@token_required
def update(current_user):
    if current_user.role_id == 3:
        id = request.json['id']
        timeIn = request.json['time_in']
        timeOut = request.json['time_out']
        status = request.json['status']
        item = Attendance.query.filter_by(id=id).first()
        item.time_in = timeIn
        item.time_out = timeOut
        item.status = status
        db.session.commit()
        return jsonify('Success')
    return jsonify({'message': ' no permission'}, 403)