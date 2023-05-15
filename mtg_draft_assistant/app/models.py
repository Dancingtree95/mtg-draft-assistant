import json
import os
from mtg_draft_assistant.model.models import models_buffer
from mtg_draft_assistant.model.train import _load_model

class PickRate(object):
    def __init__(self, path):
        with open(path, 'r', encoding = 'utf-8') as f:
            self.scores = json.loads(f.read())
    
    def __call__(self, draft_data, _):
        last_pack = draft_data[-1]['pack']
        return {name : self.scores[name] for name in last_pack}


class NeuralPickScorer(object):
    def __init__(self, checkpoints_dir_path):
        sets = [name for name in os.listdir(checkpoints_dir_path) if os.path.isdir(os.path.join(checkpoints_dir_path, name))]
        models = {}
        for set in sets:
            model_path = os.path.join(checkpoints_dir_path, set)
            with open(os.path.join(model_path, 'model_config.json'), 'r', encoding = 'utf-8') as f:
                model_config = json.loads(f.read())
            model = models_buffer[model_config['name']](**model_config['params'])
            model = _load_model(model, os.path.join(model_path, 'state_dict'))
            models[set] = model
        self.models = models

    def __call__(self, draft_data, set_code):
        return self.models[set_code].infer(draft_data)


if __name__ == '__main__':
    NeuralPickScorer('C:\\Users\\manic\\Desktop\\Draft.ai\\mtg_draft_assistant\\checkpoints')