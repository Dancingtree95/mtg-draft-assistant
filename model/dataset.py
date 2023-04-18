from torch.utils.data import Dataset, DataLoader
from torch import LongTensor
from torch.nn.utils.rnn import pad_sequence
import pandas as pd
#from mtg_draft_assistant.model.utils import load_from_disc
from .utils import load_from_disc
from tqdm import tqdm


def custom_collate_fn(batch):
    batch = list(zip(*batch))
    if len(batch) == 2:
        pool, cand = batch

        pool = [LongTensor(row) + 1 for row in pool]
        pool = pad_sequence(pool, batch_first = True)
        
        cand = LongTensor(cand) + 1

        return pool, cand
    
    else:
        meta, pool, cand = batch

        pool = [LongTensor(row) + 1 for row in pool]
        pool = pad_sequence(pool, batch_first = True)

        cand = [LongTensor(row) + 1 for row in cand]
        cand = pad_sequence(cand, batch_first = True)

        return meta, pool, cand


class DraftDataset(Dataset):
    
    def __init__(self, path, train = True):

        data = load_from_disc(path)

        self.train = train

        self.pool = data['pool_cards'].to_list()
        self.candidates = data['candidates'].to_list()

        if not train:
            self.draft_id = data['draft_id'].to_list()
            self.pack_num = data['pack_number'].to_list()
            self.pick_num = data['pick_number'].to_list()
            self.pick = data['pick'].to_list()

    def __len__(self):
        return len(self.pool)

    def __getitem__(self, idx):

        if self.train:
            return self.pool[idx], self.candidates[idx]
        else:
            return (self.draft_id[idx], self.pack_num[idx], self.pick_num[idx], self.pick[idx]), self.pool[idx], self.candidates[idx]



if __name__ == '__main__':
    dataset = DraftDataset('C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\NEO_test', train = False)

    dataloader = DataLoader(dataset, collate_fn=custom_collate_fn, batch_size= 100)

    for meta, pool, cand in tqdm(dataloader):
        #print(pool)
        #print(cand)
        #break
        pass