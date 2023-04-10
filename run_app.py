from app.draft_assistent import CardManager, ArenaDraftAssistController
from app.arena_parser import ArenaParser
from app.gui import ArenaDraftAssistGUI
from app.models import PickRate


MTG_LOG_PATH = "C:\\Users\\manic\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
#MTG_LOG_PATH = "C:\\Users\\manic\\Desktop\\Draft.ai\\test env\\testlog.txt"
SET_DATA_FOLDER = "C:\\Users\\manic\\Desktop\\Draft.ai\\sets"
INTR_MODEL_REPR_FOLDER = "C:\\Users\\manic\\Desktop\\Draft.ai\\modelIds"
CARD_SCORES_PATH = "C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\NEO_scores.json"
#CARD_SCORES_PATH = "C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\cards_value.json"

arena = ArenaParser(MTG_LOG_PATH)
card_manager = CardManager(SET_DATA_FOLDER, INTR_MODEL_REPR_FOLDER)
model = PickRate(CARD_SCORES_PATH)

controller = ArenaDraftAssistController(arena, card_manager, model)

gui = ArenaDraftAssistGUI(controller)

gui.start()

