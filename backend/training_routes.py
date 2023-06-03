from flask import Blueprint
from flask import redirect, jsonify, url_for, request, session, Response
from .auth_routes import token_required
from .Helper.camera import VideoCamera
from .Helper.align_dataset_mtcnn import main
from .Helper.classifier import mainTrain
from . import app
from flask_cors import CORS, cross_origin
import os
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={'/*': {'origins': '*'}})
training_routes = Blueprint('training_routes', __name__)

@training_routes.route('/reg_faces', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def regFaces():
    message = request.form['status']
    if message == 'true':
        input_dir = 'backend/data/raw'
        output_dir = 'backend/data/processed'
        image_size = 160
        margin = 32
        random_order = 'random_order'
        gpu_memory_fraction = 0.25
        args = {
            'input_dir': input_dir, 
            'output_dir': output_dir, 
            'image_size': image_size, 
            'margin': margin, 
            'random_order':random_order, 
            'gpu_memory_fraction': gpu_memory_fraction, 
            'detect_multiple_faces': False
         }
        print(args['output_dir'])
        main(args)
        data = 'complete reg faces'
        return jsonify(data)


@training_routes.route('/start_training', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def startTraining():
    os.remove('/Users/macbook/Desktop/attendanceServer/backend/models/facemodel.pkl')
    message = request.form['status']
    if message == 'true':
        data_dir = 'backend/data/processed'
        # test_data = 'backend/data/test/align'
        args = {
            'mode':'TRAIN', 
            'data_dir':data_dir, 
            'model':'backend/models/20180402-114759.pb', 
            'classifier_filename':'backend/models/facemodel.pkl', 
            'use_split_dataset':'store_true', 
            'batch_size':1000, 
            'image_size':160, 
            'seed':666, 
            'min_nrof_images_per_class':70, 
            'nrof_train_images_per_class':60}
        mainTrain(args)
        data = 'complete trained'
        return jsonify(data)