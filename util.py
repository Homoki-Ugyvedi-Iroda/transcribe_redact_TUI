import re
import tiktoken
import json
from typing import List
import os

DEF_ENCODING_NAME = "cl100k_base"
DEF_MAX_CHUNK_SIZE = 8192

def get_own_prompt_length() -> int:
    from redactor import SYSTEM_PROMPT_DEF, OpenAIRedactor
    redactor = OpenAIRedactor("")
    size = get_token_length(SYSTEM_PROMPT_DEF)
    size += get_token_length(redactor.read_prompt_instructions())
    size += get_token_length(json.dumps(redactor.read_prompt_qa_examples()))
    return size

def get_token_length(sentence: str) -> int:
    encoding = tiktoken.get_encoding(DEF_ENCODING_NAME)
    return len(encoding.encode(sentence))
    
def create_chunks(text: str, max_chunk_size=DEF_MAX_CHUNK_SIZE) -> List[str]:
    max_chunk_size=max_chunk_size-get_own_prompt_length()
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        current_chunk_size = get_token_length(current_chunk)
        sentence_size = get_token_length(sentence)

        if current_chunk_size + sentence_size <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            #logging.info(f"chunk: {current_chunk.strip()}")
            #logging.info(f"chunksize: {get_token_length(current_chunk.strip())}")
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def check_split_files_presence_under_input_file(input_file: str, max_file_size: int)-> bool:
    filename_root, file_ext = os.path.splitext(input_file)    
    filename_to_check = filename_root+"_" + "0" + file_ext
    if os.path.exists(filename_to_check) and os.path.getsize(filename_to_check) < max_file_size:
        return True
    filename_to_check = filename_root+"_" + "1" + file_ext    
    if os.path.exists(filename_to_check) and os.path.getsize(filename_to_check) < max_file_size:
        return True
    return False
    
def list_split_files(input_file: str)-> List[str]:
    #only runs if check_split_files_presence_under_input_file = True
    def list_split_files(input_file: str) -> List[str]:
        path, filename_ext = os.path.split(input_file)
        filename_root, file_ext = os.path.splitext(filename_ext)
        pattern = rf"{filename_root}" + r"_(\d+)"
        files = [file for file in os.listdir(path) if re.match(pattern, file)]
        files.sort(key=lambda x: int(re.match(pattern, x).group(1)))
        return files        
    
def get_prompt_value_formatted(input: str)-> str:
    return input.replace("\n", " ").replace("\r", " ").strip()
    
