import pandas as pd 
import numpy as np
import sys
import tqdm
import os
import json


from .utils import save_on_disc, load_from_disc


DRAFT_DATA_FOLDER_PATH = 'C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data'
CARD_TO_ID_FOLDER_PATH = 'C:\\Users\\manic\\Desktop\\Draft.ai\\modelIds'


def prepare_draft_data(path):
    with pd.read_csv(path, iterator=True) as df:
        shot = df.get_chunk(1)
        columns = shot.columns

    pack_cards_columns = [col_name for col_name in columns if 'pack_card_' in col_name]
    pool_cards_columns = [col_name for col_name in columns if 'pool_' in col_name]
    cards = [col_name[len('pack_card_'):] for col_name in pack_cards_columns]
    card_to_id = {card_name : i for i, card_name in enumerate(cards)}

    chunks = []

    for chunk in tqdm.tqdm(pd.read_csv(path, chunksize = 10000)):
        pack_card_block = chunk[pack_cards_columns]

        pack_card_block.columns = [card_to_id[card_name] for card_name in cards]
        pack_card_block = pack_card_block.apply( lambda x : x > 0)
        pack_cards = pack_card_block.apply(lambda x : pack_card_block.columns[x].tolist(), axis = 1)

        chunk = chunk.drop(pack_cards_columns + pool_cards_columns, axis = 1)

        chunk['pack_cards'] = pack_cards
        chunk['pick'] = chunk['pick'].map(card_to_id)
        chunk['_pick'] = chunk['pick'].apply(lambda x : [x])

        chunks.append(chunk)
    
    draft_data = pd.concat(chunks, axis = 0)

    draft_data['pool_cards'] = draft_data.groupby(by = 'draft_id')['_pick'] \
                                         .transform(lambda x : np.cumsum(x)) \
                                         .apply(lambda x : x[:-1])
    draft_data = draft_data.drop('_pick', axis = 1)
    
    return draft_data, card_to_id

if __name__ == '__main__':

    args = sys.argv[1:]

    if len(args) == 0:
        raise Exception('It is necesary to select at least path to import file')
    elif len(args) == 1:
        i_path = args[0]
        o_path = DRAFT_DATA_FOLDER_PATH
    elif len(args) == 2:
        i_path, o_apth = args
    else:
        raise Exception('Too many arguments')
    

    draft_data, cards_to_id = prepare_draft_data(i_path)

    expansion = draft_data.loc[0, 'expansion']

    save_on_disc(draft_data, os.path.join(DRAFT_DATA_FOLDER_PATH, expansion), ['pack_cards', 'pool_cards'])

    with open(os.path.join(CARD_TO_ID_FOLDER_PATH, expansion), 'w', encoding = 'utf-8') as f:
        f.write(json.dumps(cards_to_id))





