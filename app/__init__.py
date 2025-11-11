import os
import threading

from flask import Flask, render_template, current_app

from app.download_data import download_data_bp
from app.logs import logs_bp
from app.modbus_rtu_slaves_list import modbus_rtu_slaves_list_bp
from app.network_config import network_config_bp
from app.rtu_serial_params import rtu_serial_params_bp

app = Flask(__name__)
app.register_blueprint(download_data_bp)
app.register_blueprint(modbus_rtu_slaves_list_bp)
app.register_blueprint(network_config_bp)
app.register_blueprint(rtu_serial_params_bp)
app.register_blueprint(logs_bp)

# Тут можна додати конфігурацію, наприклад:
app.config['SECRET_KEY'] = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/download_data')
def download_data():
    # Get list of files in the folder
    files = os.listdir(current_app.config.get("DATA_DIR"))

    return render_template('download_data.html', files=files)