import os

from flask import Blueprint, render_template, send_from_directory, current_app

download_data_bp = Blueprint('download_data', __name__)

@download_data_bp.route('/download_data')
def download_data():
    # Get list of files in the folder
    files = os.listdir(current_app.config.get("DATA_DIR"))

    return render_template('download_data.html', files=files)

@download_data_bp.route('/download/<filename>')
def download_file(filename):
    # Serve the file from the files folder
    return send_from_directory(current_app.config.get("DATA_DIR"), filename, as_attachment=True)