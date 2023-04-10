import pandas as pd
import numpy as np
import sys
import os

DRAFT_DATA_FOLDER_PATH = 'C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data'


def make_train_test_datasets(data, seed = 42, test_size = 0.1):

    cols = ['draft_id', 'pick', 'pack_cards', 'pool_cards', 'pack_number', 'pick_number']

    draft_ids = data['draft_id'].unique()
    np.random.seed(seed)
    np.random.shuffle(draft_ids)


    test_size = int(draft_ids.size * test_size)
    test_ids, train_ids = draft_ids[:test_size], draft_ids[test_size:]

    train_data = data.loc[data['draft_id'].isin(train_ids), cols]
    test_data = data.loc[data['draft_id'].isin(test_ids), cols]

    pick_index = cols.index('pick')
    pack_cards_index = cols.index('pack_cards')

    train_data['candidates'] = train_data.apply(lambda x : [[x[pick_index], card] for card in x[pack_cards_index] if x[pick_index] != card], axis = 1)
    train_data = train_data.drop('pack_cards', axis = 1) \
                           .explode('candidates')
    
    test_data = test_data.rename(columns = {'pack_cards' : 'candidates'})


    return train_data, test_data


if __name__ == '__main__':

    args = sys.argv[1:]

    if len(args) != 1:
        raise Exception('Аргумент командной строки должен быть ровно 1 - путь к файлу')
    
    path = args[0]

    file_name = os.path.split(path)[1].split('.')[0]

    full_data = pd.read_parquet(path)

    train_data, test_data = make_train_test_datasets(full_data)

    train_data.to_parquet(os.path.join(DRAFT_DATA_FOLDER_PATH, file_name + '_train.parquet'))
    test_data.to_parquet(os.path.join(DRAFT_DATA_FOLDER_PATH, file_name + '_test.parquet'))
