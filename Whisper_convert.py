import whisper
# prompt alatt mit érthetnek itt?: https://platform.openai.com/docs/guides/speech-to-text/supported-languages
def whisper_convert(input_file: str, output_file: str):
	"""
    Converts the input file to a text.
    :input_file: the filename of the input audio file to convert.
    :output_file: the filename of the output text file.
    """

	modelName = "large-v2"
	language = "hungarian"
	model = whisper.load_model(modelName)
	result = model.transcribe(audio=input_file, language=language, word_timestamps=False, verbose=False)
	print("\nWriting transcription to file...")
	with open(output_file, "w", encoding="utf-8") as file:
		file.write(result["text"])
	print("Finished writing transcription file.")
 
 #to extend: check extensions, convert with ffmpeg, slice into 25 MB pieces
 # choose the language of the audio itself