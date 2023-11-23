# mtg-draft-assistant

That repository contains an algorithm for automatic drafting for Magic: the Gathering ccg with a simple GUI that allows directly
play drafts in MTG Arena cleint with a minimum of difficulties. Interactions with a game occur due to reading game logfile. The curent version has several limitations. First, the game has several limited formats and at the moment the application can be used to play only QuickDraft format. Second, it supports not all card sets. If format consist of cards from several expansions, like The Brothers War with old artifacts, application will not work. Repository has a script which check if expansion is supported. 

If you are not familiar with mtg at all, but want to understand what that algorithm do, you can read a brief explonation of mtg and limited by the link. 

# Architecture
The algorithm ranks proposed cards in terms of their conditional value relative to already picked cards in the pool. Every draft step represented by one-hot encoded pool of already picked cards. Model, which is a simple MLP, for every such vector output rank scores for every card in the set, which then projected on obtainable cards. 

To train such model datasets from 17lands.com was used. They contain a sagnificant number of draft records. Since the model takes into account every step of draft independently, every draft record generate 45 train examples. At first i used RankNet Loss, but then switched to CrossEntropy Loss, which gave a noticable increase in accuracy.

Actually, independent interpretation of each step is suboptimal and does not correspond to decision making process of strong draft players. Cards presented on each step are not completely random, they contain implicit information about decisions made by other players, which can be very useful, because, for example, it is bad idea to collect colors that many other players collect. 

# Installation and using
1. Clone repo `git clone https://github.com/Dancingtree95/mtg-draft-assistant.git` and cd into it `cd mtg-draft-assistant`. 
2. Prepare virtual environment `python -m venv draftai` -> `./draftai/Scripts/activate`.
3. Install dependencies `pip install -r requirements.txt`.
4. Go to [mtgjson](https://mtgjson.com/downloads/all-sets/) and download file for expansion you want draft into sets folder. 
5. Run `python check_validity.py`. If it is ok, go to next step. 
6. Go to [17lands.com](https://www.17lands.com/public_datasets), download and unpack anywhere dataset for expansion you want draft. 
7. Run `python train_nn.py path/to/dataset.csv`.
8. Open run_app.py file and set MTG_LOG_PATH variable to your actual path to mtg arena log file. 
9. Run the game, go to settings -> Account -> Detailed Logs.
8. Run `python run_app.py` and have fun.  

# Future work

- 



