from pydub import AudioSegment
from os.path import getsize

def split_audio(input_file: str, max_size_in_bytes: int):
    """Splits the audio file into the number of bytes as defined if the directory is writable

    Args:
        input_file (str): the filename that contains the audio file to be split.
        max_size_in_bytes (int): the maximum number of bytes each chunk of recording may be as a maximum

    Returns:
        _type_: a list of binary audio_chunks
    """
    audio = AudioSegment.from_file(input_file)    
    duration_in_ms = len(audio)
    size_ratio = getsize(input_file) / max_size_in_bytes
    max_chunk_audio_duration_ms = int (duration_in_ms * 1 / size_ratio)
    
    audio_chunks = []
    start_time = 0
    end_time = max_chunk_audio_duration_ms

    while start_time < len(audio):
        end_time = min(len(audio), start_time + max_chunk_audio_duration_ms)
        chunk = audio[start_time:end_time]
        audio_chunks.append(chunk)
        start_time = end_time

    return audio_chunks
