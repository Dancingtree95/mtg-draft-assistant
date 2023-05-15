import pickle
import os
import pandas as pd


def save_on_disc(data, path, sep_cols):

    if not os.path.isdir(path):
        os.makedirs(path)

    meta_path = os.path.join(path, 'meta.prqt')
    data.drop(columns = sep_cols).to_parquet(meta_path)

    for col_name in sep_cols:
        col_value = data[col_name].to_list()
        col_path = os.path.join(path, f'{col_name}.pkl')

        with open(col_path, 'wb') as f:
            pickle.dump(col_value, f)


def load_from_disc(path):
    sep_col_files = os.listdir(path)
    sep_col_files.remove('meta.prqt')

    meta = pd.read_parquet(os.path.join(path, 'meta.prqt'))

    for file_name in sep_col_files:
        name = file_name.split('.')[0]

        with open(os.path.join(path, file_name), 'rb') as f:
            value = pickle.load(f)
        
        meta[name] = value
    
    return meta
        
