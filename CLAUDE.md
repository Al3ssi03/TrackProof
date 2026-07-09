# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Stato del repository

**Non c'è ancora codice.** Il repo contiene solo i quattro documenti di progetto elencati sotto. Non esiste build system, test runner, `pyproject.toml`, né struttura di cartelle: la Fase 0 del piano di implementazione è ciò che li crea. Non cercare comandi di build/lint/test — vanno introdotti, non trovati.

Documentazione e commit sono in italiano.

## I documenti e come si compongono

I tre documenti si leggono in cascata, ognuno riferisce quello sopra per numero di sezione:

- [PRD-live-detection.md](PRD-live-detection.md) — il **perché**: problema, tier, pricing, rischi. La sezione 11 (rischi tecnici critici) è la più densa di vincoli.
- [Architettura-tecnica-v1.md](Architettura-tecnica-v1.md) — il **cosa**: schema DB, pipeline DETECT, API. Risolve concretamente i rischi 11.1, 11.3 e 11.5 del PRD.
- [Piano-implementazione-v1.md](Piano-implementazione-v1.md) — il **quando**: 7 fasi ordinate, ognuna con un criterio di completamento verificabile.

TrackProof rileva quando un brano di un artista viene suonato in un DJ set pubblico. Tre moduli: **DETECT** (fingerprinting + matching), **RANK** (classifica dei brani), **PROOF** (pagina pubblica press-ready). Solo DETECT è specificato in dettaglio.

## Processo di sviluppo

Questo processo è vincolante. Vale per ogni modifica al codice, non solo per le feature grandi.

### Branching

**Non committare né pushare mai su `main`.** Nessuna eccezione, nemmeno per un fix di una riga o per la documentazione.

`develop` è il branch di integrazione. **Non esiste ancora** — va creato al primo sviluppo:

```bash
git switch -c develop main && git push -u origin develop
```

Ogni sviluppo parte da un branch nuovo creato da `develop`, mai da `main`:

```bash
git switch develop && git pull
git switch -c feat/<slug>     # oppure fix/, refactor/, docs/
```

Se ti accorgi di aver iniziato a lavorare su `main` o `develop`, fermati e sposta il lavoro su un branch prima di committare.

### Il ciclo di ogni modifica

**1. Analisi d'impatto — prima di scrivere codice.** Chi chiama ciò che sto per cambiare? Quali flussi ne dipendono? Cerca i chiamanti, non fidarti della memoria. Elenca esplicitamente i punti a rischio: sono quelli che dovranno essere coperti da test al punto 4. Se il cambiamento tocca la pipeline DETECT, chiediti in particolare se rompe l'invariante dell'indice inverso o la compatibilità dello schema.

**2. TDD.** Test rosso prima dell'implementazione, una slice red-green alla volta. Non scrivere il test dopo per certificare codice già scritto: non è la stessa cosa e non trova gli stessi bug.

**3. Regressione.** Gira la suite **intera**, non solo i test del modulo toccato. Se un test preesistente diventa rosso è una regressione finché non dimostri il contrario. Non aggiornare un test vecchio "perché ora fallisce" — prima spiega perché il comportamento atteso è cambiato, e dillo nella PR.

**4. Nuovi test.** Coprono il nuovo comportamento *e* i punti d'impatto identificati al punto 1.

**5. Code review del diff, prima del commit.** Su due assi: correttezza (bug, casi limite, concorrenza sui job asincroni) e aderenza alla spec (il codice fa ciò che il PRD e l'architettura dicono?).

**6. Documentazione.** Vedi sotto.

I punti 3 e 4 insieme significano: **passano i test vecchi e passano i test nuovi.** Se una delle due metà non è verificata, lo sviluppo non è finito.

> La suite di test non esiste ancora. Il primo ticket che scrive codice di produzione la crea (pytest), altrimenti nulla di questo processo è applicabile.

### La documentazione è parte del deliverable

Ogni PR che cambia il comportamento aggiorna i documenti nella **stessa PR**, non "dopo":

- cambia lo schema DB o la pipeline → [Architettura-tecnica-v1.md](Architettura-tecnica-v1.md)
- cambia comportamento di prodotto, tier, paywall, flusso utente → [PRD-live-detection.md](PRD-live-detection.md)
- completa una fase o ne cambia l'ordine → [Piano-implementazione-v1.md](Piano-implementazione-v1.md), spuntando le checkbox
- cambia una convenzione o un vincolo di processo → questo file

Se una scelta implementativa **contraddice** un documento, non riscrivere il documento in silenzio per farlo tornare: segnala la contraddizione e chiedi. I documenti registrano decisioni prese, e una decisione si cambia consapevolmente.

### Chiusura dello sviluppo

A sviluppo finito e test verdi, **fermati e riporta**: cosa è cambiato, cosa dicono i test, cosa è emerso dalla review. Non aprire la PR.

La PR verso `develop` si apre **solo dopo l'OK esplicito** che lo sviluppo funziona:

```bash
gh pr create --base develop --head feat/<slug>
```

Il merge su `main` avviene solo per rilascio, con una PR `develop → main`, aperta solo su richiesta esplicita.

### Revisione della codebase ogni 50 commit

Ogni 50 commit su `develop` si rivede la codebase nel suo insieme e, se serve, si rifattorizza. Non è facoltativo e non è "quando c'è tempo": è ciò che tiene il codice in uno stato in cui gli agenti riescono a lavorarci.

Conta i commit dall'ultima revisione:

```bash
git rev-list --count last-codebase-review..HEAD   # se il tag esiste
git rev-list --count HEAD                          # la prima volta
```

Se il risultato è ≥ 50, la revisione ha la precedenza sul prossimo sviluppo. Si svolge su un suo branch (`refactor/codebase-review-<n>`) e segue lo stesso ciclo di sopra — il refactoring senza test di regressione verdi non è un refactoring. A merge avvenuto, sposta il tag:

```bash
git tag -f last-codebase-review develop && git push -f origin last-codebase-review
```

Il refactoring **non cambia comportamento**. Se durante la revisione emerge un bug o una feature mancante, non correggerli qui: annotali e trattali come sviluppo a sé.

## Il vincolo che governa tutto: il gate di Fase 1.1

Il rischio più grande del progetto è che Chromaprint **non riesca** a riconoscere un brano dentro un set mixato (EQ, pitch-shift, crossfade). Tutta la roadmap — tier, paywall, notifiche, dashboard, pagina PROOF — poggia su quell'assunto non ancora validato.

Perciò: **non costruire nulla della Fase 2 in poi finché la Fase 1.1 non ha prodotto numeri di precision/recall su set reali.** Se il recall è troppo basso (soglia indicativa 60-70%), si valuta l'alternativa embedding-based (CLAP/OpenL3) *prima* di investire nel resto. Il piano è esplicito: non saltare questo checkpoint per andare più veloci.

Corollario: se ti viene chiesto di implementare auth, tier o UI mentre la Fase 1.1 non è passata, segnalalo invece di procedere in silenzio.

## Principio architetturale: indice inverso di fingerprint

Il design ingenuo — "per ogni brano caricato, scansiona i video" — è **esplicitamente rifiutato** (PRD 11.3): ri-processa gli stessi video man mano che il catalogo cresce.

Il design adottato inverte la direzione:

1. Un video viene fingerprintato **una sola volta** alla scoperta, a finestre scorrevoli (15s, overlap 50%), e finisce in `video_fingerprint_windows`.
2. Un brano caricato viene fingerprintato una sola volta.
3. Il matching è una **query** del fingerprint brano contro l'indice, bidirezionale nel tempo: backfill contro i video già indicizzati al momento dell'upload, poi incrementale contro ogni nuovo video.

Un video già fingerprintato non si ri-processa mai. Qualsiasi modifica alla pipeline che rompe questa proprietà è un regresso, non un'ottimizzazione.

## Schema DB: le decisioni pensate per non essere rifatte

Lo schema (Architettura-tecnica-v1.md sezione 2) va usato **così com'è** anche nella Fase 1, dove serve solo Chromaprint. Tre campi sembrano inutili oggi e non lo sono:

- `fingerprint_method` + `embedding VECTOR(512)` convivono: il passaggio a embedding popola `embedding` senza migrazione distruttiva. È il motivo per cui pgvector va abilitato dalla Fase 0, prima di servire.
- `review_status` + `reviewed_by` coprono sia il flusso v1 (reviewer interno: Ale e il socio) sia il v2 (self-confirm dell'artista). Cambia chi scrive nel campo, non lo schema.
- `audio_deleted_at` su `tracks` implementa la mitigazione del rischio leak sui brani unreleased: il fingerprint non è reversibile in audio, l'audio grezzo si cancella dopo l'estrazione.

Attenzione scrivendo le migration: `detections` referenzia `entities(id)`, ma nel documento `entities` è dichiarata **dopo**. Va creata prima.

## `/internal/test-ingest` è codice di produzione

L'endpoint che valida il matching (`POST /internal/test-ingest`, sezione 3.1) riceve un file audio più la tracklist con timestamp noti, e calcola precision/recall confrontando l'output. Deve girare **lo stesso** codice di fingerprinting e matching che gira in produzione — non una copia, non uno script a parte da buttare. È una decisione deliberata del PRD (sezione 13: DETECT è codice di produzione fin da subito, non uno spike usa-e-getta): il test è credibile solo se misura il codice vero.

Lo stesso endpoint isola due domande distinte che vanno validate separatamente: "il matching funziona?" e "lo scraping trova i video giusti?". Bypassa YouTube apposta.

## Stack (deciso, non ancora scaffoldato)

Python/FastAPI · Postgres + pgvector · Chromaprint via `pyacoustid` · Redis + RQ/Celery per i job asincroni · yt-dlp + YouTube Data API v3 per l'ingestion · Next.js + Supabase Auth sul frontend · Railway/Fly.io per l'hosting MVP.

`pyacoustid` richiede il binario `fpcalc` di Chromaprint installato a livello di sistema, non basta il pacchetto Python. L'ambiente di sviluppo è Windows.

## Trappole ricorrenti

**Le "Fasi" sono due numerazioni diverse.** Le fasi del [Piano-implementazione-v1.md](Piano-implementazione-v1.md) (0 → 6) non sono le fasi della roadmap del PRD sezione 13 (1 → 4). "Fase 3" significa enrichment nel piano e TikTok nel PRD. Il piano stesso avverte di non confonderle: quando citi una fase, dì da quale documento.

**Le notifiche non sono real-time.** Il PRD promette "tempo reale" nelle sezioni 5.1/5.5 ma il matching è batch (rischio 11.4). Il linguaggio corretto, nel prodotto e nel codice, è "entro 24h".

**Il paywall è sui dettagli, non solo sul numero di tracce.** Free vede il *conteggio* delle detection; Pro/Label vedono DJ, venue, città, data, link. Qualunque endpoint che restituisce detection va filtrato per tier — non basta limitare quante tracce si monitorano.

**Ogni fase è un set di commit coerente**, non un unico commit finale.

## Skills

`.agents/skills/` contiene le skill di [mattpocock/skills](https://github.com/mattpocock/skills) (vedi `skills-lock.json`). Claude Code carica le skill da `.claude/skills/`, quindi in questa posizione **non sono invocabili** come slash command finché non vengono spostate o collegate.
