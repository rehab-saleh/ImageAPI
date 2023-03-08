import os
from os.path import basename
import shutil
from flask import Blueprint, request, current_app
from flask.helpers import url_for
from helpers import get_secure_filename_filepath, download_from_s3
from werkzeug.utils import redirect
from PIL import Image
from zipfile import ZipFile

bp = Blueprint('android', __name__)

@bp.route('/android', methods=["POST"])
def create_images():
    if request.method == 'POST':
        ICON_SIZES = [29, 40, 57, 58, 60, 80, 87, 114, 120, 180, 1024]

        filename = request.json['filename']
        
        # filename, filepath = get_secure_filename_filepath(filename)
        tempfolder = os.path.join(current_app.config['DOWNLOAD_FOLDER'], 'temp')
        
        if not os.path.exists(tempfolder):
            os.makedirs(tempfolder)

        for size in ICON_SIZES:
            file_stream = download_from_s3(filename)
            image = Image.open(file_stream)
            out = image.resize((size, size))
            outfile = os.path.join(tempfolder, f'{size}.png')
            out.save(outfile, "PNG")

        zipfilename = 'Icons.zip'
        zipfilepath = os.path.join(current_app.config['DOWNLOAD_FOLDER'], zipfilename)
        with ZipFile(zipfilepath, 'w') as zipObj:
            for foldername, subfolders, filenames in os.walk(tempfolder):
                for filename in filenames:
                    filepath = os.path.join(foldername, filename)
                    zipObj.write(filepath, basename(filepath))
            shutil.rmtree(tempfolder)
            print(zipObj.filename)
            return redirect(url_for('download_file', name=zipfilename))
