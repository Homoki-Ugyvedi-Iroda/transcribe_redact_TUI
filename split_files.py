from pydub import AudioSegment

def split_audio(input_file: str, max_size_in_bytes: int):
    """Splits the audio file into the number of bytes as defined if the directory is writable

    Args:
        input_file (str): the filename that contains the audio file to be split.
        max_size_in_bytes (int): the maximum number of bytes each chunk of recording may be as a maximum

    Returns:
        _type_: a list of binary audio_chunks
    """
    audio = AudioSegment.from_file(input_file)

    max_chunk_duration_ms = (max_size_in_bytes / (audio.frame_rate * audio.frame_width)) * 1000

    audio_chunks = []
    start_time = 0
    end_time = max_chunk_duration_ms

    while start_time < len(audio):
        chunk = audio[start_time:end_time]
        audio_chunks.append(chunk)

        start_time += max_chunk_duration_ms
        end_time += max_chunk_duration_ms

    return audio_chunks
