import os
import pathlib
import json


class LogMessage(object):

    @classmethod
    def _try_decode(cl, s):
        try:
            json_obj = json.loads(s)
        except json.JSONDecodeError:
            return s
        return json_obj
        
    @classmethod
    def _recursive_json_decode(cl, content):
        if not isinstance(content, dict):
            return content
        
        for key in ['Payload', 'request']:
            if key in content:
                content[key] = cl._recursive_json_decode(cl._try_decode(content[key]))
        
        return content


    @classmethod
    def _extract_json(cl, raw_message):
        start = raw_message.find('{')
        end = raw_message.rfind('}')

        if start == -1 or end == -1:
            return None
        
        try:
            content = json.loads(raw_message[start:end+1])
        except json.JSONDecodeError:
            return None
        content = cl._recursive_json_decode(content)
        
        return content

    @classmethod
    def from_raw_log(cl, raw_message):
        content = cl._extract_json(raw_message)

        for msg_type in cl.__subclasses__():

            if msg_type.check_affiliation(raw_message, content):
                return msg_type(raw_message, content)
            
    @classmethod
    def has_key(cl, content, rec_keys):
        for key in rec_keys:
            if not isinstance(content, dict):
                return False
            
            if key in content:
                content = content[key]
            else:
                return False
        return True
    
    

class QuickDraftPackMsg(LogMessage):

    def __init__(self, raw_message, content):
        content = content['Payload']
        self.pack_number = content['PackNumber']
        self.pick_number = content['PickNumber']
        self.pack = list(map(int, content['DraftPack']))
        self.draft_status = content['DraftStatus']

    @classmethod
    def check_affiliation(cl, raw_message, content):
        return cl.has_key(content, ['Payload', 'DraftStatus'])
    
    @property
    def name(self):
        return 'QuickDraftPack'


class QuickDraftPickMsg(LogMessage):

    def __init__(self, raw_message, content):
        content = content['request']['Payload']['PickInfo']
        self.pack_number = content['PackNumber']
        self.pick_number = content['PickNumber']
        self.pick = int(content['CardId'])
    

    @classmethod
    def check_affiliation(cl, raw_message, content):
        return cl.has_key(content, ['request', 'Payload', 'PickInfo'])
    
    @property
    def name(self):
        return 'QuickDraftPick'



class EventJoinMsg(LogMessage):

    def __init__(self, raw_message, content):
        self.event_name  = content['request']['Payload']['EventName']
        parts = self.event_name.split('_')
        self.event_type = parts[0]
        self.event_set = parts[1]

    @classmethod
    def check_affiliation(cl, raw_message, content):
        return cl.has_key(content, ['request', 'Payload', 'EventName']) and 'Event_Join' in raw_message
    
    @property
    def name(self):
        return 'EventJoin'




class ArenaParser(object):

    def __init__(self, path): 
        self.path = path
        self.incomplete_message_buffer = []
        self.log_state = [] # реализовать хранение полного состояния лога, а не только тех сообщений, которые были добавлены между двумя вызовами метода update
        self.new_messages = []
        self.cursor = None

    def _log_message_start_check(self, line):
        return '[UnityCrossThreadLogger]' in line
    
    def _register_message(self):
        if len(self.incomplete_message_buffer) == 0:
            return 

        raw_message = '\n'.join(self.incomplete_message_buffer)
        self.incomplete_message_buffer = []

        message_obj = LogMessage.from_raw_log(raw_message)

        if message_obj is not None:
            self.new_messages.append(message_obj)

    def update(self, from_begin = False):
        self.new_messages = []

        if self.cursor is None or from_begin:
            self.cursor = 0

        file_size = pathlib.Path(self.path).stat().st_size
        if self.cursor > file_size:
            self.cursor = 0

        with open(self.path, 'r', encoding = 'utf-8') as f:
            f.seek(self.cursor, 0)

            while True:
                line = f.readline()

                if line: 
                    if self._log_message_start_check(line):
                        self._register_message()

                    self.incomplete_message_buffer.append(line)
                    
                else:
                    self.cursor = f.tell()
                    self._register_message()
                    break
 
