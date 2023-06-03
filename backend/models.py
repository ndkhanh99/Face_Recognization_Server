from . import db
from . import marsh
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import datetime

class User(db.Model):
    id = db.Column((db.Integer), primary_key=True)
    public_id = db.Column((db.String(50)), unique=True)
    email = db.Column((db.String(50)), unique=True)
    name = db.Column((db.String(50)), unique=False)
    student_code = db.Column((db.String(50)), unique=True, nullable=True)
    password = db.Column((db.String(100)), nullable=False)
    role = db.Column((db.String(100)), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    status = db.Column((db.Integer), nullable=True)
    teacher_code = db.Column((db.String(50)), unique=True, nullable=True)

    def __init__(self, public_id, email, name, student_code, password, role, role_id, status, teacher_code):
        self.public_id = public_id
        self.email = email
        self.name = name
        self.student_code = student_code
        self.password = password
        self.role = role
        self.role_id = role_id
        self.status = status
        self.teacher_code = teacher_code


class Student(db.Model):
    id = db.Column((db.Integer), primary_key=True)
    name = db.Column((db.String(50)), nullable=False)
    student_code = db.Column((db.String(50)), nullable=False)

    def __init__(self, name, student_code):
        self.name = name
        self.student_code = student_code


class Teacher(db.Model):
    id = db.Column((db.Integer), primary_key=True)
    name = db.Column((db.String(50)), nullable=False)
    teacher_code = db.Column((db.String(50)), nullable=False)

    def __init__(self, name, teacher_code):
        self.name = name
        self.teacher_code = teacher_code


class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column((db.Integer), primary_key=True)
    name = db.Column((db.String(50)), nullable=False)
    user_role = db.relationship('User', backref='role_user')

    def __init__(self, name):
        self.name = name


class Subject(db.Model):
    __tablename__ = 'subjects'
    id = db.Column((db.Integer), primary_key=True)
    name = db.Column((db.String(50)), nullable=False)
    teacher = db.Column((db.String(50)), nullable=False)
    online_links = db.Column((db.String(50)), nullable=False)
    status = db.Column((db.Integer), nullable=False)
    subject_code = db.Column((db.String(50)), nullable=False)

    def __init__(self, name, teacher, online_links, status, subject_code):
        self.name = name
        self.teacher = teacher
        self.online_links = online_links
        self.status = status
        self.subject_code = subject_code


class Student_to_subject(db.Model):
    __tablename__ = 'student_to_subject'
    id = db.Column((db.Integer), primary_key=True)
    student_id = db.Column((db.String(50)), nullable=False)
    subject_id = db.Column((db.String(50)), nullable=False)

    def __init__(self, student_id, subject_id):
        self.student_id = student_id
        self.subject_id = subject_id


class Teacher_to_subject(db.Model):
    __tablename__ = 'teacher_to_subject'
    id = db.Column((db.Integer), primary_key=True)
    teacher_id = db.Column((db.String(50)), nullable=False)
    subject_id = db.Column((db.String(50)), nullable=False)

    def __init__(self, teacher_id, subject_id):
        self.teacher_id = teacher_id
        self.subject_id = subject_id


class Attendance(db.Model):
    __tablename__ = 'attendance'
    id = db.Column((db.Integer), primary_key=True)
    subject_id = db.Column((db.String(50)), nullable=False)
    lesson_id = db.Column((db.String(50)), nullable=True)
    student_code = db.Column((db.String(50)), nullable=False)
    year = db.Column((db.Integer), nullable=False)
    month = db.Column((db.Integer), nullable=False)
    day = db.Column((db.Integer), nullable=False)
    time_in = db.Column((db.String(50)), nullable=False)
    img_in_path = db.Column((db.String(50)), nullable=True)
    late_time = db.Column((db.String(50)), nullable=True)
    time_out = db.Column((db.String(50)), nullable=True)
    img_out_path = db.Column((db.String(50)), nullable=True)
    status = db.Column((db.String(50)), nullable=True)

    def __init__(self, subject_id, lesson_id, student_code, year, month, day, time_in, img_in_path, late_time, time_out, img_out_path, status):
        self.subject_id = subject_id
        self.lesson_id = lesson_id
        self.student_code = student_code
        self.year = year
        self.month = month
        self.day = day
        self.time_in = time_in
        self.img_in_path = img_in_path
        self.late_time = late_time
        self.time_out = time_out
        self.img_out_path = img_out_path
        self.status = status


class Online_lesson(db.Model):
    __tablename__ = 'online_lesson'
    id = db.Column((db.Integer), primary_key=True)
    subject_id = db.Column((db.String(50)), nullable=False)
    lesson = db.Column((db.String(50)), nullable=True)
    online_url = db.Column((db.String(50)), nullable=False)
    year = db.Column((db.Integer), nullable=False)
    month = db.Column((db.Integer), nullable=False)
    day = db.Column((db.Integer), nullable=False)
    hour_in = db.Column((db.String(50)), nullable=False)
    minute_in = db.Column((db.String(50)), nullable=True)
    hour_out = db.Column((db.String(50)), nullable=False)
    minute_out = db.Column((db.String(50)), nullable=True)

    def __init__(self, subject_id, lesson, online_url, year, month, day, hour_in, minute_in, hour_out, minute_out):
        self.subject_id = subject_id
        self.lesson = lesson
        self.online_url = online_url
        self.year = year
        self.month = month
        self.day = day
        self.hour_in = hour_in
        self.minute_in = minute_in
        self.hour_out = hour_out
        self.minute_out = minute_out


class userSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = User
        load_instance = True


class roleSchema(marsh.SQLAlchemyAutoSchema):
    user_role = marsh.Nested(userSchema, many=True)

    class Meta:
        model = Role
        load_instance = True


class subjectSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Subject
        load_instance = True


class studentSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Student
        load_instance = True


class teacherSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Teacher
        load_instance = True


class stuToSubSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Student_to_subject
        load_instance = True


class teaToSubSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Teacher_to_subject
        load_instance = True


class attendanceSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Attendance
        load_instance = True


class OnlineLessonSchema(marsh.SQLAlchemyAutoSchema):

    class Meta:
        model = Online_lesson
        load_instance = True