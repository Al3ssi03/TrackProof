import psycopg

from app.migrations import apply_migrations
from conftest import TABELLE_FASE_1


def test_migration_crea_le_sole_tabelle_fase1(db_conn: psycopg.Connection):
    rows = db_conn.execute(
        "SELECT table_name FROM information_schema.tables "
        "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
    ).fetchall()
    tabelle = {r[0] for r in rows} - {"schema_migrations"}
    assert tabelle == set(TABELLE_FASE_1)


def test_pgvector_abilitato(db_conn: psycopg.Connection):
    assert (
        db_conn.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'").fetchone()
        is not None
    )


def test_campi_per_transizione_embedding(db_conn: psycopg.Connection):
    """fingerprint_method ed embedding VECTOR(512) esistono anche se v1 usa
    solo Chromaprint (Architettura-tecnica-v1.md sezione 2.2)."""
    for tabella in ("track_fingerprints", "video_fingerprint_windows"):
        tipo = db_conn.execute(
            "SELECT format_type(a.atttypid, a.atttypmod) FROM pg_attribute a "
            "WHERE a.attrelid = %s::regclass AND a.attname = 'embedding'",
            (tabella,),
        ).fetchone()
        assert tipo == ("vector(512)",), tabella

    method = db_conn.execute(
        "SELECT column_name, data_type, column_default FROM information_schema.columns "
        "WHERE table_name = 'track_fingerprints' AND column_name = 'fingerprint_method'"
    ).fetchone()
    assert method is not None
    assert "chromaprint" in method[2]


def test_colonne_con_fk_differita_esistono_senza_vincolo(db_conn: psycopg.Connection):
    """artist_id e *_entity_id esistono da subito, ma le FK verso artists ed
    entities arrivano con le rispettive tabelle (Fase 5 e Fase 3 del piano)."""
    colonne = {
        r[0]
        for r in db_conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'tracks'"
        )
    }
    assert "artist_id" in colonne

    colonne_det = {
        r[0]
        for r in db_conn.execute(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'detections'"
        )
    }
    assert {"dj_entity_id", "venue_entity_id"} <= colonne_det

    fk_esterne = db_conn.execute(
        "SELECT conname FROM pg_constraint "
        "WHERE contype = 'f' AND conrelid IN ('tracks'::regclass, 'detections'::regclass) "
        "AND confrelid NOT IN ('tracks'::regclass, 'scanned_videos'::regclass)"
    ).fetchall()
    assert fk_esterne == []


def test_indici_richiesti_dall_architettura(db_conn: psycopg.Connection):
    indici = {
        r[0]
        for r in db_conn.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
    }
    assert {
        "idx_video_fp_video",
        "idx_detections_track",
        "idx_detections_review_status",
    } <= indici


def test_migration_idempotente(migrated_db: str):
    with psycopg.connect(migrated_db) as conn:
        assert apply_migrations(conn) == []
