import whisper
import util
import os
import tiktoken

MSG_CONVERTINGMULTIPLE_EN = "Converting multiple files ({})... \n"
MSG_CONVERTINGSINGLE_EN = "Converting file: ({})... \n"

class WhisperConverter:    
	
	def __init__(self, queue):
		self.queue = queue

	def display_message_queue(self, message: str):
		self.queue.put(message)

 
	def whisper_convert(self, input_file: str, output_file: str, language: str='', initial_prompt: str='', model_name: str="large"):
		"""
	    Converts the input file to a text.
	    :input_file: the filename of the input audio file to convert.
	    :output_file: the filename of the output text file.
		:language: the language in two-letter ISO format of the language of the audio (if not provided, the first 30 seconds will be used to discover)
		:initial_prompt: an instruction to the model regarding the format or content of the audio (or previous context), only the final 224 tokens will be used
	    """
  
		model = whisper.load_model(model_name, 'cpu')
		decode_options = {}
		if not language:
			language=language[:2]
			decode_options.update({"language": language})
		if not initial_prompt:
			encoding = tiktoken.get_encoding("cl100k_base")
			prompt_tokenized = encoding.encode(initial_prompt)
			decode_options.update({"prompt": prompt_tokenized})
	
		if util.check_split_files(input_file):
			chunk_filenames = util.list_split_files(input_file) #ordered list of files is returned
			self.display_message_queue(MSG_CONVERTINGMULTIPLE_EN.format(len(chunk_filenames)))
			for filename in chunk_filenames:
				self.display_message_queue(MSG_CONVERTINGSINGLE_EN.format(os.path.basename(filename)))
				result = model.transcribe(audio=filename, word_timestamps=False, verbose=True, **decode_options) 		
				with open(output_file, "a", encoding="utf-8") as file:
					file.write(result["text"].strip())       
		else:
			result = model.transcribe(audio=input_file, word_timestamps=False, verbose=True, **decode_options) 
			with open(output_file, "w", encoding="utf-8") as file:
				file.write(result["text"])     
	