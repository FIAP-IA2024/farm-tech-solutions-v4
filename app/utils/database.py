import sqlite3
import pandas
import os

DB_PATH = "./database/data.db"
CSV_PATH = "./database/tbl_LEITURA.csv"
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
        INSERT INTO tbl_LEITURA (ltr_UMIDADE, ltr_TEMPERATURA, ltr_PH, ltr_NUTRIENTE_P, ltr_NUTRIENTE_K, ltr_STATUS_IRRIGACAO)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (humidity, temperature, ph, sensor_p, sensor_k, irrigation_status),
    )
    connection.commit()
    connection.close()


def fetch_sensor_data():
    connection = connect()
    query = "SELECT * FROM tbl_LEITURA ORDER BY ltr_DATA DESC"
    data = pandas.read_sql_query(query, connection)

    # Export the data to a CSV file
    data.to_csv(CSV_PATH, index=False)

    data["ltr_DATA"] = pandas.to_datetime(data["ltr_DATA"])
    data["month"] = data["ltr_DATA"].dt.to_period("M")  # Adiciona uma coluna de mês
    connection.close()

    return data
