from pathlib import Path

import psycopg

MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"


def apply_migrations(
    conn: psycopg.Connection, migrations_dir: Path = MIGRATIONS_DIR
) -> list[str]:
    """Applica in ordine di nome le migration .sql non ancora registrate.

    Ogni migration gira in una transazione insieme alla riga che la registra
    in schema_migrations: o si applica tutta, o non risulta applicata.
    Restituisce i nomi dei file applicati in questa esecuzione.
    """
    with conn.transaction():
        conn.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations ("
            "  filename TEXT PRIMARY KEY,"
            "  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            ")"
        )
    applicate = {
        r[0] for r in conn.execute("SELECT filename FROM schema_migrations")
    }
    nuove: list[str] = []
    for sql_file in sorted(migrations_dir.glob("*.sql")):
        if sql_file.name in applicate:
            continue
        with conn.transaction():
            conn.execute(sql_file.read_text(encoding="utf-8"))
            conn.execute(
                "INSERT INTO schema_migrations (filename) VALUES (%s)",
                (sql_file.name,),
            )
        nuove.append(sql_file.name)
    return nuove


if __name__ == "__main__":
    from app.db import connect

    with connect() as conn:
        applicate = apply_migrations(conn)
    if applicate:
        print("Migration applicate:", ", ".join(applicate))
    else:
        print("Nessuna migration da applicare.")
