from typing import Protocol
import npyscreen

class ViewInterface(Protocol):
    def update_visibility(self, visible: bool=None) -> None:
        pass

    def display_message_queue(self, message: str) -> None:
        pass
    
    def display_message_confirm(self, message: str) -> None:
        pass
    
    def display_message_ok_cancel(self, message: str) -> None:
        pass
    
    def display_message_yes_no(self, message: str) -> None:
        pass


class BaseView(ViewInterface):
    def __init__(self, form):
        self.form = form

    def display_message_queue(self, message: str):
        self.form.output_queue.put(message)
        
    def display_message_confirm(self, message: str):
        npyscreen.notify_confirm(message)
        
    def display_message_ok_cancel(self, message)-> bool:
        return npyscreen.notify_ok_cancel(message)
    
    def display_message_yes_no(self, message)-> bool:
        return npyscreen.notify_yes_no(message)
    
       