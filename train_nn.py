import sys
import os
import json
from mtg_draft_assistant.scripts.prepare_draft_data import prepare_draft_data
from mtg_draft_assistant.model.models import MLP_Pick_Scorer_CE
from mtg_draft_assistant.model.dataset import DraftDataset
from mtg_draft_assistant.model.train import _save_model

CARD_TO_ID_FOLDER_PATH = 'modelIds'

path_to_dataset = sys.argv[1]

print('Reading and preprocessing data for trainig nn')
draft_data, cards_to_id = prepare_draft_data(path_to_dataset)
draft_data.rename({'pack_cards' : 'candidates'}, axis = 1, inplace = True)

set_code = draft_data['expansion'].iloc[0]

with open(os.path.join(CARD_TO_ID_FOLDER_PATH, set_code), 'w', encoding = 'utf-8') as f:
        f.write(json.dumps(cards_to_id))

cols = ['pool_cards', 'candidates', 'pick']
data = DraftDataset.build_from_df(draft_data, cols, None)

n_cards = len(cards_to_id)
model_config = {'name' : 'MLP_Pick_Scorer_CE', 
                'params' : {'input_size' : n_cards, 
                            'hidden_sizes' : [300, 300, 300], 
                            'norm_layer' : True
                            } 
                }
model = MLP_Pick_Scorer_CE(**model_config['params'])
print('NN training')
model.fit(data, n_epoch = 2)
print(sum(model._losses[-1000:]) / 1000)

dir_name = os.path.join('checkpoints', set_code)
if not os.path.isdir(dir_name):
    os.mkdir(dir_name)
_save_model(model, os.path.join(dir_name, 'state_dict'))
with open(os.path.join(dir_name, 'model_config.json'), 'w', encoding = 'utf-8') as f:
    f.write(json.dumps(model_config))
