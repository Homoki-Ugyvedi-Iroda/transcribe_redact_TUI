import datetime
from redact_text_w_openAI import OpenAIRedactor
import util
import npyscreen
from main import BaseView
from main import ViewInterface
import os

MAX_TOKEN_LENGTHS = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
}     

current_model_config = "gpt-4"
token_max_length = MAX_TOKEN_LENGTHS[current_model_config]
ratio_of_total_max_prompt = 0.5

class RedactorView(BaseView, ViewInterface):
    def __init__(self, form, api_key):
        super().__init__(form)
        self.form = form
        self.api_key = api_key 
        self.presenter = RedactorPresenter(self)

    def create(self):
        self.form.redact_button = self.form.add(npyscreen.ButtonPress, name="Redact", hidden=True, rely=7, relx=13, max_height=1, max_width=10)
        self.form.redact_button.whenPressed = self.on_redact
    
    def on_redact(self):
        self.presenter.handle_redaction()
        
    def update_visibility(self, visible: bool=None):
        if visible is not None:
            self.form.redact_button.hidden = not visible
        else:            
            if self.form.output_file is not None:
                self.form.redact_button.hidden = False
            else:
                self.form.redact_button.hidden = True
        self.form.redact_button.update()
        self.form.display()
class RedactorModel:
    def __init__(self, view: RedactorView):
        self.view = view
        
    def redact(self, output_file: str, apikey: str, current_model_config: str, token_max_length: int, ratio_of_total_max_prompt: float) -> str:
        if not os.path.exists(output_file):
            self.view.display_message_confirm("The text file {} does not exist. Please choose a new one".format(output_file))
            return ''
        text = ''
        with open(output_file, 'r') as file:
            text = file.read()
        
        chunks = util.create_chunks(text, int(ratio_of_total_max_prompt * token_max_length))
        self.view.display_message_queue("Redaction started ... A response could take up to two minutes per chunk. Number of chunks: {}".format(len(chunks)))
        redacted_text_list = []

        for i, chunk in enumerate(chunks, start=1):            
            start_time = datetime.datetime.now()
            self.view.display_message_queue("{:.2f}. chunk, started: {}".format(i, start_time.strftime("%H:%M:%S")))
            redact_with_OpenAI=OpenAIRedactor(apikey)
            redacted_chunk = redact_with_OpenAI.call_openAi_redact(chunk, current_model_config, int((1 - ratio_of_total_max_prompt) * token_max_length) - 1)
            end_time = datetime.datetime.now()
            time_difference = end_time - start_time
            if redacted_chunk is None:
                redacted_chunk = ""
            redacted_text_list.append(redacted_chunk)
            self.view.display_message_queue(f"[Redacted chunk: [{redacted_chunk[:100]}]")
            self.view.display_message_queue("{:.2f}. chunk processing time: {}".format(i, time_difference))

        redacted_text = " ".join(redacted_text_list)
        return redacted_text
    
class RedactorPresenter:
    def __init__(self, view: RedactorView):
        self.view = view
        self.model = RedactorModel(view)
        
    def handle_redaction(self): 
        output_file = self.view.form.output_file_display.value       
        start_time = datetime.datetime.now()
        redacted_text = self.model.redact(output_file, self.view.api_key, current_model_config, token_max_length, ratio_of_total_max_prompt) 
        if redacted_text == "":
            return
        self._write_redacted_file(output_file=output_file, redacted_text=redacted_text)
        self.view.display_message_confirm("Redaction complete!")
       
    def _write_redacted_file(self, output_file: str, redacted_text: str):
        output_dir, output_filename = os.path.split(output_file)
        redacted_filename = "redacted_" + output_filename
        redacted_output_file = os.path.join(output_dir, redacted_filename)

        with open(redacted_output_file, "w", encoding="utf-8") as file:
            file.write(redacted_text)
    