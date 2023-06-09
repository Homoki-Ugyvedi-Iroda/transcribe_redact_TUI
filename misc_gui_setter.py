import npyscreen
import ui_const
import os
from dotenv import set_key

LANGUAGE_LIST = ["Bulgarian | bg",
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
LANGUAGE_LIST.insert(0, ui_const.NAME_DETECTLANGUAGEVALUE_EN)
MODEL_LIST = ["Tiny model","Base model","Small model","Medium model","Large model"]

def get_lang_model_env_value(env_name: str, default_name: str) -> str:
    if os.getenv(env_name) is not None:
        return os.getenv(env_name)
    return default_name

class LanguageModelHandler:
    def __init__(self, form):
        self.form = form
    def create(self):
        self.language = ChooseLanguageButton(self.form)
        self.language.create()
        self.model = ChooseModelButton(self.form)
        self.model.create()
    
class ChooseLanguageButton:
    def __init__(self, form):
        self.form = form
        self.parentApp = form.parentApp
    
    def create(self):
        selected_value = get_lang_model_env_value("LANG", LANGUAGE_LIST[0])
        self.language_button = self.form.add(npyscreen.ButtonPress, name=selected_value, rely = 7, relx=50)        
        self.language_button.whenPressed = self.switch_to_choose_language_form

    def switch_to_choose_language_form(self):
        self.form.parentApp.switchForm('CHOOSELANG')
                
class ChooseLanguageForm(npyscreen.Popup):
    def create(self):
        values = LANGUAGE_LIST
        selected_value = get_lang_model_env_value("LANG", LANGUAGE_LIST[0])
        selected_index = values.index(selected_value) if selected_value in values else 0
        self.language_select = self.add(npyscreen.TitleSelectOne, values=values, name=ui_const.NAME_CHOOSELANGUAGE_EN, value = [selected_index], scroll_exit=True, help=ui_const.HELP_CHOOSELANGUAGE_EN)
    def afterEditing(self):
        chosen_language = self.language_select.values[self.language_select.value[0]]
        main_form = self.parentApp.getForm("MAIN")
        main_form.languagemodel.language.language_button.name = chosen_language
        main_form.languagemodel.language.language_button.update()
        set_key('.env', "LANG", chosen_language)
        self.parentApp.switchForm("MAIN")

class ChooseModelButton:
    def __init__(self, form):
        self.form = form
        self.parentApp = form.parentApp
    
    def create(self):
        selected_value = get_lang_model_env_value("MODEL", MODEL_LIST[len(MODEL_LIST)-1])
        self.model_button = self.form.add(npyscreen.ButtonPress, name=selected_value, rely=7, relx=70)
        self.model_button.whenPressed = self.switch_to_choose_model_form
    
    def switch_to_choose_model_form(self):
        self.form.parentApp.switchForm('CHOOSEMODEL')

        
class ChooseModelForm(npyscreen.Popup):
    def create(self):
        values = MODEL_LIST
        selected_value = get_lang_model_env_value("MODEL", MODEL_LIST[len(MODEL_LIST)-1])
        selected_index = values.index(selected_value) if selected_value in values else 0
        self.model_select = self.add(npyscreen.TitleSelectOne, values=values, name=ui_const.NAME_CHOOSEMODEL_EN, value = [selected_index], scroll_exit=True, help=ui_const.HELP_CHOOSEMODEL_EN)

    def afterEditing(self):
        chosen_model = self.model_select.values[self.model_select.value[0]]
        main_form = self.parentApp.getForm("MAIN")
        main_form.languagemodel.model.model_button.name = chosen_model
        main_form.languagemodel.model.model_button.update()
        set_key('.env', "MODEL", chosen_model)
        self.parentApp.switchForm("MAIN")

class CudaCheckbox:    
    def __init__(self, form):
        self.form = form
    def create(self):        
        checkbox_value_str = os.getenv("CUDA")
        if checkbox_value_str == "True":
            checkbox_value_bool = True
        else:
            checkbox_value_bool = False
        self.cuda_cb = self.form.add(npyscreen.Checkbox, name=ui_const.NAME_CUDACBOX_EN, value=checkbox_value_bool, help = ui_const.HELP_TRYCUDA_EN, relx=4, max_width=23, rely=8, max_height=1)
        self.cuda_cb.whenToggled = self.update_cb_save_to_env
    
    def update_cb_save_to_env(self):
        if self.cuda_cb.value:
            set_key(".env", "CUDA", "True")
        else:
            set_key(".env", "CUDA", "False")
            
class TimestampCheckbox:    
    def __init__(self, form):
        self.form = form
    def create(self):        
        checkbox_value_str = os.getenv("TIMESTAMP")
        if checkbox_value_str == "True":
            checkbox_value_bool = True
        else:
            checkbox_value_bool = False
        self.ts_cb = self.form.add(npyscreen.Checkbox, name=ui_const.NAME_TIMESTAMP_EN, value=checkbox_value_bool, help = ui_const.HELP_TIMESTAMP_EN, relx=70, max_width=23, rely=8, max_height=1)
        self.ts_cb.whenToggled = self.update_cb_save_to_env
    
    def update_cb_save_to_env(self):
        if self.ts_cb.value:
            set_key(".env", "TIMESTAMP", "True")
        else:
            set_key(".env", "TIMESTAMP", "False")