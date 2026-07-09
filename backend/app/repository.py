from uuid import UUID

import psycopg

from app.fingerprinting import Fingerprint


def save_track_fingerprint(
    conn: psycopg.Connection, title: str, fingerprint: Fingerprint
) -> tuple[UUID, UUID]:
    """Crea un brano e il suo fingerprint in un'unica transazione.

    Restituisce (track_id, fingerprint_id).
    """
    with conn.transaction():
        track_id = conn.execute(
            "INSERT INTO tracks (title) VALUES (%s) RETURNING id",
            (title,),
        ).fetchone()[0]
        fingerprint_id = conn.execute(
            "INSERT INTO track_fingerprints (track_id, fingerprint_data, fingerprint_method) "
            "VALUES (%s, %s, %s) RETURNING id",
            (track_id, fingerprint.fingerprint, fingerprint.method),
        ).fetchone()[0]
    return track_id, fingerprint_id
