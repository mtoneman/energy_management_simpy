#!/usr/bin/env python3

"Setup script for the energymanagment simulation environment"
from energymanagement import db,emutils
import sys, os

# the current path
pathname = os.path.dirname(os.path.abspath(sys.argv[0]))

# location of the database
DATA_DIR = f"{pathname}/data"

# location of the SQL files
SQL_DIR   = f"{pathname}/sql"

tables = ["version","configuration"]
scripts = ["table","alter","data"]

def read_file(filename):
    """Read the file as a string"""
    """ read the specified filename to a string
    :param filename: the full path and file name of the file
    :return: contents of the file as string
    """
    try:
        with open(filename) as f:
            return f.read()
    except IOError:
        print(f"File {filename} not accessible")
        return ""

try:
   SW_VERSION = int(read_file(pathname + "/VERSION.txt"))
except ValueError:
   sys.exit("Failure to get version from  VERSION.txt. Exiting...")

conn = db.create_connection(f"{DATA_DIR}/energymanagement.db")

rows = db.select(conn,"select_version", [])
if rows is not None:
   sys.exit(f"Database {DATA_DIR}/energymanagement.db already exist. Exiting...")

for table in tables:
    # loop over the tables DDL
    for script in scripts:
        # look for CREATE / ALTER / DATA files and apply to database
        db.executescript(conn,read_file(f"{SQL_DIR}/setup/{table}_{script}.sql"))

