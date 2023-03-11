
from flask import Flask, jsonify, request, send_from_directory
from actions import bp as actionsbp
from filters import bp as filtersbp
from android import bp as androidbp
from helpers import allowed_extension, upload_to_s3
import boto3

app = Flask(__name__)

app.config['S3_BUCKET'] = 'image-api-bucket2'
app.config['S3_KEY'] = 'AKIA3V3FQ3OBZFAC4WK3'
app.config['S3_SECRET'] = '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'
app.config['S3_LOCATION'] = 'https://image-api-bucket2.s3.amazonaws.com/uploads/'

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DOWNLOAD_FOLDER = 'downloads/'
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS

app.secret_key = 'SECRET_KEY'
app.register_blueprint(actionsbp)
app.register_blueprint(filtersbp)
app.register_blueprint(androidbp)



@app.route('/')
def index():
    return jsonify({'message': 'Welcome to Image API'})


@app.route('/images', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':

        if 'file' not in request.files:
            return jsonify({'error': 'No file was selected'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file was selected'}), 400

        if not allowed_extension(file.filename):
            return jsonify({'error': 'The extension is not supported.'}), 400

        # filename, filepath = get_secure_filename_filepath(file.filename)

        output = upload_to_s3(file, app.config['S3_BUCKET'])
        # file.save(filepath)

        return jsonify({
            'message': 'File successfully uploaded',
            'filename': output,
        }), 201

    images = []
    s3_resource = boto3.resource('s3', aws_access_key_id=app.config['S3_KEY'],
                                 aws_secret_access_key=app.config['S3_SECRET'])
    s3_bucket = s3_resource.Bucket(app.config['S3_BUCKET'])
    for obj in s3_bucket.objects.all():
        images.append(obj.key)
    return jsonify({"data": images}), 200


@app.route('/downloads/<name>')
def download_file(name):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], name)