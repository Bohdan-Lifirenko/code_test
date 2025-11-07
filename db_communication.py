import os
import sqlite3
from datetime import date, datetime


def load_slaves_list(data_dir, config_file):
    db_file = os.path.join(data_dir, config_file)
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute("SELECT slave_id, address FROM slaves")
    rows = c.fetchall()
    conn.close()
    return [{'slave_id': row[0], 'address': row[1]} for row in rows]

def table_exists(conn, table_name):
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
    return cursor.fetchone() is not None

def archive_to_sqlite(data_dir, idDevice, value):
    today = date.today().isoformat()
    db_file = os.path.join(data_dir, f"{today}.sqlite")

    conn = sqlite3.connect(db_file)  # Creates or opens file
    cursor = conn.cursor()  # Used to execute SQL commands
    if not table_exists(conn, 'arhive'):
        cursor.execute("""
                       CREATE TABLE 'arhive'
                       (
                           'rowid'
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           'idDevice'
                           TEXT,
                           'idChannel'
                           TEXT,
                           'value'
                           TEXT,
                           'time'
                           INTEGER,
                           'strTime'
                           DATATIME
                       )
                       """)

    # Prepare data for one row
    idChannel = idDevice
    time_int = int(datetime.now().timestamp())  # UNIX timestamp
    strTime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Human-readable

    cursor.execute("""
                   INSERT INTO arhive (idDevice, idChannel, value, time, strTime)
                   VALUES (?, ?, ?, ?, ?)
                   """, (idDevice, idChannel, value, time_int, strTime))

    # Save changes
    conn.commit()

    # # Optional: verify that the row was inserted
    # cursor.execute("SELECT * FROM arhive")
    # for row in cursor.fetchall():
    #     print(row)

    # Close the connection
    conn.close()

# --- Database setup ---
def create_modbus_rtu_config(config_file):
    with sqlite3.connect(config_file) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS rtu_serial_params (
                            id INTEGER PRIMARY KEY,
                            convertor_port TEXT,
                            baudrate INTEGER,
                            bytesize INTEGER,
                            parity TEXT,
                            stopbits INTEGER,
                            polling_period INTEGER
                        )''')
        # Ensure one default config exists
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rtu_serial_params")
        if cur.fetchone()[0] == 0:
            conn.execute("""INSERT INTO rtu_serial_params
                            (convertor_port, baudrate, bytesize, parity, stopbits, polling_period)
                            VALUES ('COM7', 9600, 8, 'N', 1, 1)""")
        conn.commit()

def load_rtu_serial_params(config_file):
    with sqlite3.connect(config_file) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM rtu_serial_params WHERE id = 1")
        config = cur.fetchone()

    if config:
        keys = ["id", "convertor_port", "baudrate", "bytesize", "parity", "stopbits", "polling_period"]
        config_dict = dict(zip(keys, config))
    else:
        config_dict = None

    return config_dict

# --- Database setup ---
def create_servers_config(config_file):
    with sqlite3.connect(config_file) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS servers_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flask_ip TEXT NOT NULL,
                flask_port INTEGER NOT NULL,
                modbus_ip TEXT NOT NULL,
                modbus_port INTEGER NOT NULL
            )
        ''')
        # Ensure one default config exists
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM servers_config")
        if cur.fetchone()[0] == 0:
            conn.execute("""
                           INSERT INTO servers_config (flask_ip, flask_port, modbus_ip, modbus_port)
                           VALUES (?, ?, ?, ?)
                           """, ("127.0.0.1", 5000, "127.0.0.1", 5020))
        conn.commit()

def get_servers_config(config_file):
    with sqlite3.connect(config_file) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM servers_config LIMIT 1").fetchone()
        return dict(row)

def update_servers_config(flask_ip, flask_port, modbus_ip, modbus_port, config_file):
    with sqlite3.connect(config_file) as conn:
        conn.execute("""
            UPDATE servers_config
            SET flask_ip=?, flask_port=?, modbus_ip=?, modbus_port=?
            WHERE id=1
        """, (flask_ip, flask_port, modbus_ip, modbus_port))
        conn.commit()