import sqlite3

from flask import Blueprint, render_template, request, redirect, url_for, current_app

from db_communication import load_slaves_list

modbus_rtu_slaves_list_bp = Blueprint('modbus_rtu_slaves_list', __name__)

@modbus_rtu_slaves_list_bp.route('/modbus_rtu_slaves_list', methods=['GET'])
def modbus_rtu_slaves_list():
    current_configs = load_slaves_list(current_app.config.get("DATA_DIR"), current_app.config.get("CONFIG_FILE"))

    return render_template('modbus_rtu_slaves_list.html', configs=current_configs)

# Route to add a new slave/register
@modbus_rtu_slaves_list_bp.route('/add_slave', methods=['POST'])
def add_slave():
    slave_id = int(request.form['slave_id'])
    address = int(request.form['address'])

    conn = sqlite3.connect(current_app.config.get("CONFIG_FILE"))
    c = conn.cursor()
    try:
        c.execute("INSERT INTO slaves VALUES (?, ?)", (slave_id, address))
        conn.commit()
    except sqlite3.IntegrityError:
        # Already exists (due to PRIMARY KEY)
        pass
    conn.close()

    #client.change_slaves_config(load_slaves_list(current_app.config.get("DATA_DIR"), CONFIG_FILE))

    return redirect(url_for('modbus_rtu_slaves_list.modbus_rtu_slaves_list'))

# Route to delete a slave/register
@modbus_rtu_slaves_list_bp.route('/delete_slave', methods=['POST'])
def delete_slave():
    slave_id = int(request.form['slave_id'])
    address = int(request.form['address'])

    conn = sqlite3.connect(current_app.config.get("CONFIG_FILE"))
    c = conn.cursor()
    c.execute("DELETE FROM slaves WHERE slave_id = ? AND address = ?", (slave_id, address))
    conn.commit()
    conn.close()

    #client.change_slaves_config(load_slaves_list(current_app.config.get("DATA_DIR"), current_app.config.get("CONFIG_FILE")))

    return redirect(url_for('modbus_rtu_slaves_list.modbus_rtu_slaves_list'))

# Route to edit a slave/register (GET for form, POST for update)
@modbus_rtu_slaves_list_bp.route('/edit_slave/<int:slave_id>/<int:old_address>', methods=['GET', 'POST'])
def edit_slave(slave_id, old_address):
    if request.method == 'POST':
        new_slave_id = int(request.form['slave_id'])
        new_address = int(request.form['address'])

        # If no change, redirect
        if new_slave_id == slave_id and new_address == old_address:
            return redirect(url_for('index'))

        conn = sqlite3.connect(current_app.config.get("CONFIG_FILE"))
        c = conn.cursor()
        c.execute("DELETE FROM slaves WHERE slave_id = ? AND address = ?", (slave_id, old_address))

        # Insert new config (if not exists)
        try:
            c.execute("INSERT INTO slaves VALUES (?, ?)", (new_slave_id, new_address))
        except sqlite3.IntegrityError:
            pass  # Already exists
        conn.commit()
        conn.close()

        #client.change_slaves_config(load_slaves_list(current_app.config.get("DATA_DIR"), current_app.config.get("CONFIG_FILE")))

        return redirect(url_for('modbus_rtu_slaves_list.modbus_rtu_slaves_list'))

    # GET: Render edit form
    return render_template('edit_slave.html', slave_id=slave_id, address=old_address)
