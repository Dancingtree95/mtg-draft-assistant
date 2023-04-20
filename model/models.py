import torch



class MLP(torch.nn.Sequential):
    
    def __init__(
                 self, input_size, hidden_sizes, 
                 norm_layer = False, 
                 activation_layer = torch.nn.ReLU, 
                 dropout = 0.0
                 ):
        
        layers = []
        
        in_dim = input_size
        for hid_dim in hidden_sizes[:-1]:
            layer = torch.nn.Linear(in_dim, hid_dim)
            layers.append(layer)

            if norm_layer is True:
                layers.append(torch.nn.BatchNorm1d(hid_dim))

            layers.append(activation_layer())

            layers.append(torch.nn.Dropout(dropout))

            in_dim = hid_dim

        layer = torch.nn.Linear(in_dim, hidden_sizes[-1])
        layers.append(layer)

        super().__init__(*layers)


class MLP_Pick_Scorer(torch.nn.Module):

    def __init__(self, input_size, hidden_sizes, **kwargs):
        super().__init__()
        self.input_size = input_size
        self._pool_encoder = MLP(input_size, hidden_sizes, **kwargs) 
        self._pool_encoder.append(torch.nn.Tanh())
        self._cards_embedings = torch.nn.Embedding(input_size + 1, embedding_dim=hidden_sizes[-1], padding_idx=0)

    def _pool_one_hot_encode(self, input):
        return torch.nn.functional.one_hot(input, self.input_size + 1).sum(axis = 1)[:, 1:].to(torch.float32)
    
    def forward(self, pool, conds):
        pool = self._pool_one_hot_encode(pool)
        conds_embeds = self._cards_embedings(conds)
        encoded_pool = self._pool_encoder(pool)
        output = torch.bmm(conds_embeds, encoded_pool.unsqueeze(-1)).squeeze(-1)
        return output
    



class MLP_Pick_Scorer_CE(torch.nn.Module):

    def __init__(self, input_size, hidden_sizes, **kwargs):
        super().__init__()
        self.input_size = input_size
        hidden_sizes += [input_size]
        self._pool_encoder = MLP(input_size, hidden_sizes, **kwargs) 
        

    def _pool_one_hot_encode(self, input):
        return torch.nn.functional.one_hot(input, self.input_size + 1).sum(axis = 1)[:, 1:].to(torch.float32)
    
    def forward(self, pool):
        pool = self._pool_one_hot_encode(pool)
        return self._pool_encoder(pool)

    
class Transformer_Pick_Scorer(torch.nn.Module):

    def __init__(self):
        pass

    def forward(self):
        pass


            





if __name__ == '__main__':
    from model.dataset import DraftDataset, custom_collate_fn
    from torch.utils.data import DataLoader

    dataset = DraftDataset('C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\NEO_test', train = False)

    dataloader = DataLoader(dataset, collate_fn=custom_collate_fn, batch_size= 2, shuffle=False)

    model = MLP_Pick_Scorer(287, [50])

    for meta, pool, cond in dataloader:
        output = model(pool, cond)
        print(output)
        break
