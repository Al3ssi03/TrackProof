# Piano di Implementazione v1
## Documento di supporto al PRD e all'Architettura Tecnica — TrackProof (nome provvisorio)

**Scopo:** ordine di costruzione concreto, pensato per essere seguito passo-passo da un agente di coding (Claude Code). Ogni fase ha un obiettivo chiaro e un criterio di completamento verificabile, così si può procedere in modo incrementale senza costruire cose che dipendono da parti non ancora validate.

**Riferimenti:** PRD-live-detection.md, Architettura-tecnica-v1.md

**Principio guida (PRD sezione 11.1 e 13):** il modulo DETECT si valida PRIMA di costruire tier, paywall, notifiche, dashboard, pagina PROOF. Se il matching non regge, si cambia approccio (embedding-based) prima di investire nel resto.

---

## Fase 0 — Setup progetto

**Obiettivo:** ambiente pronto, nessuna feature ancora.

- [ ] Repo con struttura backend (FastAPI) + cartella per script di test
- [ ] Postgres locale/cloud con estensione pgvector abilitata
- [ ] Schema DB da Architettura-tecnica-v1.md sezione 2 (solo le tabelle necessarie per Fase 1: `tracks`, `track_fingerprints`, `scanned_videos`, `video_fingerprint_windows`, `detections` — le altre tabelle si aggiungono quando servono, non subito)
- [ ] `pyacoustid` installato e funzionante (test: fingerprint di un file audio locale)

**Criterio di completamento:** si riesce a generare un fingerprint Chromaprint da un file audio locale e salvarlo in DB.

---

## Fase 1 — Modulo DETECT core (nessuna UI, nessun tier, nessuna auth)

**Obiettivo:** il motore di matching funziona ed è testabile in isolamento.

- [ ] Funzione: genera fingerprint di un brano intero (`track_fingerprints`)
- [ ] Funzione: genera fingerprint a finestre scorrevoli di un audio lungo (`video_fingerprint_windows`) — parametri configurabili (durata finestra, overlap), partire da 15s/50% come da Architettura-tecnica-v1.md
- [ ] Funzione: matching di un fingerprint brano contro le finestre di un audio lungo, con soglia di confidence configurabile
- [ ] Endpoint interno `/internal/test-ingest` (Architettura-tecnica-v1.md sezione 3.1): riceve audio + tracklist nota, fa girare fingerprinting + matching, restituisce precision/recall calcolati automaticamente confrontando output con la tracklist fornita

**Criterio di completamento:** dato un file audio e una tracklist nota (anche finta/di test), l'endpoint restituisce un report precision/recall. Non serve ancora che sia accurato — deve solo funzionare end-to-end.

**Non fare in questa fase:** scraping YouTube, autenticazione utenti, dashboard, notifiche, tier/pricing. Sono tutti a valle della validazione.

---

## Fase 1.1 — Validazione con i set reali del socio (gate decisionale)

**Obiettivo:** rispondere alla domanda "il matching funziona abbastanza bene?" prima di andare avanti.

- [ ] Il socio fornisce 5-10 set audio reali + tracklist con timestamp (ground truth)
- [ ] Caricare ogni set tramite `/internal/test-ingest`
- [ ] Aggregare i risultati: precision/recall medi su tutti i set, con attenzione ai casi peggiori (set con mix aggressivo/EQ pesante)

**Gate decisionale (da fissare prima di vedere i risultati, per non auto-ingannarsi):**
- Se recall e precision sono a un livello accettabile (soglia indicativa da discutere, es. >60-70% su recall) → si procede con Chromaprint in v1
- Se sono troppo bassi → si valuta l'alternativa embedding-based (CLAP/OpenL3) PRIMA di passare alla Fase 2, aggiornando `fingerprint_method` ed `embedding` come già previsto nello schema (Architettura-tecnica-v1.md sezione 2.2, pensato apposta per questo)

**Questa fase è un checkpoint, non solo un task:** non si passa alla Fase 2 senza aver guardato questi numeri.

---

## Fase 2 — Integrazione scraping YouTube reale

**Obiettivo:** collegare il motore DETECT (già validato) a video reali scoperti automaticamente.

- [ ] YouTube Data API: ricerca video per query mirate (es. "DJ set", nomi venue/festival noti)
- [ ] yt-dlp: download audio dei video candidati
- [ ] Pipeline di fingerprinting video (riusa la Fase 1, solo cambia la sorgente audio: da upload manuale a download YouTube)
- [ ] Salvataggio in `scanned_videos` + `video_fingerprint_windows`
- [ ] Cancellazione audio grezzo temporaneo dopo il fingerprinting (non serve conservarlo)
- [ ] Gestione quota YouTube: logging del consumo quota, per capire quanto margine resta rispetto al limite giornaliero (PRD sezione 10)

**Criterio di completamento:** un brano caricato genera detection reali su video YouTube trovati automaticamente, non solo su file audio caricati a mano.

---

## Fase 3 — Enrichment + entity resolution

**Obiettivo:** le detection hanno metadata utili (DJ, venue, città, data), non solo un timestamp.

- [ ] Estrazione NER/regex da titolo+descrizione video
- [ ] Tabella `entities` (Architettura-tecnica-v1.md sezione 2.1) + fuzzy matching per unificare varianti dello stesso DJ/venue (PRD sezione 11.5)
- [ ] Collegamento detection → entità risolte

**Criterio di completamento:** una detection mostra DJ/venue/città in modo leggibile, con varianti dello stesso nome unificate correttamente nella maggior parte dei casi.

---

## Fase 4 — Revisione interna (v1) + prime API per dashboard

**Obiettivo:** Ale e il socio possono rivedere le detection prima che diventino visibili.

- [ ] Endpoint `/internal/review/:detection_id` (conferma/rifiuto)
- [ ] Stato `review_status` aggiornato correttamente, `is_public_on_proof` settato solo su conferma
- [ ] API minime per far vedere le detection confermate (base per la dashboard vera, Fase 6)

**Criterio di completamento:** un ciclo completo funziona: detection trovata → revisionata manualmente → confermata → visibile via API.

---

## Fase 5 — Autenticazione, tier, paywall

**Obiettivo:** introdurre artisti reali, non solo test interni.

- [ ] Auth (Supabase Auth o equivalente)
- [ ] Tabella `artists` con campo `tier`
- [ ] Logica paywall: limite tracce per tier, dettagli detection filtrati per tier (PRD sezione 6)
- [ ] Trial Pro 14gg (campo `trial_pro_used`)

**Criterio di completamento:** un utente Free vede solo conteggio, un utente Pro vede dettagli completi, coerente con la tabella tier del PRD.

---

## Fase 6 — Dashboard, notifiche, pagina PROOF, UI/UX

**Obiettivo:** prodotto completo secondo PRD sezioni 5.4, 5.5, 5.3, 14.

- [ ] Frontend Next.js: dashboard artista con card di detection (design curato, PRD sezione 14)
- [ ] Notifiche push/email su nuova detection
- [ ] Pagina pubblica PROOF (`/artist/:slug`)
- [ ] Paywall visivo (blur/lucchetto sui dettagli bloccati)

**Criterio di completamento:** un artista reale può fare l'intero percorso da solo — upload, notifica, dashboard, condivisione pagina PROOF — senza intervento manuale di Ale/socio (a parte la revisione interna della Fase 4, ancora attiva in v1).

---

## Fasi successive (fuori da questo piano v1)

- Transizione a self-confirm utente (v2) — trigger: superamento soglia ~100-150 utenti (PRD sezione 10)
- TikTok scraping (Fase 3 del PRD, non di questo piano — nomi di fase diversi, attenzione a non confonderli)
- Instagram scraping + eventuale passaggio a embedding-based matching su larga scala

---

## Note per Claude Code

- Ogni fase è pensata per essere un set di commit/PR coerente, non tutto insieme
- Non saltare la Fase 1.1 (gate decisionale) per andare più veloci — è il punto in cui si decide se l'approccio tecnico regge, saltarlo vuol dire rischiare di costruire Fase 2-6 su fondamenta non validate
- Lo schema DB in Architettura-tecnica-v1.md è già pensato per assorbire un eventuale cambio di `fingerprint_method` senza migrazioni distruttive — usarlo così com'è anche se in Fase 1 si usa solo Chromaprint
