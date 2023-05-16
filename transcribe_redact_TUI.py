import npyscreen
import os
from dotenv import load_dotenv, set_key
import sys
import threading
from queue import Queue
import time
from typing import Protocol
import ui_const
from lang_model_chooser import LanguageModeHandler
        

class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        import lang_model_chooser
        from converter import SetTranscriptionPrompt
        from redactor import SetRedactPrompt
        self.addForm("MAIN", MainForm, name=ui_const.NAME_MAINFORM_EN)
        self.addForm("MISSING_OPENAIAPIKEY", MissingOpenAiApiKey, name=ui_const.NAME_MISSINGOPENAIKEY_EN)
        self.addForm('CHOOSELANG', lang_model_chooser.ChooseLanguageForm, name=ui_const.NAME_CHOOSELANGUAGE_EN)
        self.addForm('CHOOSEMODEL', lang_model_chooser.ChooseModelForm, name=ui_const.NAME_CHOOSEMODEL_EN)
        self.addForm('INIT_PROMPT', SetTranscriptionPrompt, name=ui_const.NAME_INITIALPROMPT_EN)
        self.addForm('REDACT_PROMPT', SetRedactPrompt, name=ui_const.NAME_REDACTPROMPT_EN)
        if not os.getenv("OPENAI_API_KEY"):
            self.setNextForm("MISSING_OPENAIAPIKEY")
    
class MainForm(npyscreen.FormBaseNew):
    def create(self):
        from redactor import RedactorView
        from converter import TranscriptionView

        load_dotenv()        
        self.output_queue = Queue()
        self.input_file = None
        self.output_file = None  
        self.did_split = []
        
        self.file_handler = FileHandler(self)
        self.file_handler.create()        
        
        self.converter = TranscriptionView(self)
        self.converter.create()
        
        self.redactor = RedactorView(self, api_key=os.getenv("OPENAI_API_KEY"))
        self.redactor.create()       
        
        self.languagemode = LanguageModeHandler(self)
        self.languagemode.create()
        
        self.cb_cuda = CudaCheckbox(self)
        self.cb_cuda.create()
        
        self.set_tab_order(self.form)
        
        self.output_handler = OutputHandler(self, self.output_queue)
        self.output_handler.create()
                
        y, x = self.useable_space()
        self.exit_button = self.add(npyscreen.ButtonPress, name=ui_const.NAME_EXITBUTTON_EN, rely=y-3, relx=x-10)
        self.exit_button.whenPressed = self.exit_application
    
    def set_tab_order(self, form):
        self.form = form
        self.form.choose_input_button.set_next(self.form.choose_output_button)
        self.form.choose_output_button.set_next(self.form.convert_button)
        self.form.convert_button.set_next(self.form.transcription_prompt_button)
        self.form.transcription_prompt_button.set_next(self.form.redact_button)
        self.form.redact_button.set_next(self.form.languagemode.language_button)
        self.form.language.language_button.set_next(self.form.languagemodel.model_button)
        self.form.model.model_button.name.set_next(self.form.cuda_cb)
        self.form.cuda_cb.set_next(self.form.cb_gpt4)
        self.form.cb_gpt4.set_next(self.form.set_max_token_length_button)   
       
    
    def exit_application(self):
        split_files_list = self.parentApp.getForm("MAIN").did_split
        if len(split_files_list) > 0:
            result = npyscreen.notify_yes_no(ui_const.MSG_DELETEUPONEXIT_EN)
            for filename in split_files_list:
                try:
                    os.remove(filename)
                except:
                    pass                
        self.output_handler.stop_periodic_update()
        self.parentApp.switchForm(None)

class FileHandler:
    def __init__(self, form):
        self.form = form

    def create(self):
        self.form.choose_input_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_AUDIOFILEBUTTON_EN)
        self.form.choose_input_button.whenPressed = self.choose_input_file
        self.form.input_file_display = self.form.add(npyscreen.FixedText, name=ui_const.NAME_AUDIOFILEDISPLAY_EN, editable=False)

        self.form.choose_output_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_TEXTFILEBUTTON_EN)
        self.form.choose_output_button.whenPressed = self.choose_output_file
        self.form.output_file_display = self.form.add(npyscreen.FixedText, name=ui_const.NAME_TEXTFILEDISPLAY_EN, editable=False)
    
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

class CudaCheckbox:    
    def create(self):        
        checkbox_value_str = os.getenv("CUDA")
        if checkbox_value_str == "True":
            checkbox_value_bool = True
        else:
            checkbox_value_bool = False
        self.cuda_cb = self.add(npyscreen.Checkbox, name=ui_const.NAME_CUDACBOX_EN, value=checkbox_value_bool, help = ui_const.HELP_TRYCUDA_EN, relx=4, max_width=23)
        self.cuda_cb.whenToggled = self.update_cuda_cb_save_to_env
    
    def update_cuda_cb_save_to_env(self):
        if self.cuda_cb.value:
            set_key(".env", "CUDA", "True")
        else:
            set_key(".env", "CUDA", "False")
    
class MissingOpenAiApiKey(npyscreen.ActionForm):
    def create(self):
        self.add(npyscreen.TitleText, name = ui_const.NAME_MISSINGOPENAIKEYDISPLAY_EN)
    def on_ok(self):
        apikey = self.get.widget(0).value
        if not apikey or apikey.strip() == "":
            self.parentApp.setNextForm("MISSING_OPENAIAPIKEY")
        else:
            set_key('.env', "OPENAI_API_KEY", apikey)
        
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

class RealtimeOutput(npyscreen.BoxTitle):   
    def __init__(self, *args, output_queue=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.output_queue = output_queue
        self.value = ""
        self.update()        
    
    def update(self, *args, **keywords):
        super(RealtimeOutput, self).update(*args, **keywords)

    def update_output(self):
        while not self.output_queue.empty():
            message = self.output_queue.get()
            if message:
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