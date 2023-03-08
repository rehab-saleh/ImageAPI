import os
from flask import Blueprint, json, request, send_from_directory, abort, current_app, jsonify
from flask.helpers import url_for
from werkzeug.utils import redirect
from PIL import Image, ImageFilter, ImageEnhance
from helpers import get_secure_filename_filepath, download_from_s3

bp = Blueprint('filters', __name__, url_prefix='/filters')


@bp.route('/blur', methods=["POST"])
def blur():
    filename = request.json['filename']
    # filename, filepath = get_secure_filename_filepath()
    file_stream = download_from_s3(filename)
    try:
        radius = int(request.json['radius'])
        image = Image.open(file_stream)
        out = image.filter(ImageFilter.GaussianBlur(radius))
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))
    
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404


@bp.route('/contrast', methods=["POST"])
def contrast():
    filename = request.json['filename']
    # filename, filepath = get_secure_filename_filepath(filename)
    file_stream = download_from_s3(filename)

    try:
        factor = float(request.json['factor'])
        image = Image.open(file_stream)
        out = ImageEnhance.Contrast(image).enhance(factor)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404


@bp.route('/brightness', methods=["POST"])
def brightness():
    filename = request.json['filename']
    file_stream = download_from_s3(filename)
    # filename, filepath = get_secure_filename_filepath(filename)

    try:
        factor = float(request.json['factor'])
        image = Image.open(file_stream)
        out = ImageEnhance.Brightness(image).enhance(factor)
        out.save(os.path.join(current_app.config['DOWNLOAD_FOLDER'], filename))
        return redirect(url_for('download_file', name=filename))
    except FileNotFoundError:
        return jsonify({"message": "File not found."}), 404