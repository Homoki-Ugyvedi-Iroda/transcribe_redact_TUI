import re
import tiktoken
import redact_text_w_openAI
import json
import logging
from typing import List
from redactor import SYSTEM_PROMPT
import os

DEF_ENCODING_NAME = "cl100k_base"
DEF_MAX_CHUNK_SIZE = 8192

def get_own_prompt_length() -> int:
    redactor = redact_text_w_openAI.OpenAIRedactor("")
    size = get_token_length(SYSTEM_PROMPT)
    size += get_token_length(redactor.read_prompt_instructions())
    size += get_token_length(json.dumps(redactor.read_prompt_qa_examples()))
    logging.info("Own prompt size: {}".format(size))
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
            logging.info(f"chunk: {current_chunk.strip()}")
            logging.info(f"chunksize: {get_token_length(current_chunk.strip())}")
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())
        logging.info(f"Last chunk: {current_chunk.strip()}")
        logging.info(f"chunksize: {get_token_length(current_chunk.strip())}")

    return chunks

def check_split_files(input_file: str)-> bool:
    filename_root, file_ext = os.path.splitext(input_file)
    if os.path.exists(filename_root+"_0"+file_ext):
        return True
    else:
        return False
    
def list_split_files(input_file: str)-> List[str]:
    def number_from_filename(filename):
        match = re.match(pattern, filename)
        if match:
            return int(match.group(1))
        return None
    
    pattern = input_file + "_" 
    matching_files = []
    for file in os.listdir():
        match = re.match(pattern, file)
        matching_files.append(file)
    matching_files.sort(key=number_from_filename)
    result_files = []    
    previous_number = None
    for file in matching_files:
        current_number = number_from_filename(file)
        if previous_number is None or current_number == previous_number + 1:
            result_files.append(file)
            previous_number = current_number
        else:
            break
    return result_files

