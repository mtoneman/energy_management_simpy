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

if rows is None:
   sys.exit(f"No database found, run setup.py first")

DB_VERSION = rows[0]['version']
print(f"DB VERSION = {DB_VERSION}, SW VERSION = {SW_VERSION}");

for i in range(DB_VERSION, SW_VERSION):
    print(f"Running changes_from_V{i}")
    db.executescript(conn,read_file(f"{SQL_DIR}/changes/changes_from_V{i}.sql"))

