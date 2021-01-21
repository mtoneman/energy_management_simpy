import os
import sqlite3
from sqlite3 import Error

pathname =os.path.dirname(os.path.realpath(__file__)) 

SQL_DIR = f"{pathname}/../sql"

def __read_query(queryname):
    filename = SQL_DIR + "/" + queryname + ".sql"
    try:
        with open(filename) as f:
            return f.read()
    except IOError:
        print(f"File {filename} not accessible")
        return ""

def resultset_to_dict(resultset):
    result = {}
    for row in resultset:
        result[row[0]] = __type_guess(row[1])
    return result

def __type_guess(string):
    try:
        return int(string)
    except ValueError:
        try:
            return float(string)
        except ValueError:
            return string


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row
        return conn
    except Error as e:
        print(e)

    return conn

def __run_query(conn, queryname, qparams):
    """
    Run a query which doesn't produce a resultset
    :param conn:
    :param sql:
    :param qparams:
    :return:
    """

    try:
        cur = conn.cursor()
        cur.execute(__read_query(queryname), qparams)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)

def executescript(conn, sql):
    """
    Run a multi statementscript which doesn't produce a resultset
    :param conn:
    :param sql:
    :param qparams:
    :return:
    """

    try:
        cur = conn.cursor()
        cur.executescript(sql)
        conn.commit()
        return cur.lastrowid
    except Error as e:
        print(e)


def insert(conn, queryname, qparams):
    return __run_query(conn, sql, qparams)

def update(conn, queryname, qparams):
    return __run_query(conn, sql, qparams)

def delete(conn, queryname, qparams):
    return __run_query(conn, sql, qparams)



def select(conn, queryname, qparams):
    """
    Run a query with a resultset
    :param conn:
    :param sql:
    :param qparams:
    :return:
    """

    try:
        cur = conn.cursor()
        cur.execute(__read_query(queryname), qparams)

        rows = cur.fetchall()

        return rows
    except Error as e:
        print(e)



