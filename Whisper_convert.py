import whisper

accepted_extensions = "*.mp3;*.m4a;*.mpga;*.wav;*.webm"
accepted_extensions_list = accepted_extensions.split(";")
accepted_filesize = 25*1024*1024

def whisper_convert(input_file: str, output_file: str):
	"""
    Converts the input file to a text.
    :input_file: the filename of the input audio file to convert.
    :output_file: the filename of the output text file.
    """

	modelName = "large-v2"
	model = whisper.load_model(modelName)
	result = model.transcribe(audio=input_file, word_timestamps=False, verbose=True)
	with open(output_file, "w", encoding="utf-8") as file:
		file.write(result["text"])