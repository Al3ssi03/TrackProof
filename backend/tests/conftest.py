import math
import os
import struct
import wave
from pathlib import Path

import psycopg
import pytest
from psycopg import conninfo

from app.migrations import apply_migrations

TEST_DATABASE_URL = os.environ.get(
    "TRACKPROOF_TEST_DATABASE_URL",
    "postgresql://trackproof:trackproof@localhost:5432/trackproof_test",
)

TABELLE_FASE_1 = (
    "tracks",
    "track_fingerprints",
    "scanned_videos",
    "video_fingerprint_windows",
    "detections",
)


@pytest.fixture(scope="session")
def test_db_url() -> str:
    """Crea il database di test se manca e restituisce il suo URL."""
    params = conninfo.conninfo_to_dict(TEST_DATABASE_URL)
    dbname = params["dbname"]
    admin_url = conninfo.make_conninfo(**{**params, "dbname": "postgres"})
    try:
        with psycopg.connect(admin_url, autocommit=True) as conn:
            exists = conn.execute(
                "SELECT 1 FROM pg_database WHERE datname = %s", (dbname,)
            ).fetchone()
            if not exists:
                conn.execute(f'CREATE DATABASE "{dbname}"')
    except psycopg.OperationalError as exc:
        pytest.fail(
            f"Postgres non raggiungibile ({exc}).\n"
            "Avvia il database locale con: docker compose up -d"
        )
    return TEST_DATABASE_URL


@pytest.fixture(scope="session")
def migrated_db(test_db_url: str) -> str:
    """URL del database di test con tutte le migration applicate."""
    with psycopg.connect(test_db_url) as conn:
        apply_migrations(conn)
    return test_db_url


@pytest.fixture()
def db_conn(migrated_db: str):
    """Connessione al DB di test, con pulizia delle tabelle a fine test."""
    with psycopg.connect(migrated_db) as conn:
        yield conn
        conn.rollback()
        with conn.transaction():
            conn.execute(f"TRUNCATE {', '.join(TABELLE_FASE_1)} CASCADE")


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
