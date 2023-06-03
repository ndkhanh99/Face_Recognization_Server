from flask import Blueprint
from flask import redirect, render_template, jsonify, url_for, request, make_response, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import os, uuid
from datetime import datetime, timedelta
from . import db
from . import UPLOAD_FOLDER
from .models import Role, User, userSchema, roleSchema
from .auth_routes import token_required
from .Helper.camera import VideoCamera
import cv2
from . import app
import time, threading
from flask_cors import CORS, cross_origin
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={'/capture-images': {'origins': '*'}})
stream_routes = Blueprint('stream_routes', __name__)
users_sche = userSchema(many=True)
roles_sche = roleSchema(many=True)

@stream_routes.route('/video')
def video():
    return Response((video_stream()), mimetype='multipart/x-mixed-replace; boundary=frame')


@stream_routes.route('/capture-images', methods=['OPTIONS', 'POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def take_faces():
    global status
    name = request.form['name']
    key = request.form['studentCode']
    print(key)
    print(status)
    save_file_thread = threading.Thread(target=(captureImages(key)))
    save_file_thread.start()
    print(status)
    app.app_context().push()
    return jsonify(key)


status = False

def generate_frames():
    generateFrame = VideoCamera()
    while True:
        success, frame = generateFrame.read()
        if status == True:
            print('completely!!')
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        yield '--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + '\r\n'


def video_stream():
    video_camera = VideoCamera()
    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


def captureImages(key):
    global status
    sample_num = 0
    camera = cv2.VideoCapture(0)
    filepath = '/Users/macbook/Desktop/attendanceServer/backend/data/raw/' + key
    isExist = os.path.exists(filepath)
    if not isExist:
        os.makedirs(filepath)
    print('The new directory is created!')
    print(filepath)
    while True:
        success, frame = camera.read()
        img = frame
        if not success:
            break
        elif sample_num == 91:
            break
        else:
            inputID_char = 'duykhanh'
            path = filepath
            img = frame
            filename = '.'.join([str(sample_num), 'png'])
            path = os.path.join(path, filename)
            cv2.imwrite(path, img)
            sample_num += 1
            print('save sample: ', sample_num)
            time.sleep(0.1)
            status = False

    status = False
    camera.release()
    cv2.destroyAllWindows()
    app.app_context().push()
    return jsonify('success')