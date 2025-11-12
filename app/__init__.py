import os
import threading

from flask import Flask, render_template, current_app

from app.download_data import download_data_bp
from app.logs import logs_bp
from app.modbus_rtu_slaves_list import modbus_rtu_slaves_list_bp
from app.network_config import network_config_bp
from app.rtu_serial_params import rtu_serial_params_bp

class Config:
    DEBUG = False
    SECRET_KEY = 'your_secret_key'  # Генеруйте випадково: import secrets; secrets.token_hex()
    MAX_CONTENT_LENGTH = 1024 * 1024  # Ліміт розміру запиту (1 MB) для офлайн-стійкості
    TRUSTED_HOSTS = None  # Список довірених хостів для динамічних IP

class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = 'your_secret_key'  # Генеруйте випадково: import secrets; secrets.token_hex()
    #TRUSTED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']  # Для локального тестування офлайн

class ProductionConfig(Config):
    DEBUG = False
    TRUSTED_HOSTS = ['your-domain.com']  # Обмеження для безпеки

app = Flask(__name__)

app.config.from_object(DevelopmentConfig)  # Або ProductionConfig залежно від середовища
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