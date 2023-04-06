from draft_assistent import CardManager, ArenaDraftAssistController
from arena_parser import ArenaParser
from gui import ArenaDraftAssistGUI
from models import PickRate


MTG_LOG_PATH = "C:\\Users\\manic\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
SET_DATA_FOLDER = "C:\\Users\\manic\\Desktop\\Draft.ai\\sets"
INTR_MODEL_REPR_FOLDER = "C:\\Users\\manic\\Desktop\\Draft.ai\\modelIds"
CARD_SCORES_PATH = "C:\\Users\\manic\\Desktop\\Draft.ai\\intermidiate data\\cards_value_total.json"

arena = ArenaParser(MTG_LOG_PATH)
card_manager = CardManager(SET_DATA_FOLDER, INTR_MODEL_REPR_FOLDER)
model = PickRate(CARD_SCORES_PATH)

controller = ArenaDraftAssistController(arena, card_manager, model)

gui = ArenaDraftAssistGUI(controller)

gui.start()