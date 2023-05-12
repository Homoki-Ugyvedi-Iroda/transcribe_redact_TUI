from main import BaseView
from main import ViewInterface
from main import OutputThread
from contextlib import redirect_stdout

class ConverterView(BaseView, ViewInterface):

    def __init__(self, form):
        super().__init__(form)
        self.presenter = ConverterPresenter(self)

    def create(self):
        from npyscreen import ButtonPress
        self.form.convert_button = self.form.add(ButtonPress, name="Convert", hidden=True, rely=7, relx=1, max_height=1, max_width=10)
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
        
    def convert(self, input_file: str, output_file: str):
        import Whisper_convert
        self.wh_converter = Whisper_convert.WhisperConverter(self.view.form.output_queue)
        self.wh_converter.whisper_convert(input_file, output_file)

class ConverterPresenter:
    def __init__(self, view: ConverterView):
        self.view = view
        self.model = ConverterModel(view)
        
    def handle_conversion(self):
        from main import CustomStdout
        input_file = self.view.form.input_file_display.value
        output_file = self.view.form.output_file_display.value

        if input_file and output_file:
            self.view.display_message_queue("Starting conversion... \n")
            with redirect_stdout(CustomStdout(self.view.form.output_queue)):
                self.model.convert(input_file, output_file)
            self.view.display_message_queue("Conversion complete! \n")

