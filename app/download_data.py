import os
import json

from flask import Blueprint, render_template, send_from_directory, current_app

download_data_bp = Blueprint('download_data', __name__)

# @download_data_bp.route('/download_data')
# def download_data():
#     # Get list of files in the folder
#     files = os.listdir(current_app.config.get("DATA_DIR"))
#
#     return render_template('download_data.html', files=files)

@download_data_bp.route('/download_data')
def download_data():
    data_dir = current_app.config.get("DATA_DIR")
    files = os.listdir(data_dir)

    # Фільтруємо тільки валідні файли (YYYY-MM-DD.sqlite)
    valid_files = []
    for file in files:
        if file.endswith('.sqlite') and len(file.split('-')) == 3:
            parts = file.split('-')
            year, month, day_ext = parts
            day = day_ext.split('.')[0]
            if year.isdigit() and len(year) == 4 and month.isdigit() and len(month) == 2 and day.isdigit() and len(
                    day) == 2:
                valid_files.append(file)

    # Сортуємо файли
    valid_files.sort(reverse=True)

    # Передаємо файли як JSON для JS
    return render_template('download_data_single.html', files_json=json.dumps(valid_files))

@download_data_bp.route('/download/data/<filename>')
def download_file(filename):
    # Serve the file from the files folder
    return send_from_directory(current_app.config.get("DATA_DIR"), filename, as_attachment=True)