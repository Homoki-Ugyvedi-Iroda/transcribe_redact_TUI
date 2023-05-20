# transcribe_redact_TUI

This a simple TUI (using npyscreen) Python app for OpenAI's whisper model (=transcribing audio) and redaction w/ OpenAI GPT APIs.

The objective was to make a tool that is accessible for experimentation for legal uses by solo lawyers and small law firms (by lawyers for lawyers).

On the first run of transcription, the app downloads models, that takes a LONG time and uses up lots of space (e.g. 2.7 GB for large model).

Currently source code only:

```
pip install -r requirements.txt
python transcribe_redact_TUI.py
```

## Experiences using the Whisper model

This does not use the API, but the downloadable models, so for transcription, no data leaves your computer when using this application. There are different kinds of models available, but in Hungarian, only the biggest ("large") is usable, and even that is far from perfect. But large model gives much better results compared to e.g. what Google Cloud transcription services are able to provide currently in Hungarian.

Problem with CUDA-based transcription is the complexity of drivers (e.g. a different driver might be needed for specific cards - more testing needed).

The greatest is that these models are multilingual (there are English-only models, but they're out of the scope of this experiment.)

You can try using CUDA-compatible GPUs on your computer for speeding up the transcription, if proper CUDA-drivers are installed. It really speeds up the results, but the memory size of the GPU will be a severe limiting factor.

E.g. a ten-year-old GeForce 750 Ti with 2 GB of RAM is not enough for the medium model.

See also:

1. the Whisper [OpenAI paper](https://cdn.openai.com/papers/whisper.pdf) for more technical details,
        
2. the Whisper [GitHub page](https://github.com/openai/whisper),
        
3. this [blogpost](https://www.assemblyai.com/blog/how-to-run-openais-whisper-speech-recognition-model/).

## Using OpenAI GPT for redaction

Rename .env.sample to .env and insert your OpenAI API key to be able to use the OpenAI GPT redaction "service".

You can ask for an OpenAI API key by registering at OpenAI, see https://platform.openai.com/account/api-keys. Keys are very cheap, but do cost money and will need a credit card. Annoying 

If your API key supports GPT-4, you can enable use of GPT-4 for redaction.

*Cons of using GPT-4*: It is much slower than GPT-3.5.

Even if they advertise 32K token lengths (for input and output), I cannot even use 8K tokens for input, especially in the afternoon CEST. Even with a timeout, the requests are charged!

I had more success with 3K token, so that's set in the application as well.

*Cons of GPT-3.5*: This provides output in the language of the prompt (the current system prompt is used in English), even if the instructions are made to provide responses in the language of the source, not the instruction.

This makes such use often impractical, and requires rewriting the original instructions.

Also, due to ignoring system prompts, with GPT-3.5, system prompt is included in user prompt instead, but still tends to ignore it.

There are two empty files in the /static folder that are not used in this application: 

- prompt_qa_examples.json could be used for chat examples to submit to the LLM (not really useful for the redaction purpose, so not used in the application),

- prompt_instructions.txt is used for a prefixed prompt (but we have a Redaction prompt button for that purpose here).

## TODO:  

- [ ] check why initial_prompt is not working and whether it works the same from command prompt (e.g. encoding inappropriate?)
- [ ] replace Cuda cb with timestamping option (for later merging of audio files separated per persons in discussions)
- [ ] involvement of audio improvement/separation etc. chain?
- [ ] A "PySimpleGUI" version?

There are some npyscreen problems:
- non-ASCII characters cannot be entered via keyboard (self._last_get_ch_was_unicode always returns false for non-ascii, had to be overriden)
- user cannot reach button helps (F1 does not work with active buttons, only w/ forms)
