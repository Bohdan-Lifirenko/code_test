import threading

from app import app  # Імпорт app з __init__.py

def run_server(ip, port):
    app.run(host=ip, port=port)

def run_server_in_thread(ip, port, data_dir, config_file):
    app.config['DATA_DIR'] = data_dir
    app.config['CONFIG_FILE'] = config_file

    flask_thread = threading.Thread(
        target=lambda: app.run(host=ip, port=port)
    )
    flask_thread.start()

def add_variable_to_server_config(name: str, variable):
    app.config[name] = variable


