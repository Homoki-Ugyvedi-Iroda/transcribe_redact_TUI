import npyscreen
import os
from dotenv import load_dotenv, set_key
import sys
import threading
from queue import Queue
import time
import ui_const
from misc_gui_setter import LanguageModelHandler, CudaCheckbox

class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        import misc_gui_setter
        from locale import setlocale, LC_ALL
        from transcriptor import SetTranscriptionPrompt
        from redactor import SetRedactPrompt, SetGptMaxTokenLength
        setlocale(LC_ALL, '')
        
        self.addForm("MAIN", MainForm, name=ui_const.NAME_MAINFORM_EN)
        self.addForm("MISSING_OPENAIAPIKEY", MissingOpenAiApiKey, name=ui_const.NAME_MISSINGOPENAIKEY_EN)
        self.addForm("CHOOSELANG", misc_gui_setter.ChooseLanguageForm, name=ui_const.NAME_CHOOSELANGUAGE_EN)
        self.addForm("CHOOSEMODEL", misc_gui_setter.ChooseModelForm, name=ui_const.NAME_CHOOSEMODEL_EN)
        self.addForm("INIT_PROMPT", SetTranscriptionPrompt, name=ui_const.NAME_INITIALPROMPT_EN)
        self.addForm("REDACT_PROMPT", SetRedactPrompt, name=ui_const.NAME_REDACTPROMPT_EN)
        self.addForm("MAXTOKENLENGTH", SetGptMaxTokenLength, name=ui_const.NAME_GPTMAXLENGTHINPUT_EN)
        if not os.getenv("OPENAI_API_KEY"):
            self.setNextForm("MISSING_OPENAIAPIKEY")

class MainForm(npyscreen.FormBaseNew):
            
    def create(self):
        from redactor import RedactorView, Gpt4CheckBox, GptMaxTokenLengthButton
        from transcriptor import TranscriptionView
        from file_handler import FileHandler

        load_dotenv()        
        self.output_queue = Queue()
        self.input_file = None
        self.output_file = None  
        self.did_split = []
        
        self.file_handler = FileHandler(self)
        self.file_handler.create()        
        
        self.transcriptor = TranscriptionView(self)
        self.transcriptor.create()
        
        self.redactor = RedactorView(self, api_key=os.getenv("OPENAI_API_KEY"))
        self.redactor.create()  

        self.languagemodel = LanguageModelHandler(self)
        self.languagemodel.create()
        
        self.cb_cuda = CudaCheckbox(self)
        self.cb_cuda.create()
        self.cuda_cb = self.cb_cuda.cuda_cb
        
        self.gpt4_cb = Gpt4CheckBox(self)
        self.gpt4_cb.create()        
        
        self.current_model_config = Gpt4CheckBox.get_model_from_gpt_4_env()
        
        self.cb_gpt_max_token_length = GptMaxTokenLengthButton(self)
        self.cb_gpt_max_token_length.create()
        
        self.output_handler = OutputHandler(self, self.output_queue)
        self.output_handler.create()          
                
        y, x = self.useable_space()
        self.exit_button = self.add(npyscreen.ButtonPress, name=ui_const.NAME_EXITBUTTON_EN, rely=y-3, relx=x-10)
        self.exit_button.whenPressed = self.exit_application    
    
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
   
            
class OutputHandler:
    def __init__(self, form, output_queue):
        self.form = form
        self.periodic_update = True
        self.output_queue = output_queue
        
    def create(self):
        self.form.scrolls_to_last_output = self.form.add(OutputBufferPager, name=ui_const.NAME_OUTPUT_EN, relx=1, rely=10, max_height=18, editable=False, output_queue=self.output_queue)
        
        threading.Thread(target=self.update_output).start()

    def update_output(self):
        while self.periodic_update:
            self.form.scrolls_to_last_output.update_output()
            time.sleep(1)

    def stop_periodic_update(self):
        self.periodic_update = False     
            
class OutputBufferPager(npyscreen.BufferPager):
    def __init__(self, *args, output_queue = None, **kwargs):
        from collections import deque
        super(OutputBufferPager, self).__init__(*args, **kwargs)
        self.values = deque(maxlen=18)
        self.output_queue = output_queue      
    
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

class MissingOpenAiApiKey(npyscreen.ActionForm):
    def create(self):
        self.api_key_input = self.add(npyscreen.TitleText, name = ui_const.NAME_MISSINGOPENAIKEYDISPLAY_EN)
    def on_ok(self):
        apikey = self.api_key_input.value
        if not apikey or apikey.strip() == "":
            self.parentApp.setNextForm("MISSING_OPENAIAPIKEY")
        else:
            set_key('.env', "OPENAI_API_KEY", apikey)
        self.parentApp.setNextForm("MAIN")
        
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")  

if __name__ == "__main__":
    app = MyApp()
    app.run()