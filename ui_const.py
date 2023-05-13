#contains the UI constants and help for the main form and related GUI forms (minor forms without MVP format)

#main.py
NAME_MAINFORM_EN= "Transcribe audio to text, redaction"
NAME_MISSINGOPENAIKEY_EN ="Missing OpenAI API key"
NAME_MISSINGOPENAIKEYDISPLAY_EN = "Enter missing OpenAI API key"
NAME_CHOOSELANGUAGE_EN = "Choose language"
NAME_CHOOSEMODEL_EN = "Choose model"
NAME_INITIALPROMPT_EN = "Initial prompt (opt.)"
NAME_EXITBUTTON_EN = "Exit"
NAME_AUDIOFILEBUTTON_EN = "Choose audio file for transcription"
NAME_AUDIOFILEDISPLAY_EN = "Audio file:"

NAME_TEXTFILEBUTTON_EN = "Choose text file (output for transcription or input redaction)"
NAME_TEXTFILEDISPLAY_EN = "Text file:"
NAME_OUTPUT_EN = "Output:"
HELP_TEXTFILEDISPLAY_EN = "This is a text file. If you transcribe, the output will be saved to this file. If you try to redact it by OpenAI GPT, this file will be the source for the redaction."
HELP_AUDIOFILEDISPLAY_EN = "This is the audio file of the formats accepted by Whisper that you wish to transcribe to text."

NAME_CHOOSEMODEL_EN = "Choose a model from the list"
NAME_CHOOSELANGUAGE_EN = "Choose a language from the list"
NAME_INITIALPROMPT_EN = "Initial prompt"
NAME_INITIALPROMPTTEXTBOX_EN = "Enter prompt to assist the transcription"

#lang_model_prompt_chooser.py
NAME_DETECTLANGUAGEVALUE_EN = "Detect language"
HELP_CHOOSELANGUAGE_EN = ""
HELP_CHOOSEMODEL_EN = ""
HELP_SETINITIALPROMPT_EN = ""

#choose_file.py
NAME_TITLEFILENAME_EN = "Choose {} file:"
MSG_PRESSTABTOBROWSE_EN = "Press TAB to browse files from the directory entered (ending with \\)"
MSG_VALIDATEOUTPUT_OVERWRITE_EN = "The text file {} already exists. If you press 'Convert', the file will be overwritten. Press Cancel if you don't want this."
MSG_VALIDATEOUTPUTFILE_NOTWRITABLE_EN = "The text file {} is not writable. Please choose a different file or check permissions."
MSG_DIRECTORYNOTWRITABLE_EN = "The directory {} is not writable. Please choose a different file or check permissions."
MSG_AUDIOTOOLARGE_EN = "The audio file size {} MB is longer than {} MB."
MSG_SPLITAUDIO_EN = "Shall I split the audio file {} into the necessary chunk sizes and process the chunks?"
MSG_FILENOTEXIST_EN = "The file {} does not exist."
MSG_EXTENSIONNOTACCEPTED_EN = "The audio file extension {} is not accepted. Please convert it to one of the accepted formats: {}."
