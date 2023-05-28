# transcribe_redact_TUI

This a simple TUI (using npyscreen) Python app for OpenAI's whisper model (=transcribing audio) and to experiment with the redaction capabilities of OpenAI GPT APIs (by automated chunking at sentence borders and message lengths set in the application).

The objective was to make a tool that is accessible for experimentation for legal uses by solo lawyers and small law firms.

Currently source code only. 

Make sure the following requirements are fulfilled:

- Python 3.9.16 or later
- This is a Windows specific version, relying on `windows_curses` package.

After downloading this source in a zip (e.g. unzipping to directory e.g. "REDACT") or cloning by git, go to the unzipped directory. Of course, best practice is to create a virtual environment before installing with `venv`, but if you don't know what a venv is, don't use it just for this module.

Installing the packages could take 15-20 minutes.

```
pip install --upgrade pip
pip install -r requirements.txt
python transcribe_redact_TUI.py
```

It will request the OpenAI API key upon start (see below), but if you don't want to use the redact feature, just press enter here or enter any value you want.

Starting the first transcription may take longer time than later transcriptions.

If you receive a `enforce fail at alloc_cpu.cpp:72 DefaultCPUAllocator not enough memory` error during the first run with **large** model (even without a GPU), **exit the application**, restart it, and it may run without any problem next time.

## Experiences using the Whisper model

This does not use the API, but the downloadable models, so for transcription, no data leaves your computer when using this application. There are different kinds of models available, but for Hungarian, only the biggest ("large") is usable, and even that is far from perfect. In Hungarian, large model gives much better results compared to e.g. what Google Cloud transcription services are able to provide.

The drawbacks with CUDA-based transcription is the size and complexity of packages to install (pytorch may cause many other errors, needs more testing).

The greatest in Whisper is that these models are multilingual (there are English-only models, but they're out of the scope of this experiment.)

You can try using CUDA-compatible GPUs on your computer for speeding up the transcription (if latest drivers are installed). It really speeds up the results, but the memory size of the GPU will be a severe limiting factor. E.g. a ten-year-old GeForce 750 Ti with 2 GB of RAM is not enough for the medium model, which is not a problem when using CPU for transcription. Check the *Try-CUDA* button, if you have it installed. (If you don't have a GPU installed with proper drivers, and you still check this *Try-CUDA* button, you will get an error message in the output box when the actual transcription starts, so no big deal.)

The "transcription prompt" (using the `initial prompt` of Whisper) is just mildly useful. It may help the model in transcribing more precisely a specific list of words in the audio (vocabulary, e.g. proper nouns like persons' or organisations' names, technical terms etc.).

It's strange that the conversion time for the large model in English is about the same as the medium model in Hungarian:

Some benchmarks so far:

audio length|transcription length|HW|model|lang|WER|transcript. time multipl.
|--|--|--|--|--|--|--|
0:33:22|0:53:54|CPU,i5-10500, 16 GB|medium|Hungarian|11.36%|1.62
0:33:22|1:41:03|CPU,i5-10500, 16 GB|large|Hungarian|13.63%|3.03
0:48:56|1:19:09|CPU,i5-10500, 16 GB|large|English|N/A|1.62

See also:

1. the Whisper [OpenAI paper](https://cdn.openai.com/papers/whisper.pdf) for more technical details,
        
2. the Whisper [GitHub page](https://github.com/openai/whisper),
        
3. this [blogpost](https://www.assemblyai.com/blog/how-to-run-openais-whisper-speech-recognition-model/).

## Using OpenAI GPT for redaction

Rename `.env.sample` to `.env` and insert your OpenAI API key to be able to use the OpenAI GPT redaction "service". Or just enter the OpenAI key during first start (this is not really recommended, it's better just to copy it into the `.env` file).

You can ask for an OpenAI API key by registering at OpenAI, see https://platform.openai.com/account/api-keys. Keys are very cheap, but do cost money and will need a credit card.

If your API key supports GPT-4, you can enable use of GPT-4 for redaction.

*Cons of using GPT-4*: It is much slower than GPT-3.5.

Even if they advertise 32K token lengths (for input and output), I cannot even use 8K tokens for input, especially in the afternoon CEST. Please take note that all API calls received are charged, even those that fail. This is not a problem specific to my use, see a bunch of similar complaints [here](https://community.openai.com/t/gpt-4-api-gateway-timeout-for-long-requests-but-billed-anyway/177214/38).

I had more success with 3000 token, so that's what I suggest (if no value is given with GPT-4, otherwise it's 3/4 of the max length of the model). You can experiment with the proper token length if you want (using the *Max token length* button).

*Cons of GPT-3.5*: This provides output in the language of the prompt (the current system prompt is used in English), even if the instructions are made to provide responses in the language of the source, not the instruction.

This makes such use often impractical, and requires rewriting the original instructions.

Also, due to ignoring system prompts, with GPT-3.5, system prompt is included in user prompt instead, but still tends to ignore it.

If you do not give any redaction prompt, there is a default system prompt ("You are a silent AI tool helping to format the long texts that were transcribed from speeches. You format the text follows: you break up the text into paragraphs, correct the text for spelling errors. You may receive the text in multiple batches. Do not include your own text in the response, and use the original language of the text.")

There are two empty files in the /static folder that are not used in this application: 

- prompt_qa_examples.json could be used for chat examples to submit to the LLM (not really useful for the redaction purpose, so not used in the application),

- prompt_instructions.txt is used for a prefixed prompt (but we have a Redaction prompt button for that purpose here).

## TODO:  

- [ ] chaining of audio improvements (similar to Adobe Audition), separation (diarisation) of speakers, and solutionsfor merging documents, redrafting prompts etc.
- [ ] A "PySimpleGUI" version?

There are some npyscreen (or windows_curses?) specific problems:
- non-ASCII characters cannot be entered via keyboard (self._last_get_ch_was_unicode always returns false for non-ascii), even after overwriting, certain characters from certain keyboards fail to appear on screen (e.g. Hungarian "áÁúÚ" from keyboard, even if the same characters are available when using e.g. Slovak keyboard layout.) Workaround by manually editing `.env` file and enter the required prompt.
- user cannot reach button helps (F1 does not work with active buttons, only w/ forms)
