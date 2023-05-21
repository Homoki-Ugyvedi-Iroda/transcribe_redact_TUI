
from whisper import load_model
from torch import cuda
from tiktoken import get_encoding

class WhisperConverter:    
	
	def whisper_convert(self, input_file: str, output_file: str, language: str='', initial_prompt: str='', model_name: str="large", CUDA: bool=False, tb: bool=False):
		"""
	    Converts the input file to a text.
	    :input_file: the filename of the input audio file to convert.
	    :output_file: the filename of the output text file.
		:language: the language in two-letter ISO format of the language of the audio (if not provided, the first 30 seconds will be used to discover)
		:initial_prompt: an instruction to the model regarding the format or content of the audio (or previous context), only the final 224 tokens will be used
	    """

     
		device = 'cpu'
		if CUDA is True:
			device = 'cuda'
		try:
			model = load_model(name=model_name, device=device)
		except cuda.OutOfMemoryError:
			raise GPUOutOfMemory()
			model = load_model(name=model_name, device='cpu')

		decode_options = {}
		if language is not None:
			language=language[:2]
			decode_options.update({"language": language})
		if initial_prompt is not None:
			decode_options.update({"prompt": initial_prompt})

		try:			
			result = model.transcribe(audio=input_file, word_timestamps=tb, verbose=True, **decode_options) 
		except Exception as e:
			raise TranscribeOutOfMemory()

		with open(output_file, "a", encoding="utf-8", errors="ignore") as file:
			file.write(result["text"])     

class GPUOutOfMemory(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

    def log_error(self):
        print("GPU memory too small for the given model. Transcribing using CPU.")
        
class TranscribeOutOfMemory(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code

    def log_error(self):
        print("The file to be converted turned out to be too large for conversion.")
    