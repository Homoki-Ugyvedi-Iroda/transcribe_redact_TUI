# transcribe_redact_TUI
A simple TUI (npyscreen) python app for whisper and redaction w/ OpenAI GPT APIs
On the first run of transcription, downloads selected models, that could take a long time and place (e.g. 2.7 GB for large model).
Rename .env.sample to .env and insert your OpenAI API key to be able to use the OpenAI GPT redaction "service".

Todo:  
        A "PySimpleGUI" version:
        There are npyscreen problems with win_npcurses(?):
                non-ascii characters cannot be entered via keyboard
                user cannot reach button helps (F1 does not work with active buttons, only w/ forms)
                multilineedit softwrap does not work
        The OpenAI GPT model number can be changed in code only, uses GPT-3.5 automatically
