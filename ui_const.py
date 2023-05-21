#contains the UI constants and help for the main form and related GUI forms (messages that will probably not be refactored for other uses)

#main.py
NAME_MAINFORM_EN= "Transcribe audio to text, redact transcription"
NAME_MISSINGOPENAIKEY_EN ="Missing OpenAI API key"
NAME_MISSINGOPENAIKEYDISPLAY_EN = "Enter missing OpenAI API key"
NAME_CHOOSELANGUAGE_EN = "Choose language"
NAME_CHOOSEMODEL_EN = "Choose model"
NAME_INITIALPROMPT_EN = "Transcription prompt"
NAME_REDACTPROMPT_EN = "Redaction prompt"

NAME_REDACTBUTTON_EN = "Redact"
NAME_TRANSCRIBEBUTTON_EN = "Transcribe"
NAME_GPT4CBOX_EN= "Use GPT4?"
NAME_EXITBUTTON_EN = "Exit"
NAME_AUDIOFILEBUTTON_EN = "Choose audio file for transcription"
NAME_AUDIOFILEDISPLAY_EN = "Audio file:"
NAME_CUDACBOX_EN = "Try w/CUDA"
NAME_TIMESTAMP_EN = "Timestamp"
NAME_GPTMAXBUTTON_EN = "Max token length"
NAME_GPTMAXLENGTHINPUT_EN = "Set the max. token length for the redaction function"

NAME_TEXTFILEBUTTON_EN = "Choose text file (output for transcription or input redaction)"
NAME_TEXTFILEDISPLAY_EN = "Text file:"
NAME_OUTPUT_EN = "Output:"

HELP_TEXTFILEDISPLAY_EN = "This is a text file. If you transcribe, the output will be saved to this file. If you try to redact it by OpenAI GPT, this file will be the source for the redaction."
HELP_AUDIOFILEDISPLAY_EN = "This is the audio file of the formats accepted by Whisper that you wish to transcribe to text."
HELP_TRYCUDA_EN = "If your computer has a GPU w/ 2GB+ RAM, and have proper drivers installed, you may " \
        "try to use that to speed up your transcription (but probably will not work...)." \
        "~2 GB GPU was enough for small, ~10 GB needed for the large model. Tiny model is useless in most languages."
HELP_GPT4CBOX_EN = "If your API key supports GPT-4, you can enable use of GPT-4. Although GPT-4 much slower, GPT-3.5 sometimes redacts in English, changing the original language and often ignores instructions." \
        "For this reason, with GPT-3.5, system prompt is included in user prompt."
HELP_TIMESTAMP_EN = "Timestamping for transcribed lines (useful later for remerging diarised audios, e.g. separate audio files by different speakers of the same conversation)."

MSG_DELETEUPONEXIT_EN = "The program has created new files when splitting up the audio in parts. Shall we delete those files now?"

#lang_model_prompt_chooser.py
NAME_DETECTLANGUAGEVALUE_EN = "Detect lang."
NAME_INITIALPROMPTTEXTBOX_EN = "You may enter a prompt to assist the transcription"

HELP_CHOOSELANGUAGE_EN = "You may choose one language of the audio that is to be transcribed. \n" \
                         "If you do not choose it, the model will try to detect it based on the first 30 seconds."
HELP_CHOOSEMODEL_EN = "You may select the size of the model used for transcription. Affects the speed and performance of transcription." \
                      "The default choice is the largest (and slowest) model."
HELP_SETINITIALPROMPT_EN = "You may set an initial prompt for the transcription model. Entering information regarding the content of the audio  \n" \
                            "to be transcribed may help the model in making more precise transcriptions. You may also enter frequently used terms during the audio. \n" \
                            "You can also provide hints or wishes regarding the format of transcription."
HELP_SETREDACTPROMPT_EN = "You may change the system prompt for the redaction (OpenAI/GPT) model. To record the default value, delete the prompt."

#file_handler.py
NAME_TITLEFILENAME_EN = "Choose {} file:"
MSG_PRESSTABTOBROWSE_EN = "Press TAB to browse files from the directory entered (ending with \\)"
MSG_VALIDATEOUTPUT_OVERWRITE_EN = "The text file {} already exists. If you press 'Transcript', the new text will be appended to the existing text. Press Cancel if you don't want this."
MSG_VALIDATEOUTPUTFILE_NOTWRITABLE_EN = "The text file {} is not writable. Please choose a different file or check permissions."
MSG_DIRECTORYNOTWRITABLE_EN = "The directory {} is not writable. Please choose a different file or check permissions."
MSG_AUDIOTOOLARGE_EN = "The audio file size {} MB is longer than {} MB."
MSG_SPLITAUDIO_EN = "Shall I split the audio file {} into the necessary chunk sizes and process the chunks?"
MSG_FILENOTEXIST_EN = "The file {} does not exist."
MSG_EXTENSIONNOTACCEPTED_EN = "The audio file extension {} is not accepted. Please convert it to one of the accepted formats: {}."

#This could not be included in Whisper_transcript, due to the lag of importing whisper and cuda
ACCEPTED_WHISPER_EXTENSIONS = "*.mp3;*.m4a;*.mpga;*.wav;*.webm"
accepted_whisper_extensions_list = ACCEPTED_WHISPER_EXTENSIONS.split(";")
ACCEPTED_WHISPER_FILESIZE = 26214400 #This was around 25 MB, but it seems offline Whisper is no longer using this limit, and current limit depends on GPU/CPU etc. so not using it
