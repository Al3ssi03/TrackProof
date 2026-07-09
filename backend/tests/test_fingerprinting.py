from pathlib import Path

from app.fingerprinting import generate_fingerprint


def test_genera_fingerprint_chromaprint_da_file_locale(audio_wav: Path):
    result = generate_fingerprint(audio_wav)

    assert result.method == "chromaprint"
    assert isinstance(result.fingerprint, bytes)
    assert len(result.fingerprint) > 0
    assert 9.0 < result.duration_seconds < 11.0  # il WAV di test dura ~10s


def test_fingerprint_deterministico_sullo_stesso_file(audio_wav: Path):
    prima = generate_fingerprint(audio_wav)
    seconda = generate_fingerprint(audio_wav)
    assert prima.fingerprint == seconda.fingerprint
