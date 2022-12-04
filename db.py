import datetime as dt
import functools
import sqlite3
from typing import Optional
from dotenv import load_dotenv
from os import getenv

load_dotenv()
DB_FILE = getenv("DB_FILE") or "tmp/test.db"

def create_connection(db_file=DB_FILE) -> Optional[sqlite3.Connection]:
    """ create a database connection to a SQLite database """

    conn = None
    try:
            conn = sqlite3.connect(db_file)
    except Exception as e:
            print(e)
    return conn

def setup_db() -> None:
    """ create tables in the database """
    conn: Optional[sqlite3.Connection] = create_connection()
    if conn is not None:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS messages (number INTEGER, epochtime INTEGER)''')
        conn.commit()

def run_db_operation(sql: str, values: tuple) -> None:
    """ run a database operation """
    conn: Optional[sqlite3.Connection] = create_connection()
    if conn is not None:
        c = conn.cursor()
        c.execute(sql, values)
        conn.commit()

def run_db_operation_decorator(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs):
        # Do something before
        conn: Optional[sqlite3.Connection] = create_connection()
        sql, values = func(*args, **kwargs)
        # Do something after
        if conn is not None:
            c = conn.cursor()
            c.execute(sql, values)
            conn.commit()
        return None
    return wrapper_decorator

@run_db_operation_decorator
def insert_message(values: tuple[int, int]) -> tuple[str, tuple]:
    """ insert a new message into the messages table """
    sql = '''INSERT INTO messages(number, epochtime) VALUES(?,?)'''
    return (sql, values)

def run_db_query_decorator(func):
    @functools.wraps(func)
    def wrapper_decorator(*args, **kwargs) -> list[tuple]:
        conn: Optional[sqlite3.Connection] = create_connection()
        sql = func(*args, **kwargs)
        results = []
        if conn is not None:
            c = conn.cursor()
            c.execute(sql)
            results = c.fetchall()
        return results
    return wrapper_decorator

@run_db_query_decorator
def get_averages() -> str:
    """ get average of all numbers in messages table """
    sql = '''
    WITH current_time as (
        SELECT MAX(epochtime) as curr_epoch from messages m
    ),
    one_minute as (
        select
            AVG("number") as avg_1m 
        FROM messages, current_time
        WHERE curr_epoch - epochtime <= 60
    ),
    five_minute as (
        select
            AVG("number") as avg_5m 
        FROM messages, current_time
        WHERE curr_epoch - epochtime <= 60*5
    ),
    thirty_minute as (
        select
            AVG("number") as avg_30m 
        FROM messages, current_time
        WHERE curr_epoch - epochtime <= 60*30
    )
    SELECT * FROM one_minute, five_minute, thirty_minute
    '''
    return sql

@run_db_operation_decorator
def delete_old_messages(current_epoch: int = int(dt.datetime.now().strftime('%s')), expire_in_minutes: int = 45) -> tuple[str, tuple[int, int]]:
    sql = '''DELETE FROM messages WHERE ? - epochtime > 60*?'''
    return (sql, (current_epoch, expire_in_minutes))


if __name__ == "__main__":
    setup_db()

    @run_db_query_decorator
    def query_db() -> str:
        return f"SELECT * FROM messages"

    print(query_db())
