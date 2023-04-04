from arena_parser import ArenaParser
import tkinter as tk
from collections import defaultdict
import pandas as pd
import json
import os

class CardManager(object):
    # в данной реализации cardmanager хранит только те карты, у которых есть mtgArenaId и modelId

    #ONE.json - 'data' - 'cards' - 'identifiers' - 'mtgArenaId'

    def __init__(self, cards_data_folder, model_repr_folder):
        sets_data = {}
        set_file_names = os.listdir(cards_data_folder)

        for file_name in set_file_names:
            set_code = file_name.split('.')[0]

            path = os.path.join(cards_data_folder, file_name)
            with open(path, 'r', encoding = 'utf-8') as f:
                set_data = json.loads(f.read())
            
            sets_data[set_code] = set_data['data']['cards']
        
        model_ids = {}
        available_sets = os.listdir(model_repr_folder)

        for set_code in available_sets:
            path = os.path.join(model_repr_folder, set_code)
            with open(path, 'r', encoding = 'utf-8') as f:
                card_to_id = json.loads(f.read())
            
            model_ids[set_code] = card_to_id

        data = defaultdict(list)

        for set_code in sets_data:
             
             for card_dict in sets_data[set_code]:
                
                name = card_dict['name']
                data['name'].append(name)

                mtgArenaId = card_dict['identifiers'].get('mtgArenaId', None)
                data['mtgArenaId'].append(mtgArenaId)

                modelId = model_ids[set_code].get(name, None)
                data['modelId'].append(modelId)

                data['set'].append(set_code)
                
                 
             
        dtype = {'name': str, 'mtgArenaId': int, 'modelId': int, 'set': str}
        cards = pd.DataFrame(data)
        cards = cards.dropna(subset = ['mtgArenaId', 'modelId'])
        cards = cards.astype(dtype)
        self.cards = cards

         

    def map(self, cards, set, input_repr, output_repr):
        # пара set и input_repr должны быть уникальными идентификаторами карты
        if not isinstance(cards, list):
            cards = [cards]
        
        result = []

        variant = self.cards.loc[self.cards.set == set].set_index(input_repr)

        for old_repr in cards:
            new_repr = variant.loc[old_repr, output_repr]
            result.append(new_repr)
        
        if len(result) == 1:
            result = result[0]
        
        return result

class DraftTracker(object):

    def __init__(self, arena):
        self.draftmsgnames = ['QuickDraftPack', 'QuickDraftPick', 'EventJoin']

        self.arena = arena

        self.draft_state = []
        self.is_now_draft = None
        self.event_type = None
        self.set = None

    @property
    def is_now_pack(self):
        if len(self.draft_state) == 0:
            return False
        
        if self.draft_state[-1].name == 'QuickDraftPack':
            return True
        else:
            return False
        

    def _check_draft_compleated(self, last_msg):
        if last_msg.name == 'QuickDraftPack':
            if last_msg.draft_status == 'Completed':
                return True
        
        return False
    
    def _set_draft_fields(self, msg):
        self.event_type = msg.event_type
        self.set = msg.event_set

    def update_state(self):

        self.arena.update()
        arena_update = self.arena.new_messages

        draft_related_msgs = [msg for msg in arena_update if msg.name in self.draftmsgnames]


        if len(draft_related_msgs) != 0:
            last_msg = draft_related_msgs[-1]
            event_join_msg_ids = [i for i, msg in enumerate(draft_related_msgs) if msg.name == 'EventJoin']
        
        else:
            if self.is_now_draft is None:
                self.is_now_draft = False
            return 
            
        if self.is_now_draft is None:

            if self._check_draft_compleated(last_msg):
                self.is_now_draft = False
                return 
            
            else:
                self.is_now_draft = True
                self._set_draft_fields(draft_related_msgs[event_join_msg_ids[-1]])
                draft_related_msgs = draft_related_msgs[event_join_msg_ids[-1] + 1:]
        
        elif self.is_now_draft == False:

            if self._check_draft_compleated(last_msg):
                return 
            
            else:
                self.is_now_draft = True
                self._set_draft_fields(draft_related_msgs[event_join_msg_ids[-1]])
                draft_related_msgs = draft_related_msgs[event_join_msg_ids[-1] + 1:]
                event_join_msg_ids = []

        if self.is_now_draft == True:

            if self._check_draft_compleated(last_msg):
                self.is_now_draft = False
                self.draft_state = []
                self.event_type = None
                self.set = None
                return 
            
            if len(event_join_msg_ids) > 0:
                self.draft_state = []
                self._set_draft_fields(draft_related_msgs[event_join_msg_ids[-1]])
                draft_related_msgs = draft_related_msgs[event_join_msg_ids[-1] + 1:]


        if len(draft_related_msgs) == 0:
            return 
        
        self.draft_state.extend(draft_related_msgs)
        




    
class ArenaDraftAssistController(object):

    def __init__(self, arena, card_manager, model):
        self.draftmsgnames = ['QuickDraftPack', 'QuickDraftPick', 'EventJoin']

        self.draft = DraftTracker(arena)
        self.model = model
        self.card_manager = card_manager

        self.draft_state = []

    
    def get_UI_state_update(self):

        self.draft.update_state()

        new_draft_state = self.draft.draft_state

        if self.draft.is_now_draft == False:
            self.draft_state = []
            return 'no draft', None

        elif not self.draft.is_now_pack:
            return 'waiting for next pack', None

        elif new_draft_state == self.draft_state:
            return 'no changes', None
                
        
        self.draft_state = new_draft_state[:]

        
        # подготовить данные и передать в модель. подготовка включает преобразование списка с log msg в список с словарями {pack:[], pick:},
        # а также замену айди карт с ареновских на моделевские
    
        processed_draft_data = []
        for i in range(0, len(self.draft_state) - 1, 2):
            step = {'pack': self.draft_state[i].pack, 'pick': self.draft_state[i + 1].pick}
            processed_draft_data.append(step)
        open_step = {'pack': self.draft_state[-1].pack, 'pick': None}
        processed_draft_data.append(open_step)


        for step in processed_draft_data:
            step['pack'] = self.card_manager.map(step['pack'], self.draft.set, 'mtgArenaId', 'name')

        
        model_response = self.model(processed_draft_data, self.draft.set)
        # response словарь вида {card_id : score}

        '''
        ui_response = {}
        for card_id in model_response:
            card_name = self.card_manager.map(card_id, self.draft.set, 'in_model_id', 'card_name')
            ui_response[card_name] = model_response[card_id]
        '''

        ui_response = model_response

        return ui_response





        

        

        
        
        

        


            
            
                 



        



                




        



