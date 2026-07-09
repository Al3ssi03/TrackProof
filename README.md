# TrackProof
Rileva automaticamente quando un brano di un artista viene suonato in un set/video pubblico (YouTube, TikTok, IG)

## Sviluppo locale

Prerequisiti:

- Python 3.14+
- Docker (per il Postgres locale)
- il binario `fpcalc` di Chromaprint a livello di sistema: `winget install AcoustID.Chromaprint`
  (poi riaprire il terminale; in alternativa impostare la variabile d'ambiente `FPCALC`
  con il percorso completo dell'eseguibile)

Setup:

```powershell
docker compose up -d                      # Postgres 17 + pgvector sulla porta 5432

cd backend
python -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
.venv\Scripts\python -m app.migrations    # applica le migration al DB applicativo
```

Test (suite completa, include i test di integrazione su Postgres):

```powershell
.venv\Scripts\python -m pytest
```

I test di integrazione usano un database separato (`trackproof_test`), creato
automaticamente alla prima esecuzione. Le variabili d'ambiente utili sono in
`.env.example`.

Prova manuale del fingerprinting (riusa il codice di produzione):

```powershell
.venv\Scripts\python scripts\fingerprint_file.py <percorso-audio> [titolo]
```
