import npyscreen
import os
import Whisper_convert
import redact_text_w_openAI
import dotenv
import util
import split_files
import sys
import threading
from queue import Queue
import time
from typing import Tuple

#todo: nyelvválasztás, modellválasztás
#initial prompttal kiegészítés!

dotenv.load_dotenv()        
apikey = os.getenv("OPENAI_API_KEY")

MAX_TOKEN_LENGTHS = {
    "gpt-4": 8192,
    "gpt-3.5-turbo": 4096,
}     

current_model_config = "gpt-3.5-turbo"
token_max_length = MAX_TOKEN_LENGTHS[current_model_config]
 
class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Audio to text conversion")
        self.addForm("MISSING_OPENAIAPIKEY", MissingOpenAiApiKey, name="Missing OpenAI API key")

class MainForm(npyscreen.ActionForm):
    def create(self):
        self.input_file = None
        self.output_file = None
        self.choose_input_button = self.add(npyscreen.ButtonPress, name="Choose input file")
        self.choose_input_button.whenPressed = self.choose_input_file
        self.input_file_display = self.add(npyscreen.FixedText, name="Input file:")
        self.choose_output_button = self.add(npyscreen.ButtonPress, name="Choose output file")
        self.choose_output_button.whenPressed = self.choose_output_file
        self.output_file_display = self.add(npyscreen.FixedText, name="Output file:")
        self.convert_button = self.add(npyscreen.ButtonPress, name="Convert", hidden=True)
        self.convert_button.whenPressed = self.on_convert
        self.redact_button = self.add(npyscreen.ButtonPress, name="Redact", hidden=True)
        self.redact_button.whenPressed = self.on_redact        
        self.realtime_output = self.add(RealtimeOutput, name="Output:")
        self.periodic_update = True
        threading.Thread(target=self.update_output).start()
        threading.Thread(target=self.wait_for_conversion).start()
        self.conversion_complete_event = threading.Event()
    
    def update_convert_button_visibility(self):
        if self.input_file_display.value and self.output_file_display.value:
            self.convert_button.hidden = False
        else:
            self.convert_button.hidden = True
        self.convert_button.update()
        self.display()
    
    def update_redact_button_visibility(self):
        if self.output_file_display.value and os.path.exists(self.output_file_display.value):                
            self.redact_button.hidden = False
        else:
            self.redact_button.hidden = True
        self.redact_button.update()
        self.display()
   
    def update_output(self):
        while self.periodic_update:
            self.realtime_output.update_output()
            time.sleep(0.1) 
               
    def on_cancel(self):
        self.periodic_update = False
        self.parentApp.setNextForm(None)
        self.parentApp.setNextForm(None)
    
    def choose_input_file(self):
        form = ChooseFileForm(parentApp=self.parentApp, mode='input')
        form.edit()
        self.input_file = form.selected_file
        self.update_convert_button_visibility()
        
    def choose_output_file(self):
        form = ChooseFileForm(parentApp=self.parentApp, mode='output')
        form.edit()
        self.output_file = form.selected_file
        self.update_convert_button_visibility()
        self.update_redact_button_visibility()    
    
    def on_convert(self):
        input_file = self.input_file_display.value
        output_file = self.output_file_display.value        
        output_queue.put("Starting conversion... \n")
        self.conversion_thread = OutputThread(target=Whisper_convert.whisper_convert, args=(input_file, output_file), event=self.conversion_complete_event)
        self.display()
        
    def conversion_complete(self):
        #npyscreen.notify_confirm("Conversion complete!", title="Success")        
        output_queue.put("Conversion complete! \n")
        self.redact_button.hidden = False
        self.redact_button.update()
        self.display()
    
    def wait_for_conversion(self):
        while self.periodic_update:
            if self.conversion_complete_event.is_set():
                self.conversion_complete_event.clear()
                self.conversion_complete()
            time.sleep(0.1)
            
    def on_redact(self):
        output_file = self.output_file_display.value
        
        if not apikey:
            self.parentApp.setNextForm("MISSING_OPENAIAPIKEY")               
        text = ''        
        with open(output_file, 'r') as file:
            text = file.read()
        chunks = util.create_chunks(text, token_max_length)
        output_queue.put("Redaction started ... A response could take up to two minutes per chunk. Number of chunks: {}".format(len(chunks)))
        redacted_text_list = []
        for i, chunk in enumerate(chunks, start=1):
            start_time = time.time()
            start_time_local = time.ctime(start_time)
            output_queue.put("{:.2f}. chunk, started: {}".format(i, start_time_local))
            next_chunk=redact_text_w_openAI.call_openAi_redact(chunk, apikey, current_model_config)
            end_time = time.time()
            time_difference = end_time - start_time
            if next_chunk is None:
                next_chunk = ""
            redacted_text_list.append(next_chunk)
            output_queue.put("[Redacted chunk: [{}]".format(next_chunk))
            output_queue.put("{:.2f}. chunk processing time: {}".format(i, time_difference))
        redacted_text = " ".join(redacted_text_list)
        output_dir, output_filename = os.path.split(output_file)
        redacted_filename = "redacted_" + output_filename
        redacted_output_file = os.path.join(output_dir, redacted_filename)
        with open(redacted_output_file, "w", encoding="utf-8") as file:
	        file.write(redacted_text)

class ChooseFileForm(npyscreen.ActionForm):
    def __init__(self, *args, mode='input', **kwargs):
        self.mode = mode
        super().__init__(*args, **kwargs)
    
    def create(self):
        self.file_widget = self.add(npyscreen.TitleFilename, name="Choose {} file:".format(self.mode),
                                     select_dir=False, must_exist=True,
                                     mask=Whisper_convert.accepted_extensions if self.mode == 'input' else "*.txt")
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
        return file_ext in Whisper_convert.accepted_extensions_list
    
    def is_length_below_limit(self, filename: str)-> Tuple[bool, str]:
        if os.path.getsize(filename) < Whisper_convert.accepted_filesize:
            return True, filename
        else:
            file_size_actual = os.path.getsize(filename)
            file_size_in_MB = int(file_size_actual / 1024 ** 2)
            max_file_size = int(Whisper_convert.accepted_filesize / 1024 ** 2)
            npyscreen.notify_confirm("The input file size {} MB is longer than {} MB.".format(file_size_in_MB, max_file_size), title="Error")
            notify_result = npyscreen.notify_ok_cancel("Shall I split the input file {} into the necessary chunk sizes and process the first chunk?".format(filename))
            if notify_result==False:
                return False            
            chunks = split_files.split_audio(filename, Whisper_convert.accepted_filesize)
            if not os.access(filename, os.W_OK):
                    npyscreen.notify_confirm("I cannot write the split files to the directory of the input file {}, because the directory is not writable. Please choose a different file or check permissions.".format(filename), title="Error")
                    return False
            for i, chunk in enumerate(chunks):
                filename_root, file_ext = os.path.splitext(filename)
                chunk.export(f"{filename_root}_{i}{file_ext}", format=file_ext[1:])
            filename = f"{filename_root}_0{file_ext}"            
            return True, filename
        return True
    
    @staticmethod
    def validate_input_file(filename: str)-> bool: 
        if ChooseFileForm.is_extension_accepted(filename):            
            if os.path.exists(filename):        
                return True            
            npyscreen.notify_confirm("The input file {} does not exist.".format(filename), title="Error")
            return False
        else:
            npyscreen.notify_confirm("The input file extension {} is not accepted. Please convert it to one of the accepted formats: {}.".format(filename, Whisper_convert.accepted_extensions), title="Error")
            return False
        
    def on_ok(self):
        selected_file = self.file_widget.value
        if self.mode == 'input':
            if ChooseFileForm.validate_input_file(selected_file):                    
                    is_length_below, new_filename = self.is_length_below_limit(selected_file)
                    if is_length_below:
                        selected_file = new_filename
                        self.parentApp.getForm("MAIN").input_file = selected_file
                        self.parentApp.setNextForm("MAIN")
                        self.parentApp.getForm("MAIN").input_file_display.value = selected_file
                        self.parentApp.getForm("MAIN").input_file_display.update()
            else:
                self.parentApp.setNextForm("MISSING_FILE")
        elif self.mode == 'output':
            if ChooseFileForm.validate_output_file(selected_file):
                self.parentApp.getForm("MAIN").output_file = selected_file
                self.parentApp.getForm("MAIN").output_file_display.value = selected_file
                self.parentApp.getForm("MAIN").output_file_display.update()
                self.parentApp.setNextForm("MAIN")
            else:
                self.parentApp.setNextForm("MISSING_FILE")
                                
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")
    
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
        
class RealtimeOutput(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Pager

    def update(self, *args, **keywords):
        super(RealtimeOutput, self).update(*args, **keywords)

    def update_output(self):
        while not output_queue.empty():
            message = output_queue.get()
            self.values.append(message)
            self.display()

output_queue = Queue()

class OutputThread(threading.Thread):
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

     
if __name__ == "__main__":
    app = MyApp()
    app.run()