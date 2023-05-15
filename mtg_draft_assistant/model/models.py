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

class MLP_PickPack_Scorer_CE(torch.nn.Module):

    def __init__(self, input_size, hidden_sizes, **kwargs):
        super().__init__()
        self.input_size = input_size
        hidden_sizes += [input_size]
        self._pool_encoder = MLP(input_size * 2, hidden_sizes, **kwargs) 
        

    def _pool_one_hot_encode(self, input):
        return torch.nn.functional.one_hot(input, self.input_size + 1).sum(axis = 1)[:, 1:].to(torch.float32)
    
    def forward(self, pool, pack):
        pool = self._pool_one_hot_encode(pool)
        pack = self._pool_one_hot_encode(pack)
        inpt = torch.cat((pool, pack), 1)
        return self._pool_encoder(inpt)
    
class MLP_PickPack_Mod_Scorer_CE(torch.nn.Module):

    def __init__(self, input_size, hidden_sizes, **kwargs):
        super().__init__()
        self.input_size = input_size
        hidden_sizes += [input_size]
        self._pool_encoder = MLP(input_size * 2 + 45, hidden_sizes, **kwargs) 
        

    def _pool_one_hot_encode(self, input):
        return torch.nn.functional.one_hot(input, self.input_size + 1).sum(axis = 1)[:, 1:]
    
    def forward(self, pool, pack):
        pool = self._pool_one_hot_encode(pool)
        pack = self._pool_one_hot_encode(pack)
        step = torch.nn.functional.one_hot(pool.sum(axis = 1), 45)
        inpt = torch.cat((pool, pack, step), 1).to(torch.float32)
        return self._pool_encoder(inpt)

class PositionalEncoderLearnable(torch.nn.Module):

    def __init__(self, max_len, d_model):
        super(PositionalEncoderLearnable, self).__init__()
        
        self.weight = torch.nn.parameter.Parameter(torch.empty(1, max_len, d_model))
        torch.nn.init.uniform_(self.weight, -0.1, 0.1)


    def forward(self, x):

        return x + self.weight[:, : x.size(1)]

    
class Transformer_Pick_Scorer(torch.nn.Module):

    def __init__(self, n_cards, card_em_dim = 100, nhead = 4, dim_feedforward = 500, dropout = 0.1, n_layers = 5):

        super().__init__()

        self.n_cards = n_cards
        
        self.CardEncoder = torch.nn.Embedding(n_cards + 2, card_em_dim, padding_idx=0)
        self.PosEncoder = PositionalEncoderLearnable(45, card_em_dim)

        encoder_layer = torch.nn.TransformerEncoderLayer(d_model=card_em_dim, 
                                                         nhead=nhead,
                                                         dim_feedforward=dim_feedforward,
                                                         dropout=dropout,
                                                         batch_first=True
                                                        )
        self.tranformer_encoder = torch.nn.TransformerEncoder(encoder_layer, n_layers, enable_nested_tensor = False)

        self.decoder = torch.nn.Linear(card_em_dim, n_cards)

    def _input_process(self, src):
        _cls = torch.ones((src.size(0), 1)).to(src.device).long()
        _cls = _cls * (self.n_cards + 1)
        src = torch.cat((_cls, src), 1)
        pad_mask = src.eq(0).bool()
        return src, pad_mask

    def forward(self, pool):

        pool, pad_mask = self._input_process(pool)
        pool_encoded = self.CardEncoder(pool)
        pool_encoded = self.PosEncoder(pool_encoded)

        output = self.tranformer_encoder(pool_encoded, src_key_padding_mask = pad_mask)
        output = output[:,0]
        output = self.decoder(output)

        return output


            





if __name__ == '__main__':
    from torch.utils.data import DataLoader

    model = Transformer_Pick_Scorer(3, 4)

    src = torch.LongTensor([[1,1,0], [2,1,1], [3,0,0]])
    output = model(src)
    print(output)
    print(output.size)

    print()
    


