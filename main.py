import npyscreen
import logging
import os
import dotenv
import sys
import threading
from queue import Queue
import time
from typing import Protocol
import ui_const

#todo:  
        #nyelvválasztás és modellválasztás: tesztelés a végrehajtásra
        #teszt: AutoScrollPager jól működik?
        #miért nem tudok visszalépni RealtimeOutputon?
      
        #PySimpleGUI változat        
        #general OS/IO error handling
        #unittests?
        #helpek megírása és ellenőrzése, hogy jó helyen ugranak-e föl
        
        #kilépéskor takarítás: törlése a szétszedett vagy átalakított fájloknak?
        #logging törlése        
        #renaming "main.py", deployment, upload

logging.basicConfig(
    filename='test_whisper_w_GPT_log_file.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s')

class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        import lang_model_prompt_chooser
        self.addForm("MAIN", MainForm, name=ui_const.NAME_MAINFORM_EN)
        self.addForm("MISSING_OPENAIAPIKEY", MissingOpenAiApiKey, name=ui_const.NAME_MISSINGOPENAIKEY_EN)
        self.addForm('CHOOSELANG', lang_model_prompt_chooser.ChooseLanguageForm, name=ui_const.NAME_CHOOSELANGUAGE_EN)
        self.addForm('CHOOSEMODEL', lang_model_prompt_chooser.ChooseModelForm, name=ui_const.NAME_CHOOSEMODEL_EN)
        self.addForm('INIT_PROMPT', lang_model_prompt_chooser.SetInitialPrompt, name=ui_const.NAME_INITIALPROMPT_EN)
        if not os.getenv("OPENAI_API_KEY"):
            self.setNextForm("MISSING_OPENAIAPIKEY")
    
class MainForm(npyscreen.FormBaseNew):
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
        
        self.lang_model_creator()  
        self.initial_prompt_creator()
        
        self.output_handler = OutputHandler(self, self.output_queue)
        self.output_handler.create()
                
        y, x = self.useable_space()
        self.exit_button = self.add(npyscreen.ButtonPress, name=ui_const.NAME_EXITBUTTON_EN, rely=y-3, relx=x-10)
        self.exit_button.whenPressed = self.exit_application
        
       
    def initial_prompt_creator(self):
        from lang_model_prompt_chooser import SetInitialPrompt, InitialPromptButton
        self.initial_prompt = ""        
        self.initial_prompt_setter = SetInitialPrompt(self)
        self.initial_prompt_setter.create()
        self.initial_prompt_button = InitialPromptButton(self)
        self.initial_prompt_button.create()        

    def lang_model_creator(self):
        from lang_model_prompt_chooser import ChooseLanguageButton, ChooseModelButton
        self.language = ChooseLanguageButton(self)
        self.language.create()
        self.model = ChooseModelButton(self)
        self.model.create()
    
    def exit_application(self):
        self.output_handler.stop_periodic_update()
        self.parentApp.switchForm(None)
        
class FileHandler:
    def __init__(self, form):
        self.form = form

    def create(self):
        self.form.choose_input_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_AUDIOFILEBUTTON_EN)
        self.form.choose_input_button.whenPressed = self.choose_input_file
        self.form.input_file_display = self.form.add(npyscreen.FixedText, name=ui_const.NAME_AUDIOFILEDISPLAY_EN)

        self.form.choose_output_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_TEXTFILEBUTTON_EN)
        self.form.choose_output_button.whenPressed = self.choose_output_file
        self.form.output_file_display = self.form.add(npyscreen.FixedText, name=ui_const.NAME_TEXTFILEDISPLAY_EN)
    
    def choose_input_file(self):
        from choose_file import ChooseFileForm
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='input', help=ui_const.HELP_AUDIOFILEDISPLAY_EN)
        form.edit()
        self.form.input_file = form.selected_file
        self.form.converter.update_visibility()

    def choose_output_file(self):
        from choose_file import ChooseFileForm        
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='output', help=ui_const.HELP_TEXTFILEDISPLAY_EN)
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
        self.add(npyscreen.TitleText, name = ui_const.NAME_MISSINGOPENAIKEYDISPLAY_EN)
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
        self.form.realtime_output = self.form.add(RealtimeOutput, name=ui_const.NAME_OUTPUT_EN, output_queue=self.output_queue, relx=1, rely=9, max_height=18)
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