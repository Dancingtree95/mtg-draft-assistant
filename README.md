# mtg-draft-assistant

The repository contains an algorithm for automatic drafting for Magic: the Gathering CCG with a simple GUI that allows for direct play drafts in MTG Arena client without much difficulty. Interactions with the game occur through reading the game logfile. However, the current version has a few limitations. Firstly, the game has several limited formats, and currently, the application can only be used to play the QuickDraft format. Secondly, it does not support all card sets. If a format consists of cards from multiple expansions, such as The Brothers' War with old artifacts, the application will not work. The repository includes a script that checks if an expansion is supported.

If you are not familiar with MTG at all but want to understand what the algorithm does, you can read a brief explanation of MTG and limited through the provided link.

# Architecture
The algorithm ranks the proposed cards in terms of their conditional value relative to the already picked cards in the pool. Each draft step is represented by a one-hot encoded pool of the already picked cards. The model, which is a simple MLP, outputs rank scores for every card in the set based on each vector and then projects them onto the obtainable cards.

To train this model, datasets from 17lands.com were used. These datasets contain a significant number of draft records. Since the model takes into account every step of the draft independently, each draft record generates 45 training examples. Initially, RankNet Loss was used, but it was later switched to CrossEntropy Loss, which noticeably increased accuracy.

However, an independent interpretation of each step is suboptimal and does not correspond to the decision-making process of strong draft players. The cards presented at each step are not completely random. They contain implicit information about decisions made by other players, which can be very useful. For example, it is a bad idea to collect colors that many other players are already collecting.

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

- Add support for the PremierDraft format.
- Solve the problem of lacking support for certain expansions.
- Research and develop a new model architecture that takes into account data from previous draft steps to make decisions.
- There is a lack of a general-purpose MTG Arena log handler. It might be useful to extract the log parsing code into a separate API.



