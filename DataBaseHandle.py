import json
import os
import mysql.connector

table_name = f'SleeperData'
table = 'cr_league_data'


def get_connection(database=None):
    connection_params = None
    try:
        with open(os.path.join(os.getcwd(), 'config.json'), 'r') as file:
            data = json.load(file)
            connection_params = {
                "host": data['host'],
                "user": data['user'],
                "password": data['password']
            }
            if database:
                connection_params["database"] = database

    except FileNotFoundError:
        print("Error: The specified file was not found.")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON from the file. Check for valid JSON format.")


    return mysql.connector.connect(**connection_params)

def create(sql) -> None:
    mydb = get_connection()

    mycursor = mydb.cursor()
    mycursor.execute(f'CREATE DATABASE IF NOT EXISTS {table_name}')

    mydb = get_connection(table_name)
    mycursor = mydb.cursor()
    mycursor.execute(sql)


def create_db() -> None:
    create(f'CREATE TABLE IF NOT EXISTS {table} (playerID VARCHAR(256), week VARCHAR(256), '
           f'roster_id VARCHAR(256), predicted_score VARCHAR(256), pos VARCHAR(256));')


def create_roster_db() -> None:
    create(f'CREATE TABLE IF NOT EXISTS {table}_roster (roster_id VARCHAR(256), week VARCHAR(256), '
           f'predicted_score VARCHAR(256));')


def create_team_wl() -> None:
    create(f'CREATE TABLE IF NOT EXISTS {table}_win_losses (roster_id VARCHAR(256), user_id VARCHAR(256), '
           f'display_name VARCHAR(256), wins VARCHAR(256), losses VARCHAR(256));')


def update_db(sql_string: str) -> None:
    mydb = get_connection(table_name)
    mycursor = mydb.cursor()

    # sql_string = f'INSERT INTO table (Week{week}) VALUES ("{values});'
    mycursor.execute(sql_string)
    mydb.commit()


def cleanup(sql) -> None:
    mydb = get_connection(table_name)
    mycursor = mydb.cursor()

    mycursor.execute(sql)


def cleanup_old_table() -> None:
    cleanup(f'DROP TABLE IF EXISTS {table_name}.{table};')


def cleanup_old_roster_table() -> None:
    cleanup(f'DROP TABLE IF EXISTS {table_name}.{table}_roster;')


def cleanup_old_wl_table() -> None:
    cleanup(f'DROP TABLE IF EXISTS {table_name}.{table}_win_losses ;')


def get_data_by_roster_id_and_week(roster_id: int, week: int):
    return get_data(f'SELECT * FROM {table} WHERE roster_id = {roster_id} AND week = {week};')


def get_roster_data_by_roster_id(roster_id: int, week: int):
    return get_data(f'SELECT * FROM {table}_roster Where roster_id = {roster_id} AND week = {week};')


def get_data(sql):
    mydb = get_connection(table_name)
    mycursor = mydb.cursor()

    mycursor.execute(sql)
    result = mycursor.fetchall()
    mycursor.close()
    return result
