import json
from mtg_draft_assistant.model.models import MLP_Pick_Scorer_CE

class PickRate(object):
    def __init__(self, path):
        with open(path, 'r', encoding = 'utf-8') as f:
            self.scores = json.loads(f.read())
    
    def __call__(self, draft_data, _):
        last_pack = draft_data[-1]['pack']
        return {name : self.scores[name] for name in last_pack}


class NeuralPickScorer(object):
    def __init__(self):
        pass

    def __call__(self, draft_data, set_code):
        pass


if __name__ == '__main__':
    pass