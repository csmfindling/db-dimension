import numpy as np
import itertools
import sys
from config import *
import MySQLdb
from populate_participants_blocks import populate_participants_blocks
from populate_blocks import populate_blocks
from populate_dimensions import populate_dimensions
from populate_participants_symbols import populate_participants_symbols
from populate_symbols import populate_symbols
import os

if __name__=='__main__':
    # get db info
    db_host = os.environ.get('db_host')
    db_user = os.environ.get('db_user')
    db_pwd  = os.environ.get('db_pwd')
    db_name = os.environ.get('db_name')

    # erase db
    db     = MySQLdb.connect(db_host, db_user, db_pwd, db_name)
    cursor = db.cursor()
    table_names = ['symbols', 'blocks', 'dimensions', 'participants_symbols', 'participants_blocks', 'participants']
    for name in table_names:
        sql    = "DROP TABLE IF EXISTS {0};".format(name)
        cursor.execute(sql)
        db.commit()

    # populate db
    populate_symbols()    
    populate_blocks('pretraining', 50, sd_pretraining_noise)
    populate_blocks('task', nb_blocks_uppbound, sd_task_noise)
    populate_dimensions()
    populate_participants_symbols()
    populate_participants_blocks()
