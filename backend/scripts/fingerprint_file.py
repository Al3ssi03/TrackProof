"""Script di test manuale: fingerprint di un file audio locale salvato su Postgres.

Uso (dalla cartella backend, con il venv attivo):
    python scripts/fingerprint_file.py <percorso-audio> [titolo]

Richiede il DB locale attivo (docker compose up -d) e le migration applicate
(python -m app.migrations). Riusa lo stesso codice di produzione dei test.
"""

import sys
from pathlib import Path

from app.db import connect
from app.fingerprinting import generate_fingerprint
from app.repository import save_track_fingerprint


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    audio_path = Path(sys.argv[1])
    titolo = sys.argv[2] if len(sys.argv) > 2 else audio_path.stem

    fp = generate_fingerprint(audio_path)
    with connect() as conn:
        track_id, fingerprint_id = save_track_fingerprint(conn, titolo, fp)

    print(f"Brano '{titolo}' ({fp.duration_seconds:.1f}s)")
    print(f"  track_id:       {track_id}")
    print(f"  fingerprint_id: {fingerprint_id}")


if __name__ == "__main__":
    main()
