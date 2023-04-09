import pandas as pd
from collections import Counter
import json
import tqdm
import sys

PATH = 'input data\\draft_data_public.NEO.PremierDraft.csv'

def p1p1_pick_rate(path, columns):
    chunks = []
    cols = [col_name for col_name in columns if ('pack_card' in col_name) or (col_name == 'pick')]


    for chunk in tqdm.tqdm(pd.read_csv(path, chunksize=10000)):
        mask_p1p1 = ( chunk['pack_number'] == 0 ) & ( chunk['pick_number'] == 0 )
        chunk = chunk.loc[mask_p1p1, cols]
        chunks.append(chunk)


    p1p1_data = pd.concat(chunks, axis = 0)


    pick_data, reveal_data = p1p1_data['pick'], p1p1_data.drop('pick', axis = 1)

    pick_counter = pick_data.value_counts().rename_axis('card').reset_index()

    revealed_counter = reveal_data.sum(axis = 0).rename('reveal').rename_axis('card').reset_index()

    revealed_counter['card'] = revealed_counter['card'].apply(lambda x : x.split('pack_card_')[1])

    combined_data = revealed_counter.merge(pick_counter, on = 'card', how = 'left').fillna(0).set_index('card')

    pick_rate = (combined_data['pick'] / combined_data['reveal']).rename('pick_rate')


    return pick_rate

def total_pick_rate(path):

    columns = None

    pick_counter = Counter()
    revealed_counter = Counter()

    for chunk in tqdm.tqdm(pd.read_csv(path, chunksize=10000)):
        if columns is None:
            columns = [col_name for col_name in chunk.columns if ('pack_card' in col_name) or (col_name == 'pick')]
        
        pick_data, reveal_data = chunk['pick'], chunk[columns].drop('pick', axis = 1)
        reveal_data.columns = [col_name.split('pack_card_')[1] for col_name in reveal_data.columns]

        pick_counter += Counter(pick_data)
        revealed_counter += Counter(reveal_data.sum(axis = 0).to_dict())

    
    pick_rate = {}

    for card in revealed_counter.keys():
        if revealed_counter[card] == 0:
            pick_rate[card] = 0
        else:
            pick_rate[card] = pick_counter.get(card, 0) / revealed_counter[card]
    
    return pick_rate
        



        

if __name__ == '__main__':

    pick_rate = total_pick_rate(PATH)

    with open('intermidiate data\\cards_value_total.json', 'w') as f:
        f.write(json.dumps(pick_rate))





