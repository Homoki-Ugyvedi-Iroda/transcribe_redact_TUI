import npyscreen
import os
import curses
import Whisper_convert
import redact_text_w_openAI
import dotenv
import util

dotenv.load_dotenv()        
apikey = os.getenv("OPENAI_API_KEY")
output_file = ('output.txt')
        
class MyApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MainForm, name="Audio to text conversion")
        self.addForm("MISSING_FILE", InputFileCombo, name="Choose a file or enter a filename...")
        self.addForm("MISSING_OPENAIAPIKEY", MissingOpenAiApiKey, name="Missing OpenAI API key")

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

class InputFileCombo(npyscreen.TitleFilenameCombo):
    def set_up_handlers(self):
        super().set_up_handlers()
        #self.handlers.update({curses.ascii.NL: self.update_output_directory})

'''
    def update_output_directory(self, *args):
        self.parent.output_file.value = os.path.join(os.path.dirname(self.value), "output.txt")
        self.parent.output_file.display()
        self.h_exit_down(None)
'''

class MainForm(npyscreen.ActionForm):
    def create(self):
        self.input_file = self.add(InputFileCombo, name="File to convert:",
                                   select_dir=False, must_exist=True, mask="*.mp3;*.m4a;*.mpga;*.wav;*.webm")
        self.output_file = self.add(InputFileCombo, name="Output File:",
                                    select_dir=False, must_exist=False, mask="*.txt", new=True)
        self.convert_button = self.add(npyscreen.ButtonPress, name="Convert")
        self.convert_button.whenPressed = self.on_convert
        self.redact_button = self.add(npyscreen.ButtonPress, name="Redact", hidden=True)
        self.redact_button.whenPressed = self.on_redact

    def on_cancel(self):
        self.parentApp.setNextForm(None)

    def on_convert(self):
        input_file = self.input_file.value
        output_file = self.output_file.value

        if not input_file or not output_file:
            npyscreen.notify_confirm("Both input and output files must be specified.", title="Error")
            return

        Whisper_convert.whisper_convert(input_file, output_file)        
        npyscreen.notify_confirm("Conversion complete!", title="Success")
        self.redact_button.hidden = False
        self.redact_button.update()
        self.display()
    
    def on_redact(self):
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
         
'''    def update_output_directory(self, *_args):
        input_file_dir = os.path.dirname(self.input_file.value)
        self.output_file.value = os.path.join(input_file_dir, "output.txt")
        self.output_file.display()
'''

        
if __name__ == "__main__":
    app = MyApp()
    app.run()