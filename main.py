import npyscreen
import logging
import os
import dotenv
import sys
import threading
from queue import Queue
import time
from typing import Protocol

#todo:  
        #nyelvválasztás és modellválasztás
        #videóátalakítás hanggá ffmpeg segítségével? NEM
        #initial prompttal kiegészítés lehetősége, példával
        #general OS/IO error handling
        #unittests?
        #kilépéskor takarítás: törlése a szétszedett vagy átalakított fájloknak?
        #PySimpleGUI változat?
        #logging törlése        
        #renaming "main.py", deployment, upload

logging.basicConfig(
    filename='test_whisper_w_GPT_log_file.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Audio to text conversion, redaction")
        self.addForm("MISSING_OPENAIAPIKEY", MissingOpenAiApiKey, name="Missing OpenAI API key")
        if not os.getenv("OPENAI_API_KEY"):
            self.setNextForm("MISSING_OPENAIAPIKEY")

class MainForm(npyscreen.ActionForm):
    def create(self):
        from converter import ConverterView
        from redactor import RedactorView

        dotenv.load_dotenv()        
        self.output_queue = Queue()
        self.input_file = None
        self.output_file = None

        self.file_handler = FileHandler(self)
        self.file_handler.create()        
        
        self.converter = ConverterView(self)
        self.converter.create()
        
        self.redactor = RedactorView(self, api_key=os.getenv("OPENAI_API_KEY"))
        self.redactor.create()
        
        self.output_handler = OutputHandler(self, self.output_queue)
        self.output_handler.create()
        
    def on_cancel(self):
        self.output_handler.stop_periodic_update()
        self.parentApp.setNextForm(None)
        
class FileHandler:
    def __init__(self, form):
        self.form = form

    def create(self):

        self.form.choose_input_button = self.form.add(npyscreen.ButtonPress, name="Choose audio file for transcription")
        self.form.choose_input_button.whenPressed = self.choose_input_file
        self.form.input_file_display = self.form.add(npyscreen.FixedText, name="Audio file:")

        self.form.choose_output_button = self.form.add(npyscreen.ButtonPress, name="Choose text file (as output for conversion or input for redaction)")
        self.form.choose_output_button.whenPressed = self.choose_output_file
        self.form.output_file_display = self.form.add(npyscreen.FixedText, name="Text file:")

    def choose_input_file(self):
        from choosefile import ChooseFileForm
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='input')
        form.edit()
        self.form.input_file = form.selected_file
        self.form.converter.update_visibility()

    def choose_output_file(self):
        from choosefile import ChooseFileForm        
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='output')
        form.edit()
        self.form.output_file = form.selected_file
        self.form.converter.update_visibility()
        self.form.redactor.update_visibility()

class ViewInterface(Protocol):
    def update_visibility(self, visible: bool=None) -> None:
        pass

    def display_message_queue(self, message: str) -> None:
        pass
    
    def display_message_confirm(self, message: str) -> None:
        pass
    
    def display_message_ok_cancel(self, message: str) -> None:
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
    
class MissingOpenAiApiKey(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name = "Enter missing OpenAI API key")
    def on_ok(self):
        apikey = self.get.widget(0).value
        if not apikey or apikey.strip() == "":
            self.parentApp.setNextForm("MISSING_OPENAIAPIKEY")
        else:
            dotenv.set_key('.env', "OPENAI_API_KEY", apikey)
        
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")  

class OutputHandler:
    def __init__(self, form, output_queue):
        self.form = form
        self.periodic_update = True
        self.output_queue = output_queue
        
    def create(self):
        self.form.realtime_output = self.form.add(RealtimeOutput, name="Output:", output_queue=self.output_queue, rely=15, relx=1, max_height=10, max_width=128)
        threading.Thread(target=self.update_output).start()

    def update_output(self):
        while self.periodic_update:
            self.form.realtime_output.update_output()
            time.sleep(0.1)

    def stop_periodic_update(self):
        self.periodic_update = False

class AutoScrollPager(npyscreen.Pager):
    def update(self, *args, **keywords):
        super(AutoScrollPager, self).update(*args, **keywords)
        self.start_display_at = len(self.values)

class RealtimeOutput(npyscreen.BoxTitle):
    _contained_widget = AutoScrollPager

    def __init__(self, *args, output_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_queue = output_queue
    
    def update(self, *args, **keywords):
        super(RealtimeOutput, self).update(*args, **keywords)

    def update_output(self):
        while not self.output_queue.empty():
            message = self.output_queue.get()
            self.values.append(message)
            self.display()

'''class OutputThread(threading.Thread):
    def __init__(self, target, args, event):
        super(OutputThread, self).__init__()
        self.target = target
        self.args = args
        self.daemon = True
        self.start()
        self.event = event
        
    def run(self):      
        with RedirectStdout(CustomStdout()):
            self.target(*self.args)
        self.event.set()
        
class RedirectStdout:
    def __init__(self, new_stdout):
        self.new_stdout = new_stdout
        self.old_stdout = None

    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = self.new_stdout

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.old_stdout
'''
class CustomStdout:
    def __init__(self, output_queue):
        self.output_queue = output_queue
        
    def write(self, s):
        if s != '\n':
            self.output_queue.put(s)
        sys.__stdout__.write(s)

    def flush(self):
        sys.__stdout__.flush()    

if __name__ == "__main__":
    app = MyApp()
    app.run()