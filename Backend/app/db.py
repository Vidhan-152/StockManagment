import mysql.connector
from mysql.connector import Error

from app.config import DB_CONFIG

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection

    except Error as e:
        print("Database connection failed : ", e)
        return None
    