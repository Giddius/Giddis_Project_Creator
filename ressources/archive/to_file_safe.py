import datetime
import os
import pprint
import self_created.gid_land as gil
import sqlite3
import sys
from contextlib import contextmanager


def add_file_safe_tbl(in_bd_instance):
    _sql = "CREATE TABLE IF NOT EXISTS file_safe_tbl (file_id integer PRIMARY KEY, file_name text, file_extension text, file_time, file_data blob,  UNIQUE(file_data))"
    with in_bd_instance.open_db() as conn:
        conn.execute(_sql)
    print('created file safe table')



def read_as_binary_to_db(in_bd_instance, file_loc):
    _temp_filename = gil.pathmaker(file_loc, st_revsplit='split_getname')
    _temp = os.path.splitext(_temp_filename)
    _extension = _temp[1]
    _filename = _temp[0]
    _time = str(datetime.datetime.now())
    with open(gil.pathmaker(file_loc), 'rb') as b_file:
        binary_file = b_file.read()
    _input_tuple = (_filename, _extension, _time ,binary_file)
    _sql = "INSERT OR IGNORE INTO file_safe_tbl (file_name, file_extension, file_time, file_data) VALUES (?, ?, ?, ?)"
    with in_bd_instance.open_db() as conn:
        conn.execute(_sql, _input_tuple)
    print('inserted' + ' ' + _filename + ' ' + _extension)


class littleDataBaser:
    def __init__(self, db_loc):
        self.db_full_loc = db_loc

    @contextmanager
    def open_db(self):
        conn = sqlite3.connect(self.db_full_loc)
        yield conn.cursor()
        conn.commit()
        conn.close()

def the_process(in_file):
    Input_files = in_file
    DATABASE_LOC = 'D:/Dropbox/hobby/Modding/Projects/Project_creator/ressources/Project_creator.db'
    DB_Handler = littleDataBaser(DATABASE_LOC)
    add_file_safe_tbl(DB_Handler)
    read_as_binary_to_db(DB_Handler, Input_files)
    with DB_Handler.open_db() as conn:
        conn.execute("SELECT file_name, file_extension, file_time FROM file_safe_tbl")
        _query = conn.fetchall()
    pprint.pprint(_query)


os.chdir(sys.argv[1])
for files in sys.argv[2:]:
    the_process(gil.pathmaker(sys.argv[1], files))
sys.exit()
