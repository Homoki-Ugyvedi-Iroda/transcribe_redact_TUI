from transcribe_redact_TUI import BaseView
from transcribe_redact_TUI import ViewInterface
from contextlib import redirect_stdout
from npyscreen import ActionPopup, ButtonPress, MultiLineEdit
import ui_const
import util
import os
from dotenv import set_key


MSG_STARTTRANSCRIBE_EN = "Starting transcription... \n"
MSG_TRANSCRIPTIONFINISHED_EN = "Conversion complete! \n"
MSG_CONVERTINGMULTIPLE_EN = "Converting multiple files ({})... \n"
MSG_CONVERTINGSINGLE_EN = "Converting file: ({})... \n"

class TranscriptionView(BaseView, ViewInterface):

    def __init__(self, form):
        super().__init__(form)
        self.presenter = TranscriptionPresenter(self)

    def create(self):
        self.form.transcriptor_button = self.form.add(ButtonPress, name=ui_const.NAME_TRANSCRIBEBUTTON_EN, hidden=True, rely=6, relx=2, max_height=1)
        self.form.transcriptor_button.whenPressed = self.on_transcription
        self.initial_prompt = ""
        self.transcription_prompt_button = TranscriptionPromptButton(self.form)
        self.transcription_prompt_button.create()
        self.initial_prompt_setter = SetTranscriptionPrompt(self.form)
        self.initial_prompt_setter.create()


    def update_visibility(self, visible: bool=None):
        main_form=self.form.parentApp.getForm("MAIN")
        if visible is not None:
            self.form.transcriptor_button.hidden = not visible
        else:            
            if main_form.input_file is not None and main_form.output_file is not None:
                self.form.transcriptor_button.hidden = False
            else:
                self.form.transcriptor_button.hidden = True
        self.form.transcriptor_button.update()
        self.form.display()
        
    def on_transcription(self):
        self.presenter.handle_transcription()
        
class TranscriptionModel:
    def __init__(self, view: TranscriptionView):
        self.view = view
    
    def get_language(self) -> str:
        main_form=self.view.form.parentApp.getForm("MAIN")
        lang_name = main_form.language.language_button.name
        if not lang_name or lang_name==ui_const.NAME_DETECTLANGUAGEVALUE_EN:
            return ""
        else:
            return lang_name.split(" | ")[-1].strip().lower()
    
    def get_model(self) -> str:
        main_form=self.view.form.parentApp.getForm("MAIN")
        model_name = main_form.model.model_button.name
        if not model_name:
            return ""
        else:
            return model_name.split(" ")[0].lower()
        
    def get_initial_prompt(self) -> str:
        initial_prompt = self.view.initial_prompt
        return initial_prompt
    
    def get_cuda(self) -> bool:
        if self.view.form.cuda_cb.value == True:
            return True
        return False 
    
    def transcribe(self, input_file: str, output_file: str):
        import Whisper_transcript
        self.wh_transcriptor = Whisper_transcript.WhisperConverter()
        language=self.get_language()
        model_name=self.get_model()
        initial_prompt=self.get_initial_prompt()
        cuda=self.get_cuda()
        '''max_size = ui_const.ACCEPTED_WHISPER_FILESIZE
                if os.path.getsize(input_file) > max_size:
            if util.check_split_files_presence_under_input_file(input_file, max_size):
                chunk_filenames = util.list_split_files(input_file) #ordered list of files is returned
                self.view.display_message_queue(MSG_CONVERTINGMULTIPLE_EN.format(len(chunk_filenames)))
                for filename in chunk_filenames:
                    self.view.display_message_queue(MSG_CONVERTINGSINGLE_EN.format(os.path.basename(filename)))
                    self.wh_transcriptor.whisper_convert(filename, output_file, language=language, model_name=model_name, initial_prompt=initial_prompt, CUDA=cuda)
        else: 
        '''   #We omitted the size checking code above, because offline Whisper works with 25MB+ files as well. Current limit seems to depend on GPU/CPU etc. so not using it.
        try:            
            self.wh_transcriptor.whisper_convert(input_file, output_file, language=language, model_name=model_name, initial_prompt=initial_prompt, CUDA=cuda)
        except Exception as e:
            self.view.display_message_queue(str(e))

class TranscriptionPresenter:
    def __init__(self, view: TranscriptionView):
        self.view = view
        self.model = TranscriptionModel(view)
        
    def handle_transcription(self):
        from transcribe_redact_TUI import CustomStdout
        input_file = self.view.form.input_file_display.value
        output_file = self.view.form.output_file_display.value      

        if input_file and output_file:
            self.view.display_message_queue(MSG_STARTTRANSCRIBE_EN)
            with redirect_stdout(CustomStdout(self.view.form.output_queue)):
                self.model.transcribe(input_file, output_file)
            self.view.display_message_queue(MSG_TRANSCRIPTIONFINISHED_EN)
        
class TranscriptionPromptButton:
    def __init__(self, form):
        self.form = form
    def create(self):
        selected_value = ui_const.NAME_INITIALPROMPT_EN
        if os.getenv('INIT_PROMPT') is not None:
            selected_value = ui_const.NAME_INITIALPROMPT_EN + "*"
        self.form.transcription_prompt_button = self.form.add(ButtonPress, name=selected_value, rely=6, relx=25)
        self.form.transcription_prompt_button.whenPressed = self.switch_to_initial_prompt_form        
    def switch_to_initial_prompt_form(self):
        self.form.parentApp.switchForm('INIT_PROMPT')    
    
class SetTranscriptionPrompt(ActionPopup):
    def create(self):
        self.add(MultiLineEdit, name = ui_const.NAME_INITIALPROMPTTEXTBOX_EN, begin_entry_at=0, value=os.getenv('INIT_PROMPT'), \
            help = ui_const.HELP_SETINITIALPROMPT_EN, autowrap=True)
        #softwrap/autowrap does not work for some reasons on Win
        
    def on_ok(self):
        set_key('.env', "INIT_PROMPT", util.get_prompt_value_formatted(self.get_widget(0).value))
        self.parentApp.switchFormPrevious()
    
    def on_cancel(self):
        self.initial_prompt  = ""
        self.parentApp.switchFormPrevious()
