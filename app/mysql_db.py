import mysql.connector
import dotenv
import os
from config import Config


def execute_update_query(query):
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute(query)
        cnx.commit()
        cursor.close()
        cnx.close()
        return 'Done'
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        if 'Duplicate' in str(err):
            return 'Duplicate'
        return err


def execute_insert_query(query, data):
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute(query, data)
        cnx.commit()
        return 'Done', int(cursor.lastrowid)
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        if 'Duplicate entry' in str(err):
            return 'Duplicate', -1
        return str(err), -1


def execute_read_query(query, fetch_all):
    cnx = get_db_connection()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute(query)
        out = None
        if fetch_all:
            out = cursor.fetchall()
        else:
            out = cursor.fetchone()

        cursor.close()
        cnx.close()
        return out
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        # return str(err)


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DATABASE
        )
        if connection.is_connected():
            return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def close_db_connection(connection):
    if connection.is_connected():
        connection.close()
