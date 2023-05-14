# transcribe_redact_TUI
A simple TUI (npyscreen) python app for whisper and redaction w/ OpenAI GPT APIs
On the first run of transcription, downloads selected models, that could take a long time and place (e.g. 2.7 GB for large model).
Rename .env.sample to .env and insert your OpenAI API key to be able to use the OpenAI GPT redaction "service".
You can ask for an OpenAI API key by registering at OpenAI, see https://platform.openai.com/account/api-keys. Keys are very cheap, but do cost money and will need a credit card.

If your API key supports GPT-4, you can enable use of GPT-4 for redaction.
Cons of GPT-4: It is much slower than GPT-3.5, and usually I cannot even use 8K tokens for input, especially in the afternoon CEST. (I had more success with 3K token, so that's set in the application as well).
Cons of GPT-3.5: often in redacts in English, because the system prompt is used in English, so this changes the original language and often ignores instructions. Due to ignoring system prompts, with GPT-3.5, system prompt is included in user prompt instead, but still tends to ignore it.

#TODO:  
        RealtimeOutput is not scrolling
        A "PySimpleGUI" version:
        There are npyscreen problems with win_npcurses(?):
                - non-ASCII characters cannot be entered via keyboard
                - user cannot reach button helps (F1 does not work with active buttons, only w/ forms)
                - MultiLineEdit softwrap does not work.
