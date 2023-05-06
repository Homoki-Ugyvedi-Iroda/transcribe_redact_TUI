import whisper
import util
import main
import os

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
	if util.check_split_files(input_file):
		chunk_filenames = util.list_split_files(input_file) #ordered list of files is returned
		main.output_queue.put("Converting multiple files ({})... \n".format(len(chunk_filenames)))
		for filename in chunk_filenames:
			model = whisper.load_model(modelName)
			main.output_queue.put("Converting file: ({})... \n".format(os.path.basename(filename)))
			result = model.transcribe(audio=file, word_timestamps=False, verbose=True)
			with open(output_file, "a", encoding="utf-8") as file:
				file.write(result["text"].strip())       
	else:
		with open(output_file, "w", encoding="utf-8") as file:
			file.write(result["text"])