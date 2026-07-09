from pathlib import Path

import psycopg

from app.fingerprinting import generate_fingerprint
from app.repository import save_track_fingerprint


def test_fingerprint_da_file_locale_salvato_su_postgres(
    db_conn: psycopg.Connection, audio_wav: Path
):
    """Criterio di completamento della Fase 0 (Piano-implementazione-v1.md):
    da un file audio locale si genera un fingerprint Chromaprint
    e lo si salva su Postgres."""
    fp = generate_fingerprint(audio_wav)

    track_id, fingerprint_id = save_track_fingerprint(
        db_conn, title="Brano di test", fingerprint=fp
    )

    row = db_conn.execute(
        "SELECT t.title, tf.fingerprint_data, tf.fingerprint_method, tf.embedding "
        "FROM track_fingerprints tf JOIN tracks t ON t.id = tf.track_id "
        "WHERE tf.id = %s AND t.id = %s",
        (fingerprint_id, track_id),
    ).fetchone()

    assert row is not None
    title, data, method, embedding = row
    assert title == "Brano di test"
    assert bytes(data) == fp.fingerprint
    assert method == "chromaprint"
    assert embedding is None  # v1 usa solo Chromaprint: embedding resta vuoto
