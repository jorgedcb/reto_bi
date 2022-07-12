#!/usr/bin/python
import psycopg2
from config import config
from datetime import datetime as dt
from datetime import timezone
from datetime import timedelta
from os import path
import itertools as it
import json

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
                time_code TIME NOT NULL,
                time_overall TIME NOT NULL,
                won BOOLEAN NOT NULL,
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
    def insert_game(parameters_response,time_code,time_overall,won):
        data_tuple = tuple(parameters_response.values()) + (time_code,time_overall,won)
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            create_table_query = """INSERT INTO games (game_id, lenght_word,
                vowels, consonants, time_code, time_overall, won) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
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
    def insert_attempts(list_attempts,last_id):
        connection = None
        try:
            params = config()
            connection = psycopg2.connect(**params)
            cursor = connection.cursor()
            for attempt in list_attempts:
                utc_datetime = dt.fromisoformat(attempt['try_datetime']).astimezone(timezone.utc)
                attempt['try_datetime'] = utc_datetime - timedelta(hours=10)
                create_table_query = """INSERT INTO attempts (game_id, word_sent, score,
                    try_datetime, position_array,right_letters_in_wrong_positions,
                    current_attempts) VALUES (%s, %s, %s, %s, %s, %s, %s);"""
                cursor.execute(create_table_query,(last_id,) + tuple(attempt.values()))
                connection.commit()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if connection:
                connection.close()

    @staticmethod
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

# filename = "/home/castilla/Desktop/sofka/reto_bi/OOP/responses.json"
# if path.isfile(filename) is False:
#     raise Exception("File not found")
# with open(filename) as fp:
#     list_responses = json.load(fp)

# list2 = [list(group) for key, group in it.groupby(list_responses, lambda x: x == 'nuevo juego') if not key]
# Postgres_connection.create_attempts_table()
# Postgres_connection.create_game_table()
# for i in range(6,len(list2)):
#     game_responses = list2[i]
#     parameters_response = game_responses[0]
#     time_code = game_responses[-1]['code_time']
#     time_overall = game_responses[-2]['overall_time']
#     list_attempts = [game_responses[x] for x in range(1,len(game_responses)-2)]
#     won = True
#     Postgres_connection.insert_game(parameters_response,time_code,time_overall,won)
#     last_id = Postgres_connection.get_last_id()
#     Postgres_connection.insert_attempts(list_attempts,last_id)
#     print(i)