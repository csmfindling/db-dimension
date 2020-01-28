import numpy as np
from config import *
import MySQLdb

import os
db_host = os.environ.get('db_host')
db_user = os.environ.get('db_user')
db_pwd  = os.environ.get('db_pwd')
db_name = os.environ.get('db_name')

def populate_participants_symbols():
    table_name = 'participants_symbols'

    db     = MySQLdb.connect(db_host, db_user, db_pwd, db_name)
    cursor = db.cursor()

    sql = "CREATE TABLE {0} (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, participant_id INT, block_number INT, shapes_of_interest VARCHAR(20) NOT NULL, \
                            colors_of_interest VARCHAR(20) NOT NULL, grates_of_interest VARCHAR(20) NOT NULL);".format(table_name)
    cursor.execute(sql)

    # for each subject, assign color, shape and grating pairing coded in base 4 (because there 4 possibilities over each dimension)
    for idx_subj in range(nb_participants_uppbound):

        assert(nb_possibleShapes == nb_possibleGrates)
        assert(nb_possibleShapes == nb_possibleColors)
        nb_possible_features_per_dim = nb_possibleShapes

        # samples pair
        features_per_dims  = np.zeros([nb_blocks_per_participant + nb_preblocks_per_participant, nb_dimensions, nb_features_per_dim]) - 1
        for idx_b in range(nb_blocks_per_participant + nb_preblocks_per_participant):
            while True:
                candidate = np.concatenate([np.random.choice(nb_possible_features_per_dim, replace=False, size=nb_features_per_dim)[np.newaxis] for i in range(nb_dimensions)])
                # differ from previous block on all dimensions
                if np.sum(np.sort(candidate, axis=1) != np.sort(features_per_dims[idx_b - 1,:], axis=1), axis=1, dtype=np.bool).all():
                    if idx_b > 0:
                        # differ from all previous blocks on at least one dimensions
                        if np.sum(np.sort(candidate, axis=1) != np.sort(features_per_dims[:idx_b, :], axis=1), axis=(1,2), dtype=np.bool).all():
                            break
                    else:
                        break
            features_per_dims[idx_b] = candidate

        # verifications
        assert(np.unique(np.reshape(features_per_dims, (nb_blocks_per_participant + nb_preblocks_per_participant, nb_dimensions * nb_features_per_dim)), axis=-1).shape[0] == (nb_blocks_per_participant + nb_preblocks_per_participant))
        assert((np.sum((np.abs(features_per_dims[1:] - features_per_dims[:-1]) > 0), axis=(-1,-2)) >= nb_dimensions).all())

        for idx_b in range(nb_blocks_per_participant + nb_preblocks_per_participant):
            sql = "Insert into participants_symbols(participant_id, block_number, shapes_of_interest, \
                                                    colors_of_interest, \
                                                    grates_of_interest) \
                                                    values('%s', '%s', '%s', '%s', '%s')" % \
                                                                          (idx_subj + 1, idx_b + 1, \
                                                                           str(features_per_dims[idx_b, 0].astype(int)), \
                                                                           str(features_per_dims[idx_b, 1].astype(int)), \
                                                                           str(features_per_dims[idx_b, 2].astype(int)))
            cursor.execute(sql)
            db.commit()
        


        