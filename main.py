import npyscreen
import logging
import os
from Whisper_convert import WhisperConverter
import dotenv
import split_files
import sys
import threading
from queue import Queue
import time
from typing import NamedTuple
from typing import Tuple
from typing import Protocol

#todo:  
        #nyelvválasztás és modellválasztás
        #videóátalakítás hanggá ffmpeg segítségével? NEM
        #initial prompttal kiegészítés lehetősége, példával
        #refactoring: ChooseFileForm; util
            #OutputHandler / RealtimeOutput: miért kell ebből kettő, melyiknek mi a célja?
            #redactor és converter esetén a maradék UI-k jó helyen vannak-e, miért ott vannak jó helyen, hogyan lehetne jobban?
            #model-view direct information exchange van benne? ha igen, az nem jó, átírandó; model legyen kövérebb, a presenter csak közvetítő legyen, inkább itt legyen UI
            #ChatGPT: "sorrend: 1. initialize View, View initializes Presenter, add presenter to view, presenter initializes            
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

        self.form.choose_input_button = self.form.add(npyscreen.ButtonPress, name="Choose input file")
        self.form.choose_input_button.whenPressed = self.choose_input_file
        self.form.input_file_display = self.form.add(npyscreen.FixedText, name="Input file:")

        self.form.choose_output_button = self.form.add(npyscreen.ButtonPress, name="Choose output file")
        self.form.choose_output_button.whenPressed = self.choose_output_file
        self.form.output_file_display = self.form.add(npyscreen.FixedText, name="Output file:")

    def choose_input_file(self):
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='input')
        form.edit()
        self.form.input_file = form.selected_file
        self.form.converter.update_visibility()

    def choose_output_file(self):
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='output')
        form.edit()
        self.form.output_file = form.selected_file
        self.form.converter.update_visibility()
        self.form.redactor.update_visibility()

class ChooseFileForm(npyscreen.ActionForm):
    class ValidationResult(NamedTuple):
        valid: bool
        message: str = None
    
    def __init__(self, *args, mode='input', **kwargs):
        self.mode = mode
        super().__init__(*args, **kwargs)
    
    def create(self):
        self.file_widget = self.add(npyscreen.TitleFilename, name="Choose {} file:".format(self.mode),
                                     select_dir=False, must_exist=True,
                                     mask=WhisperConverter.accepted_extensions if self.mode == 'input' else "*.txt")
        self.add(npyscreen.FixedText, value="Press TAB to browse files from the directory entered (ending with \\)", editable=False)
        self.selected_file = None
    
    @staticmethod    
    def validate_output_file(filename: str)-> bool: 
        if os.path.exists(filename):
            notify_result = npyscreen.notify_ok_cancel("The output file {} already exists. If you press 'Convert', the file will be overwritten. Press Cancel if you don't want this.".format(filename), title="Warning")
            if notify_result == False:
                return False
            else:
                if not os.access(filename, os.W_OK):
                    npyscreen.notify_confirm("The output file {} is not writable. Please choose a different file or check permissions.".format(filename), title="Error")
                    return False
        else:
            parent_directory = os.path.dirname(filename)
            if not os.access(parent_directory, os.W_OK):
                npyscreen.notify_confirm("The output file's parent directory {} is not writable. Please choose a different file or check permissions.".format(parent_directory), title="Error")
                return False
        return True   
    
    @staticmethod
    def is_extension_accepted(filename: str) -> bool:
        _, file_ext = os.path.splitext(filename)
        file_ext = f"*{file_ext}" 
        return file_ext in WhisperConverter.accepted_extensions_list
    
    def is_length_below_limit(self, filename: str)-> Tuple[bool, str]:
        if os.path.getsize(filename) < WhisperConverter.accepted_filesize:
            return True, filename
        else:
            file_size_actual = os.path.getsize(filename)
            file_size_in_MB = int(file_size_actual / 1024 ** 2)
            max_file_size = int(WhisperConverter.accepted_filesize / 1024 ** 2)
            npyscreen.notify_confirm("The input file size {} MB is longer than {} MB.".format(file_size_in_MB, max_file_size), title="Error")
            notify_result = npyscreen.notify_ok_cancel("Shall I split the input file {} into the necessary chunk sizes and process the chunks?".format(filename))
            if notify_result==False:
                return False
            else:                
                chunks = split_files.split_audio(filename, WhisperConverter.accepted_filesize)
                if not os.access(filename, os.W_OK):
                        npyscreen.notify_confirm("I cannot write the split files to the directory of the input file {}, because the directory is not writable. Please choose a different file or check permissions.".format(filename), title="Error")
                        return False
                for i, chunk in enumerate(chunks):
                    filename_root, file_ext = os.path.splitext(filename)
                    chunk.export(f"{filename_root}_{i}{file_ext}", format=file_ext[1:])
                split_files_processed = True
            return True, filename
        
    @staticmethod
    def validate_input_file(filename: str)-> bool: 
        if ChooseFileForm.is_extension_accepted(filename):            
            if os.path.exists(filename):        
                return True            
            npyscreen.notify_confirm("The input file {} does not exist.".format(filename), title="Error")
            return False
        else:
            npyscreen.notify_confirm("The input file extension {} is not accepted. Please convert it to one of the accepted formats: {}.".format(filename, WhisperConverter.accepted_extensions), title="Error")
            return False
        
    def on_ok(self):
        self.selected_file = self.file_widget.value
        main_form=self.parentApp.getForm("MAIN")
            
        if self.mode == 'input':
            if ChooseFileForm.validate_input_file(self.selected_file):                    
                    is_length_below, new_filename = self.is_length_below_limit(self.selected_file)
                    if is_length_below:
                        self.selected_file = new_filename
                        main_form.input_file = self.selected_file
                        self.parentApp.setNextForm("MAIN")
                        main_form.input_file_display.value = self.selected_file
                        main_form.input_file_display.update()
            else:
                self.parentApp.setNextForm("MISSING_FILE")
        elif self.mode == 'output':
            if ChooseFileForm.validate_output_file(self.selected_file):
                main_form.output_file = self.selected_file
                main_form.output_file_display.value = self.selected_file
                main_form.output_file_display.update()
                self.parentApp.setNextForm("MAIN")
            else:
                self.parentApp.setNextForm("MISSING_FILE")
                                
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")

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
        self.form.realtime_output = self.form.add(RealtimeOutput, name="Output:", output_queue=self.output_queue, rely=15, relx=1, max_height=10, max_width=70)
        threading.Thread(target=self.update_output).start()

    def update_output(self):
        while self.periodic_update:
            self.form.realtime_output.update_output()
            time.sleep(0.1)

    def stop_periodic_update(self):
        self.periodic_update = False
        
class RealtimeOutput(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Pager

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

class CustomStdout:
    def write(self, s):
        if s != '\n':
            output_queue.put(s)
        sys.__stdout__.write(s)

    def flush(self):
        sys.__stdout__.flush()    
'''

if __name__ == "__main__":
    app = MyApp()
    app.run()