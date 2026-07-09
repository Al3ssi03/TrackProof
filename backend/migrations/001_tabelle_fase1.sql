-- Fase 0: sole tabelle necessarie alla Fase 1 (Architettura-tecnica-v1.md sezione 2.1).
-- Scostamenti deliberati dal documento (motivati in sezione 2.3):
--   * tracks.artist_id senza FK: artists arriva in Fase 5 del piano.
--   * detections.dj_entity_id / venue_entity_id senza FK: entities arriva in Fase 3.
-- Le colonne esistono già, i vincoli si aggiungono con le rispettive tabelle.

-- pgvector abilitato da subito: assorbe l'eventuale passaggio a embedding
-- (CLAP/OpenL3) senza migration distruttiva.
CREATE EXTENSION IF NOT EXISTS vector;

-- Brani caricati (rilasciati o unreleased)
CREATE TABLE tracks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID, -- FK verso artists(id) da aggiungere in Fase 5
    title TEXT NOT NULL,
    is_released BOOLEAN NOT NULL DEFAULT TRUE,
    audio_storage_path TEXT, -- path S3, cifrato se is_released = FALSE
    audio_deleted_at TIMESTAMPTZ, -- cancellazione post-fingerprinting (rischio leak, PRD 12)
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

-- Video scansionati (sorgente: YouTube in v1, TikTok/IG in fasi successive)
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

-- Indice inverso: fingerprint del video a finestre scorrevoli (sezione 1)
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
    dj_entity_id UUID, -- FK verso entities(id) da aggiungere in Fase 3 (enrichment)
    venue_entity_id UUID, -- come sopra
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
