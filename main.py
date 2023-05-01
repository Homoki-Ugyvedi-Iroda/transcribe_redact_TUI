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


dotenv.load_dotenv()        
apikey = os.getenv("OPENAI_API_KEY")
        
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
        self.convert_button = self.add(npyscreen.ButtonPress, name="Convert")
        self.convert_button.whenPressed = self.on_convert
        self.redact_button = self.add(npyscreen.ButtonPress, name="Redact", hidden=True)
        self.redact_button.whenPressed = self.on_redact
        self.realtime_output = self.add(RealtimeOutput, name="Output:")
        self.periodic_update = True
        threading.Thread(target=self.update_output).start()
         
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

    def choose_output_file(self):
        form = ChooseFileForm(parentApp=self.parentApp, mode='output')
        form.edit()
        self.output_file = form.selected_file    
    
    def on_convert(self):
        input_file = self.input_file_display.value
        output_file = self.output_file_display.value
        if not input_file or not output_file:
            npyscreen.notify_confirm("Both input and output files must be specified.", title="Error")
            return

        self.conversion_thread = OutputThread(target=Whisper_convert.whisper_convert, args=(input_file, output_file))
        self.conversion_thread.start()
        #Whisper_convert.whisper_convert(input_file, output_file)        
        npyscreen.notify_confirm("Conversion complete!", title="Success")
        self.redact_button.hidden = False
        self.redact_button.update()
        self.display()
    
    def on_redact(self):
        output_file = self.output_file_display.value
        
        if not apikey:
            self.parentApp.setNextForm("MISSING_OPENAIAPIKEY")               
        text = ''        
        with open(output_file, 'r') as file:
            text = file.read()
        chunks = util.create_chunks(text)
        redacted_text_list = list[str]
        for chunk in chunks:
            redacted_text_list.append(redact_text_w_openAI.call_openAi_redact(chunk, apikey))
        redacted_text = " ".join(redacted_text_list)
        with open(str.join("redacted_",output_file), "w", encoding="utf-8") as file:
	        file.write(redacted_text)

class ChooseFileForm(npyscreen.ActionForm):
    def __init__(self, *args, mode='input', **kwargs):
        self.mode = mode
        super().__init__(*args, **kwargs)
    
    def create(self):
        self.file_widget = self.add(npyscreen.TitleFilename, name="Choose {} file:".format(self.mode),
                                     select_dir=False, must_exist=True,
                                     mask=Whisper_convert.accepted_extensions if self.mode == 'input' else "*.txt")
        self.selected_file = None
    
    @staticmethod    
    def validate_output_file(filename: str)-> bool: 
        if os.path.exists(filename):
            notify_result = npyscreen.notify_ok_cancel("The output file {} already exists, it will be overwritten. Please choose a different file or check permissions.".format(filename), title="Warning")
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
    
    @staticmethod
    def is_length_below_limit(filename: str)->bool:
        if os.path.getsize(filename) < Whisper_convert.accepted_filesize:
            return True
        else:
            npyscreen.notify_confirm("The input file size {} is longer than {} bytes.".format(os.path.getsize(filename), Whisper_convert.accepted_filesize), title="Error")
            notify_result = npyscreen.notify_ok_cancel("Shall I split the input file {} into the necessary chunk sizes and process the first chunk?".format(filename))
            if notify_result==False:
                return False            
            chunks = split_files.split_audio(filename, Whisper_convert.accepted_filesize)
            if not os.access(filename, os.W_OK):
                    npyscreen.notify_confirm("I cannot write the split files to the directory of the input file {}, because the directory is not writable. Please choose a different file or check permissions.".format(filename), title="Error")
                    return False
            for i, chunk in enumerate(chunks):
                _, file_ext = os.path.splitext(filename)[1:]
                chunk.export(f"{filename}_{i}.{file_ext}", format={file_ext})
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
            if ChooseFileForm.validate_input_file(selected_file) and ChooseFileForm.is_length_below_limit(selected_file):                    
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
        #self.parentApp.switchFormNow()

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
    def __init__(self, target, args):
        super(OutputThread, self).__init__()
        self.target = target
        self.args = args

    def run(self):
        sys.stdout = CustomStdout()
        self.target(*self.args)
        sys.stdout = sys.__stdout__

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