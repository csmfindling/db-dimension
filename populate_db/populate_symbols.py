import numpy as np
import itertools
from config import *
import MySQLdb
import os
db_host = os.environ.get('db_host')
db_user = os.environ.get('db_user')
db_pwd  = os.environ.get('db_pwd')
db_name = os.environ.get('db_name')

def populate_symbols():
  table_name = 'symbols'

  all_possible_symbols = np.array(list(itertools.product(np.arange(nb_features_per_dim), repeat=nb_dimensions)))
  nb_symbols           = len(all_possible_symbols)

  db     = MySQLdb.connect(db_host, db_user, db_pwd, db_name)
  cursor = db.cursor()

  sql = "CREATE TABLE {0} (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, shape_id INT NOT NULL, \
                          color_id INT NOT NULL, grate_id INT NOT NULL);".format(table_name)
  cursor.execute(sql)

  for idx_symb in range(nb_symbols):
      sql = "Insert into symbols(shape_id, color_id, grate_id) \
                                              values('%s', '%s', '%s')" % \
                                                                    (all_possible_symbols[idx_symb, 0] + 1, \
                                                                     all_possible_symbols[idx_symb, 1] + 1, \
                                                                     all_possible_symbols[idx_symb, 2] + 1)
      cursor.execute(sql)
      db.commit()
