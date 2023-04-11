from torch.utils.data import Dataset, DataLoader
import pandas as pd
from model.utils import save_on_disc, load_from_disc


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

    def __len__(self):
        return len(self.pool)

    def __getitem__(self, idx):

        if self.train:
            return self.pool[idx], self.candidates[idx]
        else:
            return (self.draft_id[idx], self.pack_num[idx], self.pick_num[idx]), self.pool[idx], self.candidates[idx]
