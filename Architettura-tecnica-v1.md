# Architettura Tecnica v1
## Documento di supporto al PRD — TrackProof (nome provvisorio)

**Riferimento:** PRD-live-detection.md
**Scope:** dettaglio implementativo per il modulo DETECT (v1) e struttura dati condivisa con RANK/PROOF.

---

## 1. Principio architetturale chiave: indice inverso di fingerprint

**Problema evitato (vedi PRD sezione 11.3):** processare un video per ogni brano caricato porta a ri-scaricare/ri-processare lo stesso video più volte man mano che cresce il catalogo.

**Soluzione adottata:** i video vengono fingerprintati **una sola volta**, indipendentemente da quanti brani esistono. Il fingerprint del video (a finestre scorrevoli) viene salvato in un indice. Ogni nuovo brano caricato da un artista interroga l'indice esistente (query, non re-scan) e viene anche aggiunto lui stesso all'indice per i video futuri.

```
Flusso corretto:
1. Video scoperto (scraping) → fingerprint del video salvato UNA VOLTA nell'indice
2. Brano caricato da artista → fingerprint del brano generato UNA VOLTA
3. Matching = query del fingerprint brano contro l'indice video (bidirezionale nel tempo):
   a. Contro tutti i video già in indice (backfill, una tantum al momento dell'upload)
   b. Contro ogni nuovo video che entra nell'indice da quel momento in poi (incrementale)
```

Questo dimezza il lavoro: non serve mai ri-processare un video già fingerprintato, solo far girare nuove query contro l'indice esistente.

---

## 2. Schema Database (Postgres + pgvector)

### 2.1 Tabelle core

```sql
-- Artisti
CREATE TABLE artists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    display_name TEXT NOT NULL,
    tier TEXT NOT NULL DEFAULT 'free', -- free | pro | label_agency
    tier_started_at TIMESTAMPTZ,
    trial_pro_used BOOLEAN DEFAULT FALSE, -- ha già usato il trial Pro 14gg?
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Brani caricati (rilasciati o unreleased)
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID REFERENCES artists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    is_released BOOLEAN NOT NULL DEFAULT TRUE,
    audio_storage_path TEXT, -- path S3, cifrato se is_released = FALSE
    audio_deleted_at TIMESTAMPTZ, -- cancellazione post-fingerprinting (vedi rischio leak, PRD 12)
    status TEXT NOT NULL DEFAULT 'processing', -- processing | active | archived
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Fingerprint dei brani (granularità: intero brano, per query contro indice video)
CREATE TABLE track_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id UUID REFERENCES tracks(id) ON DELETE CASCADE,
    fingerprint_data BYTEA NOT NULL, -- output Chromaprint, o vector embedding se si passa a CLAP/OpenL3
    fingerprint_method TEXT NOT NULL DEFAULT 'chromaprint', -- chromaprint | clap | openl3
    embedding VECTOR(512), -- popolato solo se fingerprint_method usa embedding (pgvector)
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Video scansionati (sorgente: YouTube in v1, TikTok/IG isolati in fasi successive)
CREATE TABLE scanned_videos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL, -- youtube | tiktok | instagram
    external_video_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    description TEXT,
    duration_seconds INT,
    uploaded_at TIMESTAMPTZ, -- data pubblicazione originale
    scan_status TEXT NOT NULL DEFAULT 'pending', -- pending | fingerprinted | failed | skipped
    scanned_at TIMESTAMPTZ,
    UNIQUE(source, external_video_id)
);

-- Indice inverso: fingerprint del video a finestre scorrevoli (il cuore dell'ottimizzazione, sezione 1)
CREATE TABLE video_fingerprint_windows (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    video_id UUID REFERENCES scanned_videos(id) ON DELETE CASCADE,
    window_start_seconds NUMERIC NOT NULL,
    window_end_seconds NUMERIC NOT NULL,
    fingerprint_data BYTEA NOT NULL,
    embedding VECTOR(512), -- se si usa fingerprint_method embedding-based
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_video_fp_video ON video_fingerprint_windows(video_id);
-- Se si passa a embedding: CREATE INDEX ON video_fingerprint_windows USING ivfflat (embedding vector_cosine_ops);

-- Detection: risultato del matching brano <-> video
CREATE TABLE detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    track_id UUID REFERENCES tracks(id) ON DELETE CASCADE,
    video_id UUID REFERENCES scanned_videos(id) ON DELETE CASCADE,
    matched_window_start NUMERIC NOT NULL,
    matched_window_end NUMERIC NOT NULL,
    confidence_score NUMERIC NOT NULL, -- 0.0 - 1.0
    dj_entity_id UUID REFERENCES entities(id), -- nullable, risolto via enrichment
    venue_entity_id UUID REFERENCES entities(id), -- nullable
    detected_city TEXT,
    detected_date DATE,
    review_status TEXT NOT NULL DEFAULT 'pending_review',
    -- pending_review | confirmed | rejected (v1: reviewer interno; v2: self-confirm utente)
    reviewed_by TEXT, -- 'internal' (v1) | artist_id (v2)
    reviewed_at TIMESTAMPTZ,
    is_public_on_proof BOOLEAN DEFAULT FALSE, -- solo se review_status = confirmed
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_detections_track ON detections(track_id);
CREATE INDEX idx_detections_review_status ON detections(review_status);

-- Entità DJ/venue risolte (vedi PRD 11.5, entity resolution)
CREATE TABLE entities (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type TEXT NOT NULL, -- dj | venue
    canonical_name TEXT NOT NULL,
    aliases TEXT[] DEFAULT '{}', -- varianti note del nome, popolate via fuzzy matching review
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Notifiche inviate (per audit/debug, non solo invio fire-and-forget)
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID REFERENCES artists(id) ON DELETE CASCADE,
    detection_id UUID REFERENCES detections(id) ON DELETE CASCADE,
    channel TEXT NOT NULL, -- push | email | in_app
    sent_at TIMESTAMPTZ,
    tier_at_send TEXT NOT NULL -- per sapere se conteneva dettagli completi o solo conteggio
);
```

### 2.2 Note sullo schema
- `fingerprint_method` e `embedding` sono pensati per convivere: v1 usa Chromaprint (`fingerprint_data`), un eventuale passaggio a embedding-based (PRD 11.1/11.6) popola `embedding` senza rompere lo schema
- `audio_deleted_at` su `tracks` implementa la mitigazione del rischio leak (PRD, Rischi di prodotto): il file audio grezzo può essere cancellato dopo l'estrazione del fingerprint, mantenendo solo il fingerprint (non reversibile in audio) — da decidere se farlo sempre o solo per `is_released = FALSE`
- `review_status` e `reviewed_by` gestiscono sia il flusso v1 (reviewer interno) sia v2 (self-confirm) senza cambiare schema, solo cambiando chi scrive in quel campo

---

## 3. Pipeline DETECT — passo per passo

```
[INGESTION]
  YouTube Data API (search) → lista candidati video
       ↓
  yt-dlp (download audio) → file audio temporaneo
       ↓
[FINGERPRINTING VIDEO — una tantum per video]
  Sliding window (es. 15s, overlap 50%) → N fingerprint per video
       ↓
  Salvataggio in video_fingerprint_windows
       ↓
  Cancellazione audio grezzo temporaneo (non serve conservarlo, solo il fingerprint)
       ↓
[MATCHING]
  Per ogni brano attivo in track_fingerprints:
    query fingerprint brano contro video_fingerprint_windows del nuovo video
       ↓
  Match sopra soglia minima → riga in detections (review_status = pending_review)
       ↓
[ENRICHMENT]
  NER/regex su title+description del video → estrazione DJ/venue/città/data candidati
       ↓
  Fuzzy match contro tabella entities → collegamento o creazione nuova entità
       ↓
[REVIEW]
  v1: coda interna (Ale + socio), SLA 48-72h
  v2: notifica + card nell'app, self-confirm dall'artista
       ↓
[NOTIFICA]
  Su transizione review_status → confirmed (o su nuova detection proposta in v2)
       ↓
[ESPOSIZIONE]
  confirmed + is_public_on_proof = TRUE → visibile su dashboard e pagina PROOF pubblica
```

### 3.1 Percorso di test del socio (bypass scraping)

Per il test di validazione descritto nel PRD (sezione 11.1, 13): un endpoint interno permette di saltare l'ingestion da YouTube e iniettare direttamente un set audio con ground truth nota.

```
POST /internal/test-ingest
Body: {
  audio_file: <file>,
  known_tracklist: [
    { track_id: "...", expected_start_seconds: 750, expected_end_seconds: 960 }
  ]
}
```

Questo endpoint:
1. Fa girare lo stesso fingerprinting a finestre scorrevoli usato in produzione (stesso codice di `[FINGERPRINTING VIDEO]`)
2. Fa girare lo stesso matching (`[MATCHING]`)
3. Confronta l'output con `known_tracklist` fornita, calcola precision/recall automaticamente
4. Non richiede scraping YouTube — isola il test del motore di matching

Vantaggio: è codice di produzione riusato per il test, non uno script a parte da buttare (coerente con la decisione presa nel PRD).

---

## 4. API design (bozza endpoint principali)

```
POST   /artists                        — registrazione artista
POST   /tracks                         — upload brano (rilasciato o unreleased)
GET    /tracks/:id/detections          — lista detection per un brano (filtrata per tier)
POST   /detections/:id/confirm         — self-confirm (v2)
POST   /detections/:id/reject          — self-confirm (v2)
GET    /artists/:id/proof-page         — dati per la pagina pubblica PROOF
POST   /internal/test-ingest           — endpoint di test descritto in 3.1 (solo Ale/socio, non pubblico)
POST   /internal/review/:detection_id  — conferma/rifiuto reviewer interno (v1)
```

---

## 5. Stack tecnologico (riferimento da PRD sezione 9)

- **Backend:** Python/FastAPI
- **Fingerprinting v1:** Chromaprint via `pyacoustid`
- **DB:** Postgres + pgvector (per supportare fin da subito un eventuale passaggio a embedding, sezione 2.1)
- **Storage audio grezzo:** S3-compatibile, cifrato per `is_released = FALSE`
- **Queue:** Redis + RQ/Celery per job asincroni (fingerprinting, matching, enrichment)
- **Frontend:** Next.js + Supabase Auth
- **Hosting MVP:** Railway/Fly.io

---

## 6. Cosa NON è ancora coperto da questo documento

- Dettaglio del modello di embedding alternativo (CLAP/OpenL3) — da specificare solo se lo spike di validazione (sezione 3.1) mostra che Chromaprint non basta
- Design dettagliato dello scraper TikTok/Instagram (fuori scope v1, PRD Fase 3/4)
- Meccanica esatta di billing/subscription (Stripe o altro) — da trattare in un documento separato quando si implementa il pricing (PRD sezione 6)
