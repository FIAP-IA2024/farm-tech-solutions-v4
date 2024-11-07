import sqlite3
import os

DB_PATH = "./database/data.db"
INIT_SQL_PATH = "./database/init.sql"
DB_INITIALIZED = False


def initialize_database():
    if not os.path.exists(DB_PATH) or os.stat(DB_PATH).st_size == 0:
        with open(INIT_SQL_PATH, "r") as sql_file:
            sql_script = sql_file.read()

        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        cursor.executescript(sql_script)
        connection.commit()
        connection.close()


def connect():
    global DB_INITIALIZED
    if not DB_INITIALIZED:
        initialize_database()
        DB_INITIALIZED = True

    return sqlite3.connect(DB_PATH)


def save_sensor_data(humidity, temperature, ph, sensor_p, sensor_k, irrigation_status):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO sensor_data (humidity, temperature, ph, sensor_p, sensor_k, irrigation_status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (humidity, temperature, ph, sensor_p, sensor_k, irrigation_status),
    )
    connection.commit()
    connection.close()


def fetch_sensor_data():
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM sensor_data")
    rows = cursor.fetchall()
    connection.close()

    return rows
