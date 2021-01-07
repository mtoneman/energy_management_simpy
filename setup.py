from energymanagement import db,emutils
import sys, os



print('sys.argv[0] =', sys.argv[0])
pathname = os.path.dirname(sys.argv[0])
print('path =', pathname)
print('full path =', os.path.abspath(pathname))

DATA_DIR = f"{os.path.abspath(pathname)}/data"
SQL_DIR   = f"{os.path.abspath(pathname)}/sql"

conn = db.create_connection(f"{DATA_DIR}/energymanagement.db")

tables = ["configuration"]
scripts = ["table","alter","data"]

def read_db_file(filename):
    try:
        with open(filename) as f:
            return f.read()
    except IOError:
        print(f"File {filename} not accessible")
        return ""


for table in tables:
    print(table)
    for script in scripts:
        db.executescript(conn,read_db_file(f"{SQL_DIR}/{table}_{script}.sql"))

