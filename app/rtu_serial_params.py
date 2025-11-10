import sqlite3

from flask import Blueprint, current_app, render_template, request, redirect, url_for

from db_communication import load_rtu_serial_params

rtu_serial_params_bp = Blueprint('rtu_serial_params', __name__)

@rtu_serial_params_bp.route('/rtu_serial_params')
def rtu_serial_params():
    with sqlite3.connect(current_app.config.get("CONFIG_FILE")) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM rtu_serial_params WHERE id = 1")
        config = cur.fetchone()

    if config:
        keys = ["id", "convertor_port", "baudrate", "bytesize", "parity", "stopbits", "polling_period"]
        config_dict = dict(zip(keys, config))
    else:
        config_dict = {}

    return render_template("rtu_serial_params.html", config=config_dict)


@rtu_serial_params_bp.route('/change_rtu_serial_params', methods=['POST'])
def change_rtu_serial_params():
    convertor_port = request.form['convertor_port']
    baudrate = int(request.form['baudrate'])
    bytesize = int(request.form['bytesize'])
    parity = request.form['parity']
    stopbits = int(request.form['stopbits'])
    polling_period = int(request.form['polling_period'])



    with sqlite3.connect(current_app.config.get("CONFIG_FILE")) as conn:
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

        #client.change_rtu_serial_params(load_rtu_serial_params(CONFIG_FILE))

    return redirect(url_for('rtu_serial_params.rtu_serial_params'))