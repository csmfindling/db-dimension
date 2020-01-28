import numpy as np
import itertools
from config import *
import MySQLdb

import os
db_host = os.environ.get('db_host')
db_user = os.environ.get('db_user')
db_pwd  = os.environ.get('db_pwd')
db_name = os.environ.get('db_name')

def sublistExists(list, sublist):
    for i in range(len(list)-len(sublist)+1):
        if sublist == list[i:i+len(sublist)]:
            return True #return position (i) if you wish
    return False #or -1

def populate_participants_blocks():
    all_possible_symbols = np.array(list(itertools.product(np.arange(nb_features_per_dim), repeat=nb_dimensions)))
    nb_symbols           = len(all_possible_symbols)

    table_name = 'participants_blocks'
    db         = MySQLdb.connect(db_host, db_user, db_pwd, db_name)
    cursor     = db.cursor()


    sql = "CREATE TABLE {0} (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, \
                            participant_id INT, blocks_ids VARCHAR(200), correct_dimension VARCHAR(100), unidimensional_block VARCHAR(100));".format(table_name)
    cursor.execute(sql)

    sql = "Select `id`,`correct_dimension` from blocks where `type`='pretraining'"
    cursor.execute(sql)
    pretraining_blocks                                                 = np.array(cursor.fetchall())
    ids_of_pretraining_blocks, correct_dimension_of_pretraining_blocks = pretraining_blocks[:,0], pretraining_blocks[:,1]

    sql = "Select `id`,`correct_dimension` from blocks where `type`='task'"
    cursor.execute(sql)
    task_blocks                                          = np.array(cursor.fetchall())
    ids_of_task_blocks, correct_dimension_of_task_blocks = task_blocks[:,0], task_blocks[:,1]

    if nb_preblocks_per_participant >= nb_dimensions:
        return NotImplemented

    for idx_subj in range(nb_participants_uppbound):
        while True:
            preblocks_participant  = np.random.choice(len(correct_dimension_of_pretraining_blocks), replace=False, size=nb_preblocks_per_participant)
            if (np.unique(np.unique(correct_dimension_of_pretraining_blocks[preblocks_participant], return_counts=True)[-1])[0] == 1): # constraint on number of correct dimensions
                break
        while True:
            taskblocks_participant = np.random.choice(len(correct_dimension_of_task_blocks), replace=False, size=nb_blocks_per_participant)
            correct_dimension_cand = correct_dimension_of_task_blocks[taskblocks_participant]
            if np.all(np.abs(np.unique(correct_dimension_of_task_blocks[taskblocks_participant], return_counts=True)[-1]*1./nb_blocks_per_participant - 1/3.) == .0): # constraint on number of correct dimensions
                if (not sublistExists(list(correct_dimension_cand), [1,1,1])) and (not sublistExists(list(correct_dimension_cand), [2,2,2])) and (not sublistExists(list(correct_dimension_cand), [3,3,3])):
                    break

        unidimensional_block                         = np.zeros(nb_blocks_per_participant + nb_preblocks_per_participant, dtype=np.int)
        indexes_unidimensional                       = nb_preblocks_per_participant + 1 + np.random.randint(3) + np.arange(0, nb_blocks_per_participant, 4)
        unidimensional_block[indexes_unidimensional] = 1

        assert(len(indexes_unidimensional) == 6)

        ids_of_blocks                = np.concatenate((ids_of_pretraining_blocks[preblocks_participant], ids_of_task_blocks[taskblocks_participant]))
        correct_dimensions_of_blocks = np.concatenate((correct_dimension_of_pretraining_blocks[preblocks_participant], correct_dimension_of_task_blocks[taskblocks_participant]))

        sql = "Insert into participants_blocks(participant_id, blocks_ids, correct_dimension, unidimensional_block) \
                                                values('%s', '%s', '%s', '%s')" % \
                                                                      (idx_subj + 1, \
                                                                       ids_of_blocks, correct_dimensions_of_blocks, unidimensional_block)
        cursor.execute(sql)
        db.commit()         



