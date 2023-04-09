import tkinter as tk



class ArenaDraftAssistGUI(object):

    def __init__(self, controller):
        self.controller = controller
        self.data_labels = []
        self.root = tk.Tk()

        self.root.attributes("-topmost", True)

    def _clear_frame(self):
        for label in self.data_labels:
            label.destroy()

    def update_ui(self):

        resp_status, card_scores = self.controller.get_UI_state_update()

        if card_scores is not None:

            self._clear_frame()

            sorted_cards = sorted(card_scores.items(), key = lambda x : x[1], reverse=True)
            
            for i, (card_name, score) in enumerate(sorted_cards):
                label_key = tk.Label(self.root, text=card_name)
                label_key.grid(row=i, column=0)
                label_value = tk.Label(self.root, text='{0:.2f}'.format(score))
                label_value.grid(row=i, column=1)
                self.data_labels.append(label_key)
                self.data_labels.append(label_value)
        
        elif resp_status == 'no draft':

            self._clear_frame()

            label_msg = tk.Label(self.root, text = 'No draft')
            label_msg.grid(row = 5, column = 2)
            self.data_labels.append(label_msg)

        elif resp_status == 'waiting for next pack':

            self._clear_frame()

            label_msg = tk.Label(self.root, text = 'waiting for next pack')
            label_msg.grid(row = 5, column = 2)
            self.data_labels.append(label_msg) 
        
        self.root.after(100, self.update_ui)

    def start(self):
        self.root.after(100, self.update_ui)
        self.root.mainloop()

if __name__ =='__main__':
    pass