import torch
import tqdm

def RankLoss(pair_scores, device):
     pad_label = torch.ones(pair_scores.size(0)).to(device)
     logits = pair_scores[:,0] - pair_scores[:,1]
     return torch.nn.BCEWithLogitsLoss()(logits, pad_label)

def _one_epoch_training_loop_without_sample_weights(model, dataloader, optimizer, device):
     model.train()

     losses = []

     for pool, cond in tqdm.tqdm(dataloader):
          optimizer.zero_grad()

          output = model(pool.to(device), cond.to(device))

          loss = RankLoss(output, device)
          losses.append(loss.item())

          loss.backward()

          optimizer.step()
     
     return losses


def _model_inference_for_dataset(model, dataloader, device):
     model.eval()

     meta = []
     cand = []
     scores = []
     for meta_batch, pool_batch, cand_batch in tqdm.tqdm(dataloader):
          
          output = model(pool_batch.to(device), cand_batch.to(device)).detach().cpu()

          meta.extend(meta_batch)
          for i in range(output.size(0)):
               mask = cand_batch[i] > 0
               cand.append(cand_batch[i, mask].tolist())
               scores.append(output[i, mask].tolist())
     
     return meta, cand, scores
     
                
                
                






def _model_inference_for_instance(model, pool, candidates, device):
     pass


def _save_model(model, path):
     torch.save(model.state_dict(), path)

def _load_model(model, path):
     return model.load_state_dict(torch.load(path))

if __name__ == '__main__':
     from torch.optim import Adam
     from model.dataset import DraftDataset, custom_collate_fn
     from model.models import MLP_Pick_Scorer
     from torch.utils.data import DataLoader

     data = DraftDataset('C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\NEO_train', train = True)
     dataloader = DataLoader(data, batch_size = 500, collate_fn=custom_collate_fn, shuffle=True)

     model = MLP_Pick_Scorer(287, [300, 150, 75])
     optim = Adam(model.parameters(), lr = 1e-2)

     if torch.cuda.is_available():
          device = torch.device('cuda')
     else:
          device = torch.device('cpu')

     print(device)

     model = model.to(device)
     losses = _one_epoch_training_loop_without_sample_weights(model, dataloader, optim, device)
     
     _save_model(model, "C:\\Users\\manic\\Desktop\\Draft.ai\\checkpoints\\one_epoch_1e-2")

     #print(losses)

          


