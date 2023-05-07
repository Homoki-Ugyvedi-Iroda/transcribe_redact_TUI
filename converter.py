import npyscreen
import Whisper_convert
import main

class ConverterView(main.BaseView, main.ViewInterface):
    def __init__(self, form):
        super().__init__(form)
        self.presenter = ConverterPresenter(form, self)

    def create(self):
        self.form.convert_button = self.form.add(npyscreen.ButtonPress, name="Convert", hidden=True)
        self.form.convert_button.whenPressed = self.on_convert

    def update_visibility(self, visible: bool):
        self.form.convert_button.hidden = not visible
        self.form.convert_button.update()
        self.form.display()    
        
    def on_convert(self):
        self.presenter.handle_conversion()
        
class ConverterModel:
    def __init__(self, view: ConverterView):
        self.view = view
        
    def convert(self, input_file: str, output_file: str):
        Whisper_convert.whisper_convert(input_file, output_file)

class ConverterPresenter:
    def __init__(self, view: ConverterView):
        self.view = view
        self.model = ConverterModel(view)
        
    def handle_conversion(self):
        input_file = self.view.form.input_file_display.value
        output_file = self.view.form.output_file_display.value

        if input_file and output_file:
            self.view.display_message_queue("Starting conversion... \n")
            self.model.convert(input_file, output_file)
            self.view.display_message_queue("Conversion complete! \n")
            self.view.form.redactor.update_visibility()
        else:
            self.view.update_visibility(False)
    