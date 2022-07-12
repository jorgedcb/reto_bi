#!/usr/bin/python
import psycopg2
from config import config
import datetime


class Postgres_connection:
    @staticmethod
    def connect():
        """ Connect to the PostgreSQL database server """
        connection = None
        try:
            params = config()
            print("Connecting to the PostgreSQL database...")
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            print("PostgreSQL database version:")
            cursor.execute("SELECT version()")
            db_version = cursor.fetchone()
            print(db_version)
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if connection is not None:
                connection.close()
                print("Database connection closed.")

    @staticmethod
    def create_game_table():
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """
                DROP TABLE IF EXISTS games CASCADE;
                CREATE TABLE games(
                id INT GENERATED ALWAYS AS IDENTITY,
                game_id VARCHAR(255) NOT NULL,
                lenght_word INT NOT NULL,
                vowels INT NOT NULL,
                consonants INT NOT NULL,
                init_time TIMESTAMP NOT NULL,
                PRIMARY KEY(id)
                );"""
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    @staticmethod
    def insert_game(data_tuple):
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """INSERT INTO games (game_id, lenght_word, vowels, consonants, init_time) VALUES (%s, %s, %s, %s, %s);"""
            cursor.execute(create_table_query, data_tuple)
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    @staticmethod
    def create_attempts_table():
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """
                DROP TABLE IF EXISTS attempts;
                CREATE TABLE attempts(
                id INT GENERATED ALWAYS AS IDENTITY,
                game_id  INT NOT NULL,
                word_sent VARCHAR(255) NOT NULL,
                score NUMERIC NOT NULL,
                try_datetime TIMESTAMP NOT NULL,
                position_array TEXT[] NOT NULL,
                right_letters_in_wrong_positions TEXT[] NOT NULL,
                current_attempts INT NOT NULL,
                PRIMARY KEY(id),
                CONSTRAINT fk_game
                    FOREIGN KEY(game_id) 
                    REFERENCES games(id)
                );"""
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    @staticmethod
    def insert_attempt(data_tuple):
        connection = None
        start_time = datetime.datetime.now()
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """INSERT INTO attempts (game_id, word_sent, score, try_datetime, position_array,right_letters_in_wrong_positions,current_attempts) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
            cursor.execute(create_table_query, data_tuple)
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    @staticmethod
    def create_information_table():
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """
                DROP TABLE IF EXISTS information;
                CREATE TABLE information(
                id INT GENERATED ALWAYS AS IDENTITY,
                game_id  INT NOT NULL,
                final_time TIMESTAMP NOT NULL,
                time_code TIME NOT NULL,
                time_overall TIME NOT NULL,
                correct_word VARCHAR(255) NOT NULL,
                attempts_needed INT NOT NULL,
                PRIMARY KEY(id),
                CONSTRAINT fk_game
                    FOREIGN KEY(game_id) 
                    REFERENCES games(id)
                );"""
            cursor.execute(create_table_query)
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    @staticmethod
    def insert_information(data_tuple):
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """INSERT INTO information (game_id, final_time, time_code, time_overall, correct_word,attempts_needed) VALUES (%s, %s, %s, %s, %s, %s);"""
            cursor.execute(create_table_query, data_tuple)
            connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    def get_last_id():
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            select_id_query = """SELECT max(id) from  games"""
            cursor.execute(select_id_query)
            last_id = cursor.fetchall()
            cursor.close()
            return last_id[0][0]
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()
