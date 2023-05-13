import os
from typing import NamedTuple
from typing import Tuple
import npyscreen
from main import BaseView
import ui_const

ACCEPTED_WHISPER_EXTENSIONS = "*.mp3;*.m4a;*.mpga;*.wav;*.webm"
accepted_whisper_extensions_list = ACCEPTED_WHISPER_EXTENSIONS.split(";")
ACCEPTED_WHISPER_FILESIZE = 25*1024*1024


class ChooseFileForm(npyscreen.ActionForm, BaseView):
    class ValidationResult(NamedTuple):
        valid: bool
        message: str = None
    
    def __init__(self, *args, mode='input', **kwargs):
        self.mode = mode
        super().__init__(*args, **kwargs)
    
    def create(self):
        self.file_widget = self.add(npyscreen.TitleFilename, name=ui_const.NAME_TITLEFILENAME_EN.format(self.mode),
                                     select_dir=False, must_exist=True,
                                     mask=ACCEPTED_WHISPER_EXTENSIONS if self.mode == 'input' else "*.txt")
        self.add(npyscreen.FixedText, value=ui_const.MSG_PRESSTABTOBROWSE_EN, editable=False, color='CONTROL')
        self.selected_file = None
    
    def validate_output_file(self, filename: str)-> bool: 
        if os.path.exists(filename):
            notify_result = self.display_message_ok_cancel(ui_const.MSG_VALIDATEOUTPUT_OVERWRITE_EN.format(filename))
            if not notify_result:
                return False
            else:
                if not os.access(filename, os.W_OK):
                    self.display_message_confirm(ui_const.MSG_VALIDATEOUTPUTFILE_NOTWRITABLE_EN.format(filename))
                    return False
        else:
            parent_directory = os.path.dirname(filename)
            if not os.access(parent_directory, os.W_OK):
                self.display_message_confirm(ui_const.MSG_DIRECTORYNOTWRITABLE_EN.format(parent_directory))
                return False
        return True   
    
    def is_extension_accepted(self, filename: str) -> bool:
        _, file_ext = os.path.splitext(filename)
        file_ext = f"*{file_ext}" 
        return file_ext in accepted_whisper_extensions_list
    
    def is_length_below_limit(self, filename: str)-> Tuple[bool, str]:
        if os.path.getsize(filename) < ACCEPTED_WHISPER_FILESIZE:
            return True, filename
        else:
            file_size_actual = os.path.getsize(filename)
            file_size_in_MB = int(file_size_actual / 1024 ** 2)
            max_file_size = int(ACCEPTED_WHISPER_FILESIZE / 1024 ** 2)
            self.display_message_confirm(ui_const.MSG_AUDIOTOOLARGE_EN.format(file_size_in_MB, max_file_size))
            notify_result = self.display_message_ok_cancel(ui_const.MSG_SPLITAUDIO_EN.format(filename))
            if not notify_result:
                return False
            else:                
                import split_files
                chunks = split_files.split_audio(filename, ACCEPTED_WHISPER_FILESIZE)
                if not os.access(filename, os.W_OK):
                        self.display_message_confirm(ui_const.MSG_DIRECTORYNOTWRITABLE_EN.format(filename))
                        return False
                for i, chunk in enumerate(chunks):
                    filename_root, file_ext = os.path.splitext(filename)
                    chunk.export(f"{filename_root}_{i}{file_ext}", format=file_ext[1:])
            return True, filename
        
    def validate_input_file(self, filename: str)-> bool: 
        if self.is_extension_accepted(filename):            
            if os.path.exists(filename):        
                return True            
            self.display_message_confirm(ui_const.MSG_FILENOTEXIST_EN.format(filename), title="Error")
            return False
        else:
            self.display_message_confirm(ui_const.MSG_EXTENSIONNOTACCEPTED_EN.format(filename, ACCEPTED_WHISPER_EXTENSIONS))
            return False
        
    def on_ok(self):
        self.selected_file = self.file_widget.value
        main_form=self.parentApp.getForm("MAIN")
            
        if self.mode == 'input':
            if self.validate_input_file(self.selected_file):                    
                    is_length_below, new_filename = self.is_length_below_limit(self.selected_file)
                    if is_length_below:
                        self.selected_file = new_filename
                        main_form.input_file = self.selected_file
                        self.parentApp.setNextForm("MAIN")
                        main_form.input_file_display.value = self.selected_file
                        main_form.input_file_display.update()
            else:
                self.parentApp.setNextForm("MISSING_FILE")
        elif self.mode == 'output':
            if self.validate_output_file(self.selected_file):
                main_form.output_file = self.selected_file
                main_form.output_file_display.value = self.selected_file
                main_form.output_file_display.update()
                self.parentApp.setNextForm("MAIN")
            else:
                self.parentApp.setNextForm("MISSING_FILE")
                                
    def on_cancel(self):
        self.parentApp.setNextForm("MAIN")
