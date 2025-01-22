import psycopg2
import json

from db_env import (
    DB_CACHE_NAME,
    DB_CACHE_USER,
    DB_CACHE_PASSWORD,
    DB_CACHE_HOST,
    DB_CACHE_PORT,
    DB_CACHE_TABLE_NAME,
)


def connect_to_database():
    try:
        # Replace these values with your actual database credentials
        connection = psycopg2.connect(
            dbname=DB_CACHE_NAME,
            user=DB_CACHE_USER,
            password=DB_CACHE_PASSWORD,
            host=DB_CACHE_HOST,
            port=DB_CACHE_PORT,
        )

        return connection

    except Exception as error:
        print("Error connecting to the database.")


def read_database(hashed_id: str) -> json:
    connection = connect_to_database()

    cursor = connection.cursor()

    cursor.execute(f"SELECT * FROM {DB_CACHE_TABLE_NAME} WHERE id=%s;", (hashed_id,))
    db_data = cursor.fetchall()

    cursor.close()
    connection.close()

    return db_data


def write_to_database(hashed_id, route):
    connection = connect_to_database()
    cursor = connection.cursor()

    cursor.execute(
        f"INSERT INTO {DB_CACHE_TABLE_NAME} (id, route) VALUES (%s, %s);",
        (hashed_id, route),
    )

    connection.commit()
    cursor.close()
    connection.close()
