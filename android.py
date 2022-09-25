from datetime import datetime
import os
from os.path import basename
import shutil
from flask import Blueprint, current_app,  redirect, request, url_for
from helpers import get_secure_filename_filepath
from PIL import Image
from zipfile import ZipFile

bp = Blueprint('android', __name__, url_prefix='/android')

ICON_SIZES = [29, 40, 57, 60, 80, 87, 114, 120, 180, 1024]

@bp.route('/', methods=["POST"])
def create_images():
    filename = request.json['filename']
    filename, filepath = get_secure_filename_filepath(filename)

    tempfolder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
    os.makedirs(tempfolder)

    for size in ICON_SIZES:
       outfile = os.path.join(tempfolder, f'{size}.png')
       image = Image.open(filepath)
       out = image.resize((size, size))
       out.save(outfile, 'PNG')

    now = datetime.now()
    timestamp = str(datetime.timestamp(now)).rsplit('.')[0]
    Zipfilename = f'{timestamp}.zip'
    Zipfilepath = os.path.join(current_app.config['UPLOAD_FOLDER'], Zipfilename)

    with ZipFile(Zipfilepath, 'w') as zipObj:
        for foldername, subfolders, filenames, in os.walk(tempfolder):
            for filepath in filenames:
                filepath = os.path.join(foldername, filename)
                zipObj.write(filepath, basename(filepath))
        shutil.rmtree(tempfolder)
        return redirect(url_for('download_file', name=Zipfilename ))

