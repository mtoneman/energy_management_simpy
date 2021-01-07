import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return conn

def __run_query(conn, sql, qparams):
    """
    Run a query which doesn't produce a resultset
    :param conn:
    :param sql:
    :param qparams:
    :return:
    """

    try:
        cur = conn.cursor()
        cur.execute(sql, qparams)
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


def insert(conn, sql, qparams):
    return __run_query(conn, sql, qparams)

def update(conn, sql, qparams):
    return __run_query(conn, sql, qparams)

def delete(conn, sql, qparams):
    return __run_query(conn, sql, qparams)



def select(conn, sql, qparams):
    """
    Run a query with a resultset
    :param conn:
    :param sql:
    :param qparams:
    :return:
    """

    try:
        conn.row_factory = lite.Row

        cur = conn.cursor()
        cur.execute(sql, qparams)

        rows = cur.fetchall()

        for row in rows:
            print(row)

        return rows
    except Error as e:
        print(e)



