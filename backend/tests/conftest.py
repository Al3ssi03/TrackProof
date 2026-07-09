import math
import struct
import wave
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def audio_wav(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """File audio locale di test: ~10s di melodia sintetica, generato al volo.

    Chromaprint ha bisogno di contenuto spettrale variabile: un tono fisso
    produrrebbe un fingerprint degenere, quindi si alternano più note.
    """
    path = tmp_path_factory.mktemp("audio") / "brano_test.wav"
    sample_rate = 44100
    note_hz = [261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 261.63, 196.00]
    frames = bytearray()
    for freq in note_hz:
        for i in range(int(sample_rate * 1.25)):
            value = int(16000 * math.sin(2 * math.pi * freq * i / sample_rate))
            frames += struct.pack("<h", value)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(bytes(frames))
    return path
