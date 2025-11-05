import os
import sqlite3
from datetime import date, datetime


def load_configs(data_dir, config_file):
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