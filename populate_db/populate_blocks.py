import numpy as np
import itertools
from config import *
import MySQLdb
from compute_reward_densities import generate_rewards

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

def populate_blocks(type_, nb_blocks_uppbound_, sd=25):
    table_name = 'blocks'
    db         = MySQLdb.connect(db_host, db_user, db_pwd, db_name)
    cursor     = db.cursor()

    assert(type_ in ['pretraining', 'task'])

    if type_ == 'pretraining':
        sql = "CREATE TABLE {0} (id INT PRIMARY KEY NOT NULL AUTO_INCREMENT, left_symbol VARCHAR(50), right_symbol VARCHAR(50), \
                                        rewards_high VARCHAR(100), rewards_low VARCHAR(100), correct_side VARCHAR(500), \
                                        correct_symbols VARCHAR(20), correct_dimension INT, correct_feature INT, type VARCHAR(50));".format(table_name)
        cursor.execute(sql)

    for idx_b in range(nb_blocks_uppbound_):
        # symbol-index dictionary
        all_possible_symbols = np.array(list(itertools.product(np.arange(nb_features_per_dim), repeat=nb_dimensions)))
        nb_symbols           = len(all_possible_symbols)    
        correct_dimension    = np.random.randint(nb_dimensions)
        incorrect_dimensions = np.delete(np.arange(nb_dimensions), correct_dimension)
        correct_feature      = np.random.randint(nb_features_per_dim)
        correct_symbols      = np.where(all_possible_symbols[:,correct_dimension] == correct_feature)[0]

        ## Training block todo -> add constraint for rewards rates
        symbolsOfBlockRight  = np.zeros(nb_symbols * nb_loops_over_possibilities, dtype=np.int8) - 1
        count                = 0
        for idx_loop in range(nb_loops_over_possibilities):
            while True:
                candidate               = np.random.choice(nb_symbols, replace=False, size=nb_symbols)
                candidateSymbol_correct = np.array([candidate[i] in correct_symbols for i in range(len(candidate))])
                if np.all((np.abs(np.diff(all_possible_symbols[candidate], axis=0)).sum(axis=1) == 1) + \
                          (np.abs(np.diff(all_possible_symbols[candidate], axis=0)).sum(axis=1) == 2) )  \
                            and (symbolsOfBlockRight[count - 1] != candidate[0]) \
                            and ('True  True  True' not in str(candidateSymbol_correct)) and ('False  False  False' not in str(candidateSymbol_correct)): 
                    symbolsOfBlockRight[count : (count + len(candidate))] = candidate
                    count += len(candidate)
                    break
        symbolsOfBlockRightCorrect = np.array([symbolsOfBlockRight[i] in correct_symbols for i in range(len(symbolsOfBlockRight))])                    
        symbolsOfBlockRight        = symbolsOfBlockRight + 1 # such that indexing starts at 1            

        # compute complementary symbols
        complements_training = 1 - all_possible_symbols[symbolsOfBlockRight - 1]
        symbolsOfBlockLeft   = np.array([np.where(np.sum(np.abs(all_possible_symbols - complements_training[i]), axis=1) == 0)[0][0] for i in range(len(complements_training))], dtype=np.int) + 1
        
        # false positive
        while True:
            rewards_low, rewards_high = generate_rewards(sd = sd, nb_samples=nb_symbols * nb_loops_over_possibilities)
            reward_incorrect1 = ((all_possible_symbols[symbolsOfBlockRight-1][:,incorrect_dimensions[0]] == symbolsOfBlockRightCorrect) * rewards_high + (all_possible_symbols[symbolsOfBlockRight-1][:,incorrect_dimensions[0]] != symbolsOfBlockRightCorrect) * rewards_low)
            reward_incorrect2 = ((all_possible_symbols[symbolsOfBlockRight-1][:,incorrect_dimensions[1]] == symbolsOfBlockRightCorrect) * rewards_high + (all_possible_symbols[symbolsOfBlockRight-1][:,incorrect_dimensions[1]] != symbolsOfBlockRightCorrect) * rewards_low)
            fpositives = (rewards_low > rewards_high) * 1
            if np.abs(reward_incorrect1.mean() - 50) < 2. and np.abs(reward_incorrect2.mean() - 50) < 2. and (not sublistExists(list(fpositives), [1,1,1])):
                if type_ == 'pretraining':
                    if (not sublistExists(list(fpositives), [1,1])):
                        break
                else:
                    break

        correct_side = np.array(['right'] * len(complements_training))
        left_correct = np.array([symbolsOfBlockLeft[i] in (correct_symbols + 1) for i in range(len(symbolsOfBlockLeft))])
        correct_side[left_correct] = 'left'


        sql = "Insert into blocks(left_symbol, right_symbol, rewards_high, rewards_low, correct_side, correct_dimension, correct_feature, correct_symbols, type) \
                                                values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                                                                      (symbolsOfBlockLeft, symbolsOfBlockRight, \
                                                                       rewards_high, rewards_low, str(list(correct_side)).replace('\'',''), \
                                                                       correct_dimension + 1, correct_feature + 1, correct_symbols + 1, type_)
        cursor.execute(sql)
        db.commit()

        ###### tried a stronger constraint where at least two dimensions changes every trial => not possible
        # candidate         = [np.random.choice(nb_symbols)]
        # candidate_symbols = np.arange(nb_symbols)
        # for idx_symbol in range(nb_symbols):
        #   next_cand   = (np.sum(np.abs(all_possible_symbols[candidate_symbols] - all_possible_symbols[candidate[-1]]), axis=1) == 2)
        #   candidate.append(np.random.choice(candidate_symbols[next_cand]))
        #   candidate_symbols = candidate_symbols[candidate_symbols!=candidate[-1]]
