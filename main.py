import os
import sqlite3
import threading
import time

from ModbusTCPServer import ModbusTCPServer
from ModbusTCPClient import ModbusTCPClient
from db_communication import load_slaves_list, create_modbus_rtu_config, load_rtu_serial_params

from flask import send_from_directory, Flask, render_template, request, redirect, url_for

# Get absolute path to the folder where the script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
# Database file inside that folder
CONFIG_FILE = os.path.join(DATA_DIR, "config.sqlite")
create_modbus_rtu_config(CONFIG_FILE)

server = ModbusTCPServer(ip='127.0.0.1', port=5020)
server.start()

client = ModbusTCPClient(
    polling_period=1,
    slaves_config=load_slaves_list(DATA_DIR, CONFIG_FILE),
    context=server.context,
    data_dir=DATA_DIR,
    rtu_serial_params_dict=load_rtu_serial_params(CONFIG_FILE)
)
client.start_polling()
app = Flask(__name__)

@app.route('/')
def home():
    # Get list of files in the folder
    files = os.listdir(DATA_DIR)

    return render_template('index.html', files=files)

@app.route('/download/<filename>')
def download_file(filename):
    # Serve the file from the files folder
    return send_from_directory(DATA_DIR, filename, as_attachment=True)

# Flask route to display the data and form
@app.route('/modbus_rtu_slaves_list', methods=['GET'])
def modbus_rtu_slaves_list():
    current_configs = load_slaves_list(DATA_DIR, CONFIG_FILE)

    return render_template('modbus_rtu_slaves_list.html', configs=current_configs)

# Route to add a new slave/register
@app.route('/add_slave', methods=['POST'])
def add_slave():
    slave_id = int(request.form['slave_id'])
    address = int(request.form['address'])

    conn = sqlite3.connect(CONFIG_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO slaves VALUES (?, ?)", (slave_id, address))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already exists (due to PRIMARY KEY)
        pass
    conn.close()

    client.change_slaves_config(load_slaves_list(DATA_DIR, CONFIG_FILE))

    return redirect(url_for('modbus_rtu_slaves_list'))

# Route to delete a slave/register
@app.route('/delete_slave', methods=['POST'])
def delete_slave():
    slave_id = int(request.form['slave_id'])
    address = int(request.form['address'])

    conn = sqlite3.connect(CONFIG_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM slaves WHERE slave_id = ? AND address = ?", (slave_id, address))
    conn.commit()
    conn.close()

    client.change_slaves_config(load_slaves_list(DATA_DIR, CONFIG_FILE))

    return redirect(url_for('modbus_rtu_slaves_list'))

# Route to edit a slave/register (GET for form, POST for update)
@app.route('/edit_slave/<int:slave_id>/<int:old_address>', methods=['GET', 'POST'])
def edit_slave(slave_id, old_address):
    if request.method == 'POST':
        new_slave_id = int(request.form['slave_id'])
        new_address = int(request.form['address'])

        # If no change, redirect
        if new_slave_id == slave_id and new_address == old_address:
            return redirect(url_for('index'))

        conn = sqlite3.connect(CONFIG_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM slaves WHERE slave_id = ? AND address = ?", (slave_id, old_address))

        # Insert new config (if not exists)
        try:
            c.execute("INSERT INTO slaves VALUES (?, ?)", (new_slave_id, new_address))
        except sqlite3.IntegrityError:
            pass  # Already exists
        conn.commit()
        conn.close()

        client.change_slaves_config(load_slaves_list(DATA_DIR, CONFIG_FILE))

        return redirect(url_for('modbus_rtu_slaves_list'))

    # GET: Render edit form
    return render_template('edit_slave.html', slave_id=slave_id, address=old_address)

# --- Routes ---
@app.route('/rtu_serial_params')
def rtu_serial_params():
    with sqlite3.connect(CONFIG_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM rtu_serial_params WHERE id = 1")
        config = cur.fetchone()

    if config:
        keys = ["id", "convertor_port", "baudrate", "bytesize", "parity", "stopbits", "polling_period"]
        config_dict = dict(zip(keys, config))
    else:
        config_dict = {}

    return render_template("rtu_serial_params.html", config=config_dict)


@app.route('/change_rtu_serial_params', methods=['POST'])
def change_rtu_serial_params():
    convertor_port = request.form['convertor_port']
    baudrate = int(request.form['baudrate'])
    bytesize = int(request.form['bytesize'])
    parity = request.form['parity']
    stopbits = int(request.form['stopbits'])
    polling_period = int(request.form['polling_period'])



    with sqlite3.connect(CONFIG_FILE) as conn:
        conn.execute('''UPDATE rtu_serial_params SET
                            convertor_port=?,
                            baudrate=?,
                            bytesize=?,
                            parity=?,
                            stopbits=?,
                            polling_period=?
                        WHERE id=1''',
                     (convertor_port, baudrate, bytesize, parity, stopbits, polling_period))
        conn.commit()

        client.change_rtu_serial_params(load_rtu_serial_params(CONFIG_FILE))

    return redirect(url_for('rtu_serial_params'))

# Example usage in a program with other tasks:
if __name__ == "__main__":
    # Запускаємо Flask в іншому потоці (для розробки; у продакшені використовуйте gunicorn)
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000))
    flask_thread.start()

    # server = ModbusTCPServer(ip='127.0.0.1', port=5020)
    # server.start()
    #
    # client = ModbusTCPClient(
    #     convertor_port='COM7',
    #     baudrate=9600,  # Match your slave's baud rate
    #     bytesize=8,
    #     parity='N',  # 'N' for none, 'E' for even, 'O' for odd
    #     stopbits=1,
    #     polling_period=1,
    #     DATA_DIR=DATA_DIR,
    #     CONFIG_FILE=CONFIG_FILE,
    #     context=server.context
    # )
    # client.start_polling()

    while True:
        print("Run")
        time.sleep(2)

    # # Simulate other tasks running in the main thread
    # try:
    #     for i in range(10):
    #         print(f"Main program task: {i}")
    #         time.sleep(1)
    #
    #     # Stop and restart example
    #     server.stop()
    #     client.stop_polling()
    #     time.sleep(2)
    #
    #     # Run a bit more
    #     for i in range(5):
    #         print(f"Main program task after restart: {i}")
    #         time.sleep(1)
    # finally:
    #     server.stop()