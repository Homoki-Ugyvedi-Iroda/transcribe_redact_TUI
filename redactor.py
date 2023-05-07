import datetime
from redact_text_w_openAI import OpenAIRedactor
import util
import npyscreen
import main
import os

MAX_TOKEN_LENGTHS = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
}     

current_model_config = "gpt-4"
token_max_length = MAX_TOKEN_LENGTHS[current_model_config]
ratio_of_total_max_prompt = 0.5

class RedactorView(main.BaseView, main.ViewInterface):
    def __init__(self, form, api_key):
        super().__init__(form)
        self.form = form
        self.api_key = api_key 
        self.presenter = RedactorPresenter(form, self)

    def create(self):
        self.form.redact_button = self.form.add(npyscreen.ButtonPress, name="Redact", hidden=True)
        self.form.redact_button.whenPressed = self.on_redact
    
    def on_redact(self):
        self.presenter.handle_redaction()

class RedactorModel:
    def __init__(self, view: RedactorView):
        self.view = view
        
    def redact(self, output_file: str, apikey: str, current_model_config: str, token_max_length: int, ratio_of_total_max_prompt: float) -> str:
        text = ''
        with open(output_file, 'r') as file:
            text = file.read()
        
        chunks = util.create_chunks(text, int(ratio_of_total_max_prompt * token_max_length))
        self.view.display_message("Redaction started ... A response could take up to two minutes per chunk. Number of chunks: {}".format(len(chunks)))
        redacted_text_list = []

        for i, chunk in enumerate(chunks, start=1):            
            start_time = datetime.datetime.now()
            self.view.output_queue.put("{:.2f}. chunk, started: {}".format(i, start_time.strftime("%H:%M:%S")))
            redacted_chunk = OpenAIRedactor(chunk, apikey, current_model_config, int((1 - ratio_of_total_max_prompt) * token_max_length) - 1)
            end_time = datetime.datetime.now()
            time_difference = end_time - start_time
            if redacted_chunk is None:
                redacted_chunk = ""
            redacted_text_list.append(redacted_chunk)
            self.view.output_queue.put(f"[Redacted chunk: [{redacted_chunk[:100]}]")
            self.view.output_queue.put("{:.2f}. chunk processing time: {}".format(i, time_difference))

        redacted_text = " ".join(redacted_text_list)
        return redacted_text
    
class RedactorPresenter:
    def __init__(self, view: RedactorView):
        self.view = view
        self.model = RedactorView(view)
        
    def handle_redaction(self): 
        output_file = self.view.form.output_file_display.value       
        start_time = datetime.datetime.now()
        redacted_text = self.model.redact(output_file, self.apikey, current_model_config, token_max_length, ratio_of_total_max_prompt) 
        self._write_redacted_file(output_file=output_file, redacted_text=redacted_text)
        self.view.display_message_confirm("Redaction complete!", title="Success")
       
    def _write_redacted_file(self, output_file: str, redacted_text: str):
        output_dir, output_filename = os.path.split(output_file)
        redacted_filename = "redacted_" + output_filename
        redacted_output_file = os.path.join(output_dir, redacted_filename)

        with open(redacted_output_file, "w", encoding="utf-8") as file:
            file.write(redacted_text)
    