import whisper
import util
import os
import sys
#import torch
#import datetime
import tiktoken

class WhisperConverter:
    
	accepted_extensions = "*.mp3;*.m4a;*.mpga;*.wav;*.webm"
	accepted_extensions_list = accepted_extensions.split(";")
	accepted_filesize = 25*1024*1024

	def __init__(self, queue):
		self.queue = queue
        
	def whisper_convert(self, input_file: str, output_file: str, language: str='', initial_prompt: str=''):
		"""
	    Converts the input file to a text.
	    :input_file: the filename of the input audio file to convert.
	    :output_file: the filename of the output text file.
		:language: the language in two-letter ISO format of the language of the audio (if not provided, the first 30 seconds will be used to discover)
		:initial_prompt: an instruction to the model regarding the format or content of the audio (or previous context), only the final 224 tokens will be used
	    """
		modelName = "large"
		model = whisper.load_model(modelName, 'cpu')
		decode_options = {}
		if language is not None:
			language=language[:2]
			decode_options = language
		if initial_prompt is not None:
			encoding = tiktoken.get_encoding("cl100k_base")
			prompt_tokenized = encoding.encode(initial_prompt)
			decode_options = {"prompt": prompt_tokenized}
	
		if util.check_split_files(input_file):
			chunk_filenames = util.list_split_files(input_file) #ordered list of files is returned
			self.queue.put("Converting multiple files ({})... \n".format(len(chunk_filenames)))
			for filename in chunk_filenames:
				model = whisper.load_model(modelName)
				self.queue.put("Converting file: ({})... \n".format(os.path.basename(filename)))
				result = model.transcribe(audio=filename, word_timestamps=False, verbose=True, **decode_options) 		
				with open(output_file, "a", encoding="utf-8") as file:
					file.write(result["text"].strip())       
		else:
			result = model.transcribe(audio=input_file, word_timestamps=False, verbose=True, **decode_options) 
			with open(output_file, "w", encoding="utf-8") as file:
				file.write(result["text"])     
	
			'''if __name__ == "__main__":
			input_file = sys.argv[1]
			output_file = sys.argv[2]
			whisper_convert(input_file, output_file)'''
