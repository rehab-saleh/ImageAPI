import os
from flask import Blueprint, request, current_app, jsonify
from flask.helpers import url_for
from werkzeug.utils import redirect, secure_filename
from PIL import Image
from helpers import get_secure_filename_filepath, download_from_s3


bp = Blueprint('actions', __name__, url_prefix='/actions')

URL = 'https://image-api-bucket2.s3.amazonaws.com'


@bp.route('/resize', methods=["POST"])
def resize():
    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    try:
        file_stream = download_from_s3(filename)
        image = Image.open(file_stream)
        width, height = int(request.json['width']), int(request.json['height'])
        out = image.resize((width, height))
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))
        
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404


@bp.route('/presets/<preset>', methods=["POST"])
def resize_preset(preset):
    presets = {'small': (640, 480), 'medium': (1280, 960), 'large': (1600, 1200)}
    if preset not in presets:
        return jsonify({"message": "The preset is not available"}), 400

    filename = request.json['filename']
    file_stream = download_from_s3(filename)
    # filename, filepath = get_secure_filename_filepath(filename)

    try:
        size = presets[preset]
        image = Image.open(file_stream)
        out = image.resize(size)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))

    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404


@bp.route('/rotate', methods=["POST"])
def rotate():
    filename = request.json['filename']
    file_stream = download_from_s3(filename)
    # filename, filepath = get_secure_filename_filepath()

    try:
        degree = float(request.json['degree'])
        image = Image.open(file_stream)
        out = image.rotate(degree)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404


@bp.route('/flip', methods=["POST"])
def flip():
    filename = request.json['filename']
    file_stream = download_from_s3(filename)

    # filename, filepath = get_secure_filename_filepath(filename)

    try:
        image = Image.open(file_stream)
        out = None
        if request.json['direction'] == 'horizontal':
            out = image.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            out = image.transpose(Image.FLIP_LEFT_RIGHT)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))

    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404