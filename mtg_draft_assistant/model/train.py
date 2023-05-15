import torch
import tqdm

def RankLoss(pair_scores, device):
     pad_label = torch.ones(pair_scores.size(0)).to(device)
     logits = pair_scores[:,0] - pair_scores[:,1]
     return torch.nn.BCEWithLogitsLoss()(logits, pad_label)

def MarginLoss(pair_scores, device, margin = 0):
     pad_label = torch.ones(pair_scores.size(0)).to(device)
     return torch.nn.MarginRankingLoss(margin)(pair_scores[:,0], pair_scores[:,1], pad_label)

def CELoss(scores, cand, target, weights = None):
     n_classes = scores.size(1)
     cand_mask = torch.nn.functional.one_hot(cand, n_classes + 1).sum(axis = 1)[:, 1:].eq(0)
     scores.masked_fill_(cand_mask, -torch.inf)
     if weights is not None:
          return (torch.nn.CrossEntropyLoss(reduction = 'none')(scores, target) * weights).mean()
     else:
          return torch.nn.CrossEntropyLoss()(scores, target)

def _one_epoch_trainig_loop_CE(model, dataloader, optimizer, device):
     model.train()

     losses = []

     for pool, cand, target in tqdm.tqdm(dataloader):
          optimizer.zero_grad()

          scores = model(pool.to(device))

          loss = CELoss(scores, cand.to(device), target.to(device))
          losses.append(loss.item())

          loss.backward()

          optimizer.step()
     
     return losses

def _one_epoch_trainig_loop_CE_pickpack(model, dataloader, optimizer, device):
     model.train()

     losses = []

     for pool, cand, target in tqdm.tqdm(dataloader):
          optimizer.zero_grad()

          scores = model(pool.to(device), cand.to(device))

          loss = CELoss(scores, cand.to(device), target.to(device))
          losses.append(loss.item())

          loss.backward()

          optimizer.step()
     
     return losses

def _one_epoch_trainig_loop_CE_pickpack_weights(model, dataloader, optimizer, device):
     model.train()

     losses = []

     for pool, cand, target, weights in tqdm.tqdm(dataloader):
          optimizer.zero_grad()

          scores = model(pool.to(device), cand.to(device))

          loss = CELoss(scores, cand.to(device), target.to(device), weights.to(device))
          losses.append(loss.item())

          loss.backward()

          optimizer.step()
     
     return losses

def _one_epoch_training_loop_rank(model, dataloader, optimizer, device):
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


def _model_inference_for_dataset_rank(model, dataloader, device):
     model.eval()

     meta = []
     cand = []
     scores = []
     for meta_batch, pool_batch, cand_batch in tqdm.tqdm(dataloader):
          
          with torch.no_grad():
               output = model(pool_batch.to(device), cand_batch.to(device)).cpu()

          meta.extend(meta_batch)
          for i in range(output.size(0)):
               mask = cand_batch[i] > 0
               cand.append((cand_batch[i, mask] - 1).tolist())
               scores.append(output[i, mask].tolist())
     
     return meta, cand, scores

def _model_inference_for_dataset_CE(model, dataloader, device):
     model.eval()

     meta = []
     cand = []
     scores = []
     for meta_batch, pool_batch, cand_batch in tqdm.tqdm(dataloader):

          with torch.no_grad():
              output = model(pool_batch.to(device)).cpu()
          
          meta.extend(meta_batch)
          for i in range(output.size(0)):
               mask = cand_batch[i] > 0
               cand.append((cand_batch[i, mask] - 1).tolist())
               scores.append(output[i, cand[-1]].tolist())
     
     return meta, cand, scores

def _model_inference_for_dataset_CE_pickpack(model, dataloader, device):
     model.eval()

     meta = []
     cand = []
     scores = []
     for meta_batch, pool_batch, cand_batch in tqdm.tqdm(dataloader):

          with torch.no_grad():
              output = model(pool_batch.to(device), cand_batch.to(device)).cpu()
          
          meta.extend(meta_batch)
          for i in range(output.size(0)):
               mask = cand_batch[i] > 0
               cand.append((cand_batch[i, mask] - 1).tolist())
               scores.append(output[i, cand[-1]].tolist())
     
     return meta, cand, scores


def _model_inference_for_instance(model, pool, candidates, device):
     pass


def _save_model(model, path):
     torch.save(model.state_dict(), path)

def _load_model(model, path):
     model.load_state_dict(torch.load(path))
     return model

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
     losses = _one_epoch_training_loop_rank(model, dataloader, optim, device)
     
     _save_model(model, "C:\\Users\\manic\\Desktop\\Draft.ai\\checkpoints\\one_epoch_1e-2")

     #print(losses)

          


