import mysql.connector

from helpers.read_config import database_config
from datetime import datetime

user, password, hostname, port, db = database_config()


connection = mysql.connector.connect(host=hostname, user=user, password=password)
c = connection.cursor()
c.execute(f"CREATE DATABASE IF NOT EXISTS {db}")

connection.commit()
connection.close()

connection = mysql.connector.connect(host=hostname, user=user, password=password, database=db)
c = connection.cursor()

create_goal_events_table = '''
                CREATE TABLE goal_events
                (
                    id INT NOT NULL AUTO_INCREMENT,
                    trace_id VARCHAR(250) NOT NULL,
                    player_id VARCHAR(250) NOT NULL,
                    goal_speed INTEGER NOT NULL,
                    goal_type VARCHAR(100) NOT NULL,
                    goal_distance INTEGER NOT NULL,
                    date_created DATETIME NOT NULL,
                    CONSTRAINT goal_events_pk PRIMARY KEY (id)
                )
                '''

create_boost_events_table = '''
                CREATE TABLE boost_events
                (
                    id INT NOT NULL AUTO_INCREMENT,
                    player_id VARCHAR(250) NOT NULL,
                    boost_amount INTEGER NOT NULL,
                    total_boost INTEGER NOT NULL,
                    location VARCHAR(100) NOT NULL,
                    trace_id VARCHAR(100) NOT NULL,
                    date_created DATETIME NOT NULL,
                    CONSTRAINT boost_events_pk PRIMARY KEY (id)
                )
                '''

c.execute(create_goal_events_table)
c.execute(create_boost_events_table)

connection.commit()
connection.close()
