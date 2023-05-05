import re
import tiktoken
import redact_text_w_openAI
import json
import logging

def own_prompt_length() -> int:
    size = return_token_length(redact_text_w_openAI.SYSTEM_PROMPT)
    size += return_token_length(redact_text_w_openAI.read_prompt_instructions())
    size += return_token_length(json.dumps(redact_text_w_openAI.read_prompt_qa_examples()))
    logging.info("Own prompt size: {}".format(size))
    return size

def return_token_length(sentence: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(sentence))
    
def create_chunks(text: str, max_chunk_size=8192) -> list[str]:
    max_chunk_size=max_chunk_size-own_prompt_length()
    sentences = re.split(r'(?<=[.!?]) +', text)

    chunks = []
    current_chunk = ""

    for sentence in sentences:
        current_chunk_size = return_token_length(current_chunk)
        sentence_size = return_token_length(sentence)

        if current_chunk_size + sentence_size <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            chunks.append(current_chunk.strip())
            logging.info(f"chunk: {current_chunk.strip()}")
            logging.info(f"chunksize: {return_token_length(current_chunk.strip())}")
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())
        logging.info(f"Last chunk: {current_chunk.strip()}")
        logging.info(f"chunksize: {return_token_length(current_chunk.strip())}")

    return chunks
