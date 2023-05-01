import re
import tiktoken

def return_token_length(sentence: str) -> int:
    encoding = tiktoken.encoding_for_model('gpt-4')
    return len(encoding.encode(sentence))
    
def create_chunks(text: str, max_chunk_size=4096) -> list[str]:
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
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
