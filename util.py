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
        # Calculate the size of the current chunk and the new sentence in bytes
        current_chunk_size = return_token_length(current_chunk)
        sentence_size = return_token_length(sentence)

        # Check if adding the sentence would exceed the max_chunk_size
        if current_chunk_size + sentence_size <= max_chunk_size:
            current_chunk += " " + sentence
        else:
            # Add the current chunk to the chunks list and start a new chunk
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    # Add the last chunk to the chunks list
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
