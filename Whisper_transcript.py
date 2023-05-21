
from whisper import load_model, utils
from torch import cuda
from tiktoken import get_encoding
MSG_OUTOFMEMORY_EN = "GPU memory too small for the given model. Transcribing using CPU."
MSG_TOOLARGEFILE_EN = "The file to be converted turned out to be too large for conversion."

class WhisperConverter:    
	
	def whisper_convert(self, input_file: str, output_file: str, language: str='', initial_prompt: str='', model_name: str="large", CUDA: bool=False, ts: bool=False):
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
			model = load_model(name=model_name, device='cpu')
			raise RuntimeError(MSG_OUTOFMEMORY_EN)
		decode_options = {}
		if language:
			language=language[:2]
			decode_options.update({"language": language})			
		if initial_prompt:
			decode_options.update({"prompt": initial_prompt})

		try:			
			result = model.transcribe(audio=input_file, word_timestamps=ts, verbose=True, **decode_options) 
		except Exception as e:
			raise RuntimeError(MSG_TOOLARGEFILE_EN)

		with open(output_file, "a", encoding="utf-8", errors="ignore") as file:
			if ts==False:
				file.write(result["text"])
			else:
				line = ""
				for segment in result["segments"]:
					start, end, text = segment["start"], segment["end"], segment["text"]
					line += f"[{utils.format_timestamp(start)} --> {utils.format_timestamp(end)}] {text}" + "\n"
				file.write(line)

