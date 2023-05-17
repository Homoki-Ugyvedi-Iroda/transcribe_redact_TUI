import os
from typing import NamedTuple
from typing import Tuple
import npyscreen
import ui_const
from util import check_split_files_presence_under_input_file
from baseview import BaseView

class FileHandler:
    def __init__(self, form):
        self.form = form

    def create(self):
        self.form.choose_input_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_AUDIOFILEBUTTON_EN)
        self.form.choose_input_button.whenPressed = self.choose_input_file
        self.form.input_file_display = self.form.add(npyscreen.FixedText, name=ui_const.NAME_AUDIOFILEDISPLAY_EN, editable=False)

        self.form.choose_output_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_TEXTFILEBUTTON_EN)
        self.form.choose_output_button.whenPressed = self.choose_output_file
        self.form.output_file_display = self.form.add(npyscreen.FixedText, name=ui_const.NAME_TEXTFILEDISPLAY_EN, editable=False)
    
    def choose_input_file(self):
        from file_handler import ChooseFileForm
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='input', help=ui_const.HELP_AUDIOFILEDISPLAY_EN)
        form.edit()
        self.form.input_file = form.selected_file
        self.form.transcriptor.update_visibility()

    def choose_output_file(self):
        from file_handler import ChooseFileForm        
        form = ChooseFileForm(parentApp=self.form.parentApp, mode='output', help=ui_const.HELP_TEXTFILEDISPLAY_EN)
        form.edit()
        self.form.output_file = form.selected_file
        self.form.transcriptor.update_visibility()
        self.form.redactor.update_visibility()

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
                                     mask=ui_const.ACCEPTED_WHISPER_EXTENSIONS if self.mode == 'input' else "*.txt")
        self.add(npyscreen.FixedText, value=ui_const.MSG_PRESSTABTOBROWSE_EN, hidden=False, color='CONTROL', editable=False)
        self.selected_file = None
    
    def validate_output_file(self, filename: str)-> bool: 
        main_form=self.parentApp.getForm("MAIN")
        if os.path.exists(filename) and main_form.input_file is not None:
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
        return file_ext in ui_const.accepted_whisper_extensions_list
    
    def is_length_below_limit(self, filename: str)-> Tuple[bool, str]:
        if os.path.getsize(filename) < ui_const.ACCEPTED_WHISPER_FILESIZE:
            return True, filename
        else:
            file_size_actual = os.path.getsize(filename)
            file_size_in_MB = int(file_size_actual / 1024 ** 2)
            max_file_size_in_MB = int(ui_const.ACCEPTED_WHISPER_FILESIZE / 1024 ** 2)
            if check_split_files_presence_under_input_file(filename, ui_const.ACCEPTED_WHISPER_FILESIZE):
                return True, filename
            self.display_message_confirm(ui_const.MSG_AUDIOTOOLARGE_EN.format(file_size_in_MB, max_file_size_in_MB))
            notify_result = self.display_message_yes_no(ui_const.MSG_SPLITAUDIO_EN.format(filename))
            if not notify_result:
                return False, filename
            else:                
                import split_files
                chunks = split_files.split_audio(filename, ui_const.ACCEPTED_WHISPER_FILESIZE)
                if not os.access(filename, os.W_OK):
                        self.display_message_confirm(ui_const.MSG_DIRECTORYNOTWRITABLE_EN.format(filename))
                        return False, filename
                for i, chunk in enumerate(chunks):
                    filename_root, file_ext = os.path.splitext(filename)
                    filename_split = f"{filename_root}_{i}{file_ext}"
                    chunk.export(filename_split, format=file_ext[1:])
                    self.parentApp.getForm("MAIN").did_split.append(filename_split)
            return True, filename
        
    def validate_input_file(self, filename: str)-> bool: 
        if self.is_extension_accepted(filename):            
            if os.path.exists(filename):        
                return True            
            self.display_message_confirm(ui_const.MSG_FILENOTEXIST_EN.format(filename), title="Error")
            return False
        else:
            self.display_message_confirm(ui_const.MSG_EXTENSIONNOTACCEPTED_EN.format(filename, ui_const.ACCEPTED_WHISPER_EXTENSIONS))
            return False
        
    def on_ok(self):
        self.selected_file = self.file_widget.value
        main_form=self.parentApp.getForm("MAIN")
            
        if self.mode == 'input':
            if self.validate_input_file(self.selected_file):                    
                    #is_length_below, new_filename = self.is_length_below_limit(self.selected_file)
                    #if is_length_below:
                        #self.selected_file = new_filename
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
