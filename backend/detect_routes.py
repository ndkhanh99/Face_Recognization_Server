from flask import Blueprint
from flask import redirect, render_template, jsonify, url_for, request, make_response, session, Response
import tensorflow as tf
from . import db
import facenet.src.facenet as facenet
import imutils
from imutils.video import VideoStream
import pickle
from .Helper.align import detect_face
import numpy as np, cv2
from .models import Role, User, userSchema, roleSchema, Subject, Attendance, Online_lesson
from . import app
from flask_cors import CORS, cross_origin
import time, os
from .auth_routes import token_required
import datetime, numpy as np, random
cors = CORS(app, resources={'/test': {'origins': '*'}})
detect_routes = Blueprint('detect_routes', __name__)
PRESERVE_CONTEXT_ON_EXCEPTION = False
MINSIZE = 20
THRESHOLD = [0.6, 0.7, 0.7]
FACTOR = 0.709
IMAGE_SIZE = 182
INPUT_IMAGE_SIZE = 160
CLASSIFIER_PATH = '/Users/macbook/Desktop/attendanceServer/backend/models/facemodel.pkl'
FACENET_MODEL_PATH = '/Users/macbook/Desktop/attendanceServer/backend/models/20180402-114759.pb'
student_name = ''
if os.path.exists(CLASSIFIER_PATH) == True:
    with open('/Users/macbook/Desktop/attendanceServer/backend/models/facemodel.pkl', 'rb') as (file):
        model, class_names = pickle.load(file)
    print('Custom Classifier, Successfully loaded')
with tf.Graph().as_default():
    gpu_options = tf.compat.v1.GPUOptions(per_process_gpu_memory_fraction=0.333)
    sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
    with sess.as_default():
        print('Loading feature extraction model')
        facenet.load_model(FACENET_MODEL_PATH)
        images_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name('input:0')
        embeddings = tf.compat.v1.get_default_graph().get_tensor_by_name('embeddings:0')
        phase_train_placeholder = tf.compat.v1.get_default_graph().get_tensor_by_name('phase_train:0')
        pnet, rnet, onet = detect_face.create_mtcnn(sess, '/Users/macbook/Desktop/attendanceServer/backend/Helper/align')

@detect_routes.route('/test', methods=['POST'])
@cross_origin()
def upload_img_file():
    if request.method == 'POST':
        name = detectFaces()
        return jsonify(name)


@detect_routes.route('/time-in', methods=['POST', 'OPTIONS'])
@cross_origin()
@token_required
def checkIn(current_user):
    global student_name
    photo = request.form.get('testImage')
    image_path = os.path.join('/Users/macbook/Desktop/attendanceServer/backend/static/images/studentAttend/checkIn')
    file_name = current_user.student_code + '_' + request.form.get('courseId') + '_' + request.form.get('lessonId') + '.png'
    name = detectFaces(image_path, file_name, current_user.student_code)
    if student_name != '':
        print(student_name)
        username = current_user.name
        if current_user.student_code == name:
            username = current_user.name
            subject_id = request.form.get('courseId')
            lesson_id = request.form.get('lessonId')
            print(subject_id, lesson_id)
            today = datetime.datetime.now()
            late_time = 0
            subject = Online_lesson.query.filter_by(subject_id=subject_id, lesson=lesson_id).first()
            time_compare = datetime.datetime(subject.year, subject.month, subject.day, subject.hour_in, subject.minute_in)
            if not subject:
                return jsonify({'message': 'no lesson found'})
            if today > time_compare:
                print('vao tre:', str(today - time_compare)[:7])
                late_time = str(today - time_compare)[:7]
            check = Attendance.query.filter_by(subject_id=subject_id, lesson_id=lesson_id, student_code=(current_user.student_code)).first()
            print(check)
            if not check: 
                attend = Attendance(subject_id=subject_id,
                lesson_id=lesson_id,
                student_code=(current_user.student_code),
                year=(today.year),
                month=(today.month),
                day=(today.day),
                time_in=(today.strftime('%H:%M:%S')),
                img_in_path=('images/studentAttend/checkIn/' + current_user.student_code + '_' + request.form.get('courseId') + '_' + request.form.get('lessonId') + '.png'),
                late_time=late_time,
                time_out='',
                img_out_path='',
                status='điểm danh chưa đủ')
                db.session.add(attend)
                db.session.commit()

                subject_link = subject.online_url
                print(subject_link)

                return jsonify({'student_code':name,  'subject_link':subject_link,  'status':1,  'late_time':late_time})
            else:

                return jsonify({'message': 'Đã điểm danh'})
            
        return jsonify({'message':'Điểm danh thất bại vì bạn không phải' + username,  'status':0})


@detect_routes.route('/time-out', methods=['POST', 'OPTIONS'])
@cross_origin()
@token_required
def checkOut(current_user):
    photo = request.form.get('testImage')
    image_path = os.path.join('/Users/macbook/Desktop/attendanceServer/backend/static/images/studentAttend/checkOut')
    file_name = current_user.student_code + '_' + request.form.get('courseId') + '_' + request.form.get('lessonId') + '.png'
    name = detectFaces(image_path, file_name, current_user.student_code)
    print(name)
    username = current_user.name
    if current_user.student_code == name:
        username = current_user.name
        subject_id = request.form.get('courseId')
        lesson_id = request.form.get('lessonId')
        print(subject_id, lesson_id)
        today = datetime.datetime.now()
        late_time = 0
        subject = Online_lesson.query.filter_by(subject_id=subject_id, lesson=lesson_id).first()
        time_in_compare = datetime.datetime(subject.year, subject.month, subject.day, subject.hour_in, subject.minute_in)
        time_out_compare = datetime.datetime(subject.year, subject.month, subject.day, subject.hour_out, subject.minute_out)
        if not subject:
            return jsonify({'message': 'no lesson found'})
        check = Attendance.query.filter_by(subject_id=subject_id, lesson_id=lesson_id, student_code=(current_user.student_code)).first()
        newStatus = u'kh\xf4ng \u0111i\u1ec3m danh \u0111\u1ee7'
        print(check)
        if not check:
            return jsonify({'message': u'B\u1ea1n ch\u01b0a \u0111i\u1ec3m danh gi\u1edd v\xe0o'})
        check.time_out = today.strftime('%H:%M:%S')
        check.img_out_path = 'images/studentAttend/checkOut/' + current_user.student_code + '_' + request.form.get('courseId') + '_' + request.form.get('lessonId') + '.png'
        if time_in_compare < today:
            if today < time_out_compare:
                print('ra som:')
                newStatus = u'ra s\u1edbm'
                if check.late_time != 0:
                    newStatus = u'v\xe0o tr\u1ec5 + ra s\u1edbm'
        if time_out_compare < today:
            if today < time_out_compare + datetime.timedelta(minutes=15):
                if check.late_time == '0':
                    newStatus = u'\u0111i\u1ec3m danh \u0111\u1ee7'
                if check.late_time != '0':
                    newStatus = u'v\xe0o tr\u1ec5'
        check.status = newStatus
        db.session.commit()
        return jsonify({'student_code':name,  'status':1,  'message':u'checkout th\xe0nh c\xf4ng',  'trang_thai':newStatus})
    return jsonify({'message':u'\u0110i\u1ec3m danh th\u1ea5t b\u1ea1i v\xec b\u1ea1n kh\xf4ng ph\u1ea3i ' + username,  'status':0})


def detectFaces(image_path, file_name, student_folder):
    global student_name
    count_unknown = 0
    cap  = VideoStream(src=0).start()
    while True:
        # folder = '/Users/macbook/Downloads/raw/182'
        # for filename in os.listdir(folder):
        #     frame = cv2.imread(os.path.join(folder, filename))
        frame = cap.read()
        frame = imutils.resize(frame, width=600)
        frame = cv2.flip(frame, 1)
        rand_name = random.randint(0, 1000)
        bounding_boxes, _ = detect_face.detect_face(frame, MINSIZE, pnet, rnet, onet, THRESHOLD, FACTOR)
        faces_found = bounding_boxes.shape[0]
        try:
            det = bounding_boxes[:, 0:4]
            bb = np.zeros((faces_found, 4), dtype=(np.int32))
            for i in range(faces_found):
                bb[i][0] = det[i][0]
                bb[i][1] = det[i][1]
                bb[i][2] = det[i][2]
                bb[i][3] = det[i][3]
                print(bb[i][3] - bb[i][1])
                print(frame.shape[0])
                print((bb[i][3] - bb[i][1]) / frame.shape[0])
                if (bb[i][3] - bb[i][1]) / frame.shape[0] > 0.25:
                    cropped = frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :]
                    scaled = cv2.resize(cropped, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE), interpolation=(cv2.INTER_CUBIC))
                    scaled = facenet.prewhiten(scaled)
                    scaled_reshape = scaled.reshape(-1, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, 3)
                    feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
                    emb_array = sess.run(embeddings, feed_dict=feed_dict)
                    predictions = model.predict_proba(emb_array)
                    best_class_indices = np.argmax(predictions, axis=1)
                    best_class_probabilities = predictions[(
                        np.arange(len(best_class_indices)), best_class_indices)]
                    best_name = class_names[best_class_indices[0]]
                    print('Name: {}, Probability: {}'.format(best_name, best_class_probabilities))
                    count_unknown += 1
                    if best_class_probabilities > 0.7:
                        print('Name: {}, Probability: {}'.format(best_name, best_class_probabilities))
                        cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0,
                                                                                            255,
                                                                                            0), 2)
                        text_x = bb[i][0]
                        text_y = bb[i][3] + 20
                        cv2.putText(frame, best_name, (text_x, text_y), (cv2.FONT_HERSHEY_COMPLEX_SMALL), 1,
                            (255, 255, 255), thickness=1, lineType=2)
                        cv2.putText(frame, (str(round(best_class_probabilities[0], 3))), (text_x, text_y + 17), (cv2.FONT_HERSHEY_COMPLEX_SMALL),
                            1, (255, 255, 255), thickness=1, lineType=2)
                        cv2.imwrite(os.path.join(image_path, file_name), frame)
                        time.sleep(1)
                        VideoStream(src=0).stop()
                        cap.stop()
                        cv2.destroyAllWindows()
                        student_name = best_name
                        if student_name != '':
                            return best_name
                    else:
                        name = 'Unknown'
                        print('Unknown')
                        print(count_unknown)
                        # cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0,
                        #                                                                     255,
                        #                                                                     0), 2)
                        # text_x = bb[i][0]
                        # text_y = bb[i][3] + 20
                        # cv2.putText(frame, best_name, (text_x, text_y), (cv2.FONT_HERSHEY_COMPLEX_SMALL), 1,
                        #     (255, 255, 255), thickness=1, lineType=2)
                        # cv2.putText(frame, (str(round(best_class_probabilities[0], 3))), (text_x, text_y + 17), (cv2.FONT_HERSHEY_COMPLEX_SMALL),
                        #     1, (255, 255, 255), thickness=1, lineType=2)
                        # time.sleep(1)
                        # unknowName = student_folder + '_' + str(count_unknown) + '.png'
                        # cv2.imwrite(os.path.join('backend/static/images/unknown', unknowName ), frame)
                        if count_unknown == 20:
                            print('break')
                            best_name = 'unknown'
                            VideoStream(src=0).stop()
                            cap.stop()
                            cv2.destroyAllWindows()
                            return best_name

        except:
            pass

        if cv2.waitKey(1) & 255 == ord('q'):
            break

    cv2.destroyAllWindows()