from mtg_draft_assistant.app.draft_assistent import CardManager, ArenaDraftAssistController
from mtg_draft_assistant.app.arena_parser import ArenaParser
from mtg_draft_assistant.app.gui import ArenaDraftAssistGUI
from mtg_draft_assistant.app.models import PickRate, NeuralPickScorer


MTG_LOG_PATH = "C:\\Users\\manic\\AppData\\LocalLow\\Wizards Of The Coast\\MTGA\\Player.log"
SET_DATA_FOLDER = "sets"
INTR_MODEL_REPR_FOLDER = "modelIds"
CHEKPOINTS_PATH = "checkpoints"

arena = ArenaParser(MTG_LOG_PATH)
card_manager = CardManager(SET_DATA_FOLDER, INTR_MODEL_REPR_FOLDER)
model = NeuralPickScorer(CHEKPOINTS_PATH)

controller = ArenaDraftAssistController(arena, card_manager, model)

gui = ArenaDraftAssistGUI(controller)

gui.start()

