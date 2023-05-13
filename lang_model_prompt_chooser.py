import npyscreen
import ui_const

LANGUAGE_LIST = ["Detect | -",
                "Bulgarian | bg",
                "Croatian | hr",
                "Czech | cs",
                "Danish | da",
                "Dutch | nl",
                "English | en",
                "Estonian | et",
                "Finnish | fi",
                "French | fr",
                "German | de",
                "Greek | el",
                "Hungarian | hu",
                "Italian | it",
                "Latvian | lv",
                "Lithuanian | lt",
                "Polish | pl",
                "Portuguese | pt",
                "Romanian | ro",
                "Slovak | sk",
                "Slovenian | sl",
                "Spanish | es",
                "Swedish | sv",
                ]
MODEL_LIST = ["Tiny model","Base model","Small model","Medium model","Large model"]

class ChooseLanguageButton:
    def __init__(self, form):
        self.form = form
    
    def create(self):
        self.language_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_DETECTLANGUAGEVALUE_EN, rely = 7, relx=2)
        self.language_button.whenPressed = self.switch_to_choose_language_form        
    
    def switch_to_choose_language_form(self):
        self.form.parentApp.switchForm('CHOOSELANG')
        
class ChooseLanguageForm(npyscreen.Popup):
    def create(self):
        self.language_select = self.add(npyscreen.TitleSelectOne, values=LANGUAGE_LIST, name=ui_const.NAME_CHOOSELANGUAGE_EN, value = [0,], scroll_exit=True, help=ui_const.HELP_CHOOSELANGUAGE_EN)
    def afterEditing(self):
        chosen_language = self.language_select.values[self.language_select.value[0]]
        main_form = self.parentApp.getForm('MAIN')
        main_form.language.language_button.name = chosen_language
        main_form.language.language_button.update()
        self.parentApp.switchForm('MAIN')

class ChooseModelButton:
    def __init__(self, form):
        self.form = form
    
    def create(self):
        self.model_button = self.form.add(npyscreen.ButtonPress, name="Large model", rely=7, relx=24)
        self.model_button.whenPressed = self.switch_to_choose_model_form        
    
    def switch_to_choose_model_form(self):
        self.form.parentApp.switchForm('CHOOSEMODEL')
        
class ChooseModelForm(npyscreen.Popup):
    def create(self):
        self.model_select = self.add(npyscreen.TitleSelectOne, values=MODEL_LIST, name=ui_const.NAME_CHOOSEMODEL_EN, value = [len(MODEL_LIST) - 1,], scroll_exit=True, help=ui_const.HELP_CHOOSEMODEL_EN)
    def afterEditing(self):
        chosen_model = self.model_select.values[self.model_select.value[0]]
        main_form = self.parentApp.getForm('MAIN')
        main_form.model.model_button.name = chosen_model
        main_form.model.model_button.update()
        self.parentApp.switchForm('MAIN')

class InitialPromptButton:
    def __init__(self, form):
        self.form = form
    def create(self):
        self.initial_prompt_button = self.form.add(npyscreen.ButtonPress, name=ui_const.NAME_INITIALPROMPT_EN, rely=7, relx=44)
        self.initial_prompt_button.whenPressed = self.switch_to_initial_prompt_form        
    def switch_to_initial_prompt_form(self):
        self.form.parentApp.switchForm('INIT_PROMPT')    
    
class SetInitialPrompt(npyscreen.ActionPopup):
    def create(self):
        self.add(npyscreen.TitleText, name = ui_const.NAME_INITIALPROMPTTEXTBOX_EN, begin_entry_at=0, help = ui_const.HELP_SETINITIALPROMPT_EN)
        
    def on_ok(self):
        main_form = self.parentApp.getForm('MAIN')
        main_form.initial_prompt = self.get_widget(0).value
        self.parentApp.switchFormPrevious()
    
    def on_cancel(self):
        self.parentApp.getForm('MAIN').initial_prompt = ""
        self.parentApp.switchFormPrevious()
