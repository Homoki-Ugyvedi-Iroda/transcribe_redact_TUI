from main import BaseView
from main import ViewInterface
from contextlib import redirect_stdout
import ui_const

NAME_TRANSCRIBEBUTTON_EN = "Transcribe"
MSG_STARTTRANSCRIBE_EN = "Starting transcription... \n"
MSG_TRANSCRIPTIONFINISHED_EN = "Conversion complete! \n"

class ConverterView(BaseView, ViewInterface):

    def __init__(self, form):
        super().__init__(form)
        self.presenter = ConverterPresenter(self)

    def create(self):
        from npyscreen import ButtonPress
        self.form.convert_button = self.form.add(ButtonPress, name=NAME_TRANSCRIBEBUTTON_EN, hidden=True, rely=7, relx=1, max_height=1, max_width=10)
        self.form.convert_button.whenPressed = self.on_convert

    def update_visibility(self, visible: bool=None):
        main_form=self.form.parentApp.getForm("MAIN")
        if visible is not None:
            self.form.convert_button.hidden = not visible
        else:            
            if main_form.input_file is not None and main_form.output_file is not None:
                self.form.convert_button.hidden = False
            else:
                self.form.convert_button.hidden = True
        self.form.convert_button.update()
        self.form.display()
        
    def on_convert(self):
        self.presenter.handle_conversion()
        
class ConverterModel:
    def __init__(self, view: ConverterView):
        self.view = view
    
    def get_language(self) -> str:
        main_form=self.form.parentApp.getForm("MAIN")
        lang_name = main_form.language.language_button.name
        if not lang_name:
            return ""
        else:
            return lang_name.split(" | ")[-1].strip().lower()
    def get_model(self) -> str:
        main_form=self.form.parentApp.getForm("MAIN")
        model_name = main_form.model.model_button.name
        if not model_name or model_name==ui_const.NAME_DETECTLANGUAGEVALUE_EN:
            return ""
        else:
            return model_name.split(" ")[0].lower()
    def get_initial_prompt(self) -> str:
        main_form=self.form.parentApp.getForm("MAIN")
        initial_prompt = main_form.initial_prompt
        return initial_prompt
    
    def convert(self, input_file: str, output_file: str):
        import Whisper_convert
        self.wh_converter = Whisper_convert.WhisperConverter(self.view.form.output_queue)
        self.wh_converter.whisper_convert(input_file, output_file, language=self.get_language, model_name=self.get_model)

class ConverterPresenter:
    def __init__(self, view: ConverterView):
        self.view = view
        self.model = ConverterModel(view)
        
    def handle_conversion(self):
        from main import CustomStdout
        input_file = self.view.form.input_file_display.value
        output_file = self.view.form.output_file_display.value

        if input_file and output_file:
            self.view.display_message_queue(MSG_STARTTRANSCRIBE_EN)
            with redirect_stdout(CustomStdout(self.view.form.output_queue)):
                self.model.convert(input_file, output_file)
            self.view.display_message_queue(MSG_TRANSCRIPTIONFINISHED_EN)

