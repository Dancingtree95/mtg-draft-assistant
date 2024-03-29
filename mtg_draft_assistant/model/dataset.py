from torch.utils.data import Dataset, DataLoader
from torch import LongTensor, FloatTensor
from torch.nn.utils.rnn import pad_sequence
import pandas as pd
#from mtg_draft_assistant.model.utils import load_from_disc
from .utils import load_from_disc
from tqdm import tqdm
import numpy as np


def train_rank_collator(batch):
    batch = list(zip(*batch))

    pool, cand = batch

    pool = [LongTensor(row) + 1 for row in pool]
    pool = pad_sequence(pool, batch_first = True)
    
    cand = LongTensor(cand) + 1

    return pool, cand

def infer_collator(batch):
    batch = list(zip(*batch))

    *meta, pool, cand = batch

    pool = [LongTensor(row) + 1 for row in pool]
    pool = pad_sequence(pool, batch_first = True)

    cand = [LongTensor(row) + 1 for row in cand]
    cand = pad_sequence(cand, batch_first = True)

    meta = list(zip(*meta))

    return meta, pool, cand

def train_collator(batch):
    batch = list(zip(*batch))

    pool, cand, target = batch

    pool = [LongTensor(row) + 1 for row in pool]
    pool = pad_sequence(pool, batch_first = True)

    cand = [LongTensor(row) + 1 for row in cand]
    cand = pad_sequence(cand, batch_first = True)

    target = LongTensor(target)

    return pool, cand, target

def train_collator_weights(batch):
    batch = list(zip(*batch))

    pool, cand, target, weights = batch

    pool = [LongTensor(row) + 1 for row in pool]
    pool = pad_sequence(pool, batch_first = True)

    cand = [LongTensor(row) + 1 for row in cand]
    cand = pad_sequence(cand, batch_first = True)

    target = LongTensor(target)

    weights = FloatTensor(weights)

    return pool, cand, target, weights




class DraftDataset(Dataset):
    
    def __init__(self, data, columns, transform = None):

        if transform is not None:
            transform(data)

        self.cols = columns

        for col in columns:
            setattr(self, col, data[col].to_numpy())
        
        self._lengths = data.shape[0]
    
    @classmethod
    def build_from_disc(cls, path, columns, transform = None):
        data = load_from_disc(path)
        return cls(data, columns, transform)
    
    @classmethod
    def build_from_df(cls, df, columns, transform = None):
        return cls(df, columns, transform)


    def __len__(self):
    
        return self._lengths

    def __getitem__(self, idx):

        return tuple(getattr(self, col)[idx] for col in self.cols)



if __name__ == '__main__':
    dataset = DraftDataset('C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\NEO_test', train = False)

    dataloader = DataLoader(dataset, collate_fn=infer_collator, batch_size= 100)

    for meta, pool, cand in tqdm(dataloader):
        #print(pool)
        #print(cand)
        #break
        pass