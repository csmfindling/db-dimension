import numpy as np
import itertools
from config import *
import MySQLdb

import os
db_host = os.environ.get('db_host')
db_user = os.environ.get('db_user')
db_pwd  = os.environ.get('db_pwd')
db_name = os.environ.get('db_name')

def populate_dimensions():
    table_name = 'dimensions'

    db     = MySQLdb.connect(db_host, db_user, db_pwd, db_name)
    cursor = db.cursor()


    sql = "CREATE TABLE {0} (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, dimension_id INT NOT NULL, \
                            dimension_name VARCHAR(100) NOT NULL);".format(table_name)
    cursor.execute(sql)

    dimensions = np.array(['shape', 'color', 'grate'])

    for idx_dim in range(len(dimensions)):
        sql = "Insert into dimensions(dimension_id, dimension_name) \
                                                values('%s', '%s')" % \
                                                                      (idx_dim + 1, \
                                                                       dimensions[idx_dim])
        cursor.execute(sql)
        db.commit()
