from dataclasses import dataclass
from pathlib import Path

import acoustid

CHROMAPRINT = "chromaprint"


@dataclass(frozen=True)
class Fingerprint:
    """Fingerprint di un file audio, pronto per `track_fingerprints.fingerprint_data`."""

    fingerprint: bytes
    duration_seconds: float
    method: str = CHROMAPRINT


def generate_fingerprint(audio_path: str | Path) -> Fingerprint:
    """Genera il fingerprint Chromaprint di un file audio locale.

    Usa sempre il binario `fpcalc` (richiesto a livello di sistema, vedi
    Architettura-tecnica-v1.md sezione 5): il percorso audioread di pyacoustid
    non è affidabile su Python recenti e non è quello che gira in produzione.
    `fpcalc` viene cercato nella PATH o nella variabile d'ambiente FPCALC.
    """
    duration, fingerprint = acoustid.fingerprint_file(str(audio_path), force_fpcalc=True)
    return Fingerprint(fingerprint=bytes(fingerprint), duration_seconds=float(duration))
