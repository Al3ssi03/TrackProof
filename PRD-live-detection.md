# PRD — [Nome provvisorio: "TrackProof"]
## Product Requirements Document v0.1

**Autore:** Ale
**Data:** Luglio 2026
**Status:** Draft

---

## 1. Problema

Gli artisti (produttori/DJ) non hanno visibilità su **dove e quando** i loro brani vengono suonati live da altri DJ (set club, festival, radio, contenuti social). Questa informazione oggi:

- Non esiste in forma strutturata (nessuna piattaforma la aggrega)
- È dispersa su YouTube (DJ set upload), TikTok, Instagram Reels
- Ha valore concreto: prova di trazione per booking agent, label, sponsor, press kit

**Chi soffre il problema:** produttori emergenti/mid-tier che vogliono dimostrare trazione reale (non solo stream Spotify) a label, agenzie, promoter.

---

## 2. Obiettivo del prodotto

Costruire una piattaforma che:
1. **Rileva** automaticamente quando un brano di un artista viene suonato in un set/video pubblico (YouTube, TikTok, IG)
2. **Arricchisce** la detection con metadata (DJ, venue, città, data)
3. **Aggrega** i dati in un ranking/dashboard per l'artista
4. **Espone** una pagina pubblica "press-ready" con le prove verificate

Modellato sui 3 moduli di Seen Live: **DETECT** (ex-ID), **RANK** (ex-FLOOR), **PROOF** (ex-PRESS).

---

## 3. Non-goals (fuori scope v1)

- Non facciamo licensing/royalty collection (non è un PRO/collecting society)
- Non copriamo radio terrestre/broadcast TV
- Non facciamo detection real-time (batch è accettabile in v1)
- Non copriamo Spotify/streaming (già coperto da altri tool, non è il nostro differenziale)

---

## 4. Utenti target

| Persona | Bisogno |
|---|---|
| Produttore emergente (house/tech house) | Vuole prove concrete di trazione live per pitch a label/booking |
| Music manager/label A&R | Vuole monitorare più artisti del roster in un colpo solo |
| Booking agent | Vuole vedere in quali città/venue un artista "gira" già organicamente |

---

## 5. Funzionalità v1 (MVP da lanciare)

### 5.1 DETECT
- Upload brano (audio file) da parte dell'artista → generazione fingerprint. **Accettati sia brani già pubblicati/distribuiti che unreleased** (non ancora usciti su piattaforme streaming) — utile soprattutto per artisti che vogliono monitorare reazioni live prima del rilascio ufficiale
- Scansione automatica YouTube (query mirate: "DJ set", "live set", nomi venue/festival noti) via YouTube Data API + yt-dlp
- Matching fingerprint su audio dei set scansionati (finestra scorrevole, non intero video)
- Output: lista detection con video, timestamp, confidence score
- **Notifica push/email in tempo reale** ad ogni nuova detection rilevata (o proposta, in v2 self-confirm) — è il momento di massimo engagement, va sfruttato subito

**Fuori scope MVP:** TikTok e Instagram (vedi sezione Rischi — si aggiungono in v1.1/v1.2 come moduli isolati)

### 5.2 RANK
- Punteggio per brano basato su: numero detection, "peso" del DJ/venue (se riconoscibile), recency
- Classifica interna per artista (quali brani performano meglio live)

### 5.3 PROOF
- Pagina pubblica per artista (`trackproof.com/artist/nomeartista`)
- Mostra detection verificate: DJ, venue/evento, città, data, link al video
- Pensata per essere linkata in press kit / bio / EPK

### 5.4 Dashboard artista
- Login, upload brani, visualizzazione detection, export (PDF/immagine) per press kit
- **Card di detection nella dashboard**, contenuto variabile in base al tier (coerente col paywall di sezione 6):
  - Free: card con conteggio detection e brano, senza dettagli
  - Pro/Label: card completa con DJ, venue, città, data, link video, azione conferma/rifiuto (v2)
- Le card servono anche da elemento di **upsell visivo**: sul tier Free, la card mostra chiaramente cosa si sta perdendo (es. dettagli sfocati/bloccati con icona lucchetto) per spingere all'upgrade

### 5.5 Notifiche
- Notifica (push mobile se c'è un'app, altrimenti email/in-app) ogni volta che il sistema rileva una nuova detection
- Contenuto della notifica coerente col tier: free riceve "Abbiamo trovato una detection sul tuo brano X" (generico, spinge ad aprire l'app e vedere l'upsell); Pro/Label ricevono già DJ/venue nel testo della notifica stessa
- Le notifiche sono anche un driver di retention: motivo per tornare nell'app anche settimane dopo l'upload iniziale

---

## 6. Pricing model (v1)

**Filosofia:** freemium **permanente** (non trial a tempo). Il valore di questo prodotto (detection che si accumulano nel tempo su YouTube/TikTok/IG) si manifesta gradualmente — un trial a giorni rischia di scadere prima che l'utente veda risultati concreti, bruciando l'acquisizione. Meglio un free tier stabile che genera valore reale nel tempo e diventa anche canale di marketing (vedi Growth Loop).

### Struttura tier

| Tier | Prezzo indicativo | Tracce monitorate | Dettagli detection | Pagina PROOF pubblica |
|---|---|---|---|---|
| **Free** | €0 | 3 | Solo conteggio (es. "4 detection trovate") | Sì, visibile ma con dati limitati |
| **Pro** | ~€9-15/mese | 10-15 | Completi: DJ, venue, città, data, link video + export press kit | Sì, completa |
| **Label/Agency** | ~€30-50/mese | Illimitate, multi-artista | Completi + dashboard aggregata multi-artista | Sì, completa per ogni artista |

*Prezzi indicativi da validare con interviste a 5-10 produttori target prima di fissarli definitivamente.*

### Paywall sui dettagli, non solo sul numero di tracce

Il limite non è solo "quante tracce puoi monitorare" ma anche "quanto vedi delle detection":
- **Free:** l'utente vede che ci sono state detection (numero), ma non sa quali DJ/venue/città — crea curiosità (pattern tipo "chi ha visto il tuo profilo" su LinkedIn)
- **Pro/Label:** sblocca i dettagli completi, cioè esattamente ciò che serve per costruire un press kit — è il vero valore che si vende

### Trial (solo sul piano Pro, non sul limite free)

Niente trial generico a tempo sul free tier. Invece: **"Prova Pro gratis per 14 giorni"** — accesso temporaneo a più tracce monitorate + dettagli completi. Alla scadenza, l'account torna al tier Free (3 tracce, solo conteggio). Questo converte meglio del trial isolato perché l'utente vede concretamente cosa perde tornando indietro (loss aversion) invece di sperimentare un trial scollegato dal prodotto reale.

### Growth loop: la pagina PROOF come canale marketing

La pagina pubblica PROOF resta **visibile e gratuita anche nel tier Free** (con dati limitati, coerente col paywall sopra). Motivo: gli artisti la condividono in bio/social/press kit, generando traffico organico verso il prodotto. Il free tier quindi non è solo un costo di acquisizione ma un canale di crescita attivo — ogni artista free che condivide la sua pagina PROOF porta nuovi visitatori/potenziali utenti.

### Da chiarire prima di implementare
- Prezzi esatti dei tier (validare con interviste target)
- Definizione precisa di "traccia monitorata" (slot fisso o rotazione se sostituisci un brano?)
- Limiti esatti tier Label/Agency (numero artisti gestibili, seat multipli?)
- Meccanica di downgrade a fine trial Pro: cosa succede alle tracce oltre il limite Free (restano archiviate ma nascoste, o si perdono?)

---

## 7. Revisione delle detection

### V1: revisione interna su brani test
In v1, Ale e il socio testano il sistema **con un set di brani di prova** (non ancora artisti reali paganti), revisionando manualmente le detection per validare l'affidabilità del matching prima di esporre il prodotto a utenti veri.

- **SLA di revisione: 48-72h lavorative** dalla detection alla revisione — target interno, serve a validare che il fingerprinting funzioni bene prima del lancio pubblico
- Obiettivo v1: capire il tasso di falsi positivi/negativi reali, calibrare le soglie di confidence, prima di fidarsi del sistema con utenti paganti

### V2: conferma da parte dell'utente (self-serve)
Una volta validato il sistema in v1, la revisione passa da "controllo interno" a **conferma da parte dell'artista stesso**:

**Flusso proposto:**
1. Il matching engine rileva una possibile detection con confidence score
2. Solo le detection sopra una soglia minima (es. >70-80%, da calibrare in v1) vengono mostrate all'utente — sotto soglia, scartate automaticamente per non intasare l'utente di rumore
3. L'utente vede la detection proposta (video, timestamp, DJ/venue se riconosciuti) e conferma o rifiuta con un click ("È il mio brano" / "Non è il mio brano")
4. Solo le detection **confermate dall'utente** diventano visibili come "verificate" in dashboard e sulla pagina pubblica PROOF
5. Le detection rifiutate vengono usate come feedback per migliorare la soglia di confidence nel tempo (utile anche per un futuro modello di scoring più intelligente)

**Perché funziona meglio della revisione interna a scala:**
- Elimina il collo di bottiglia dei 2 founder come reviewer manuali su ogni singolo utente
- L'artista è la persona più qualificata per riconoscere il proprio brano (anche versioni remixate/pitchate che un algoritmo potrebbe non essere sicuro al 100%)
- Il feedback (conferma/rifiuto) diventa dato utile per migliorare il modello nel tempo

**Da definire per v2:**
- Soglia minima di confidence sotto cui non si mostra nemmeno la proposta (per non generare rumore/sfiducia)
- Cosa succede se l'utente non risponde mai a una detection proposta (resta "in sospeso" per sempre? scade dopo X giorni e viene scartata?)
- Serve comunque un controllo anti-abuso? (es. un utente che conferma detection non sue per gonfiare il proprio ranking FLOOR — da valutare se serve un controllo random/spot-check anche in v2)

---

## 8. Metriche di successo

- **Attivazione:** % artisti che completano upload + ricevono almeno 1 detection entro 30gg
- **Precisione:** % detection confermate manualmente corrette (target iniziale >85%)
- **Copertura:** numero video scansionati/settimana, numero brani in catalogo
- **Retention:** % artisti che tornano a controllare la dashboard entro 14gg da una nuova detection

---

## 9. Architettura tecnica (riferimento sintetico)

- **Ingestion:** YouTube Data API v3 + yt-dlp (v1); TikTok/IG scraper isolati (v1.1+)
- **Fingerprinting:** Chromaprint/AcoustID per MVP → valutare embedding custom (CLAP/OpenL3 + pgvector) se precisione insufficiente su audio mixato
- **Storage:** Postgres + pgvector, S3 per audio grezzo temporaneo
- **Queue/jobs:** Redis + RQ/Celery per scraping e fingerprinting asincroni
- **Backend:** Python/FastAPI
- **Frontend:** Next.js + Supabase Auth
- **Hosting MVP:** Railway/Fly.io

*(Dettaglio schema DB e pipeline: documento separato "Architettura tecnica v1")*

---

## 10. Costi stimati e scalabilità

Stima dei costi di scraping/infrastruttura per fascia di utenti attivi. Numeri indicativi, da validare con test reali su piccola scala prima di impegnare budget.

**Assunzioni di base:**
- Mix tier realistico: maggioranza Free (3 tracce), quota che converte a Pro (10-15 tracce) → media stimata ~3.5 tracce monitorate/utente
- Ogni traccia viene ri-scansionata periodicamente nel tempo, non solo all'upload
- Costo proxy TikTok/IG stimato a ~€5/GB medio (range reale $1-8/GB a seconda di provider/volume — vedi sezione Rischi)
- YouTube resta gratis in euro ma soggetto al tetto di ~100 ricerche/giorno (quota Google)

| Utenti | Tracce monitorate (stima) | Video scansionati/giorno | Banda TikTok/IG (GB/mese) | Costo proxy (€/mese) | Hosting/infra (€/mese) | YouTube quota | Revisione | **Totale stimato/mese** |
|---|---|---|---|---|---|---|---|---|
| **10** | ~35 | 50-100 | 15-30 | 75-150 | 20-50 | OK, ampio margine | Manuale (Ale + socio, v1) | **~€100-250** |
| **100** | ~350 | 300-500 | 90-150 | 450-750 | 100-200 | OK con caching/batching query | Manuale, ancora gestibile ma cresce | **~€600-1.050** |
| **200** | ~700 | 600-1.000 | 180-300 | 900-1.500 | 200-400 | Vicino al limite, serve ottimizzare o valutare estensione | Diventa collo di bottiglia → **soglia critica per passare a v2 self-confirm** | **~€1.200-2.200** |
| **1000** | ~3.500 | 2.500-4.000 | 750-1.200 | 2.500-4.000* | 800-2.000 | Serve estensione quota o API terza a pagamento | Deve essere già v2 self-confirm, impossibile a mano | **~€4.000-8.000** |

*A 1000 utenti il volume permette sconti di fascia (es. Bright Data scende a ~€2,50/GB oltre i 700GB/mese), quindi il proxy costa meno per GB rispetto ai tier più piccoli.

**Insight chiave:** tra 100 e 200 utenti si attraversano due soglie critiche insieme — il limite di quota YouTube e la sostenibilità della revisione manuale. Questo conferma che il passaggio a v2 (self-confirm, vedi sezione 7) non è solo una scelta di prodotto ma **una necessità di costo/scalabilità** che arriva prima di quanto ci si aspetterebbe. Vale la pena avere v2 pronto prima di superare i 100-150 utenti attivi, non dopo.

**Scenario realistico atteso per il lancio iniziale:** il socio (DJ) testerà il sistema su se stesso, poi l'app verrà data alla sua cerchia di DJ pugliesi — presumibilmente **non oltre ~100 utenti** in questa fase. Questo significa che, salvo crescita oltre il giro di conoscenze iniziale, i costi realistici restano nella fascia **€100-1.050/mese** (righe 10-100 utenti della tabella), e la revisione manuale (Ale + socio) resta sostenibile più a lungo del previsto. La soglia critica dei 100-150 utenti per v2 self-confirm diventa quindi un **traguardo da tenere pronto se/quando si decide di aprire oltre la cerchia iniziale**, non un'urgenza immediata — ma vale la pena non perderla di vista se il prodotto funziona e nasce la tentazione di allargare organicamente (es. il classico passaparola tra DJ che porta oltre le aspettative iniziali).

---

## 11. Rischi tecnici critici (analisi da senior architect)

Punti emersi da un'analisi architetturale del PRD — separati dai rischi di prodotto (sezione 12) perché, se non risolti, invalidano l'intero progetto invece di richiedere solo un aggiustamento.

### 11.1 Il matching su audio "sporco" non è ancora validato — è il rischio più grande del progetto
Tutta la roadmap (pricing, UI/UX, notifiche, tier) è costruita sull'assunto che Chromaprint/AcoustID riesca a riconoscere un brano dentro un DJ set live (audio mixato, EQ, pitch-shift, crossfade, key change armonico). È un caso molto più difficile del classico "Shazam" su audio pulito. Se il matching non regge, nessun'altra parte del prodotto ha senso.

**Mitigazione concreta e già disponibile:** il socio (DJ) testerà il sistema — non con uno spike separato da buttare, ma caricando i propri set audio **direttamente nel modulo DETECT** (bypassando temporaneamente lo scraping YouTube), con ground truth nota (lui sa quali brani ha suonato, quando, con quali transizioni). Questo isola "il matching funziona?" da "lo scraping trova i video giusti?" — due problemi diversi da validare separatamente, sullo stesso codice che finirà in produzione. Se il tasso di falsi negativi è alto con Chromaprint, va valutata l'alternativa embedding-based (CLAP/OpenL3) **prima** di costruire sopra dashboard, tier, notifiche, paywall.

### 11.2 Rischio legale non limitato a TikTok/IG
Il PRD (sezione 12, Rischi di prodotto) tratta il rischio ToS come circoscritto a TikTok/Instagram. In realtà anche su YouTube: scaricare video con yt-dlp per uso commerciale, conservare contenuti scaricati, e costruire un prodotto a pagamento sopra dati derivati da scraping violano potenzialmente anche i Termini di Servizio di YouTube (che vietano download automatizzato e uso per servizi derivati/concorrenti). È un rischio strutturale a tutto il modulo DETECT, non solo ai moduli v1.1+. Consigliata una consulenza legale leggera (1-2h con un legale IP/tech) prima del lancio anche solo alla cerchia di conoscenti, per capire l'esposizione reale.

### 11.3 Architettura di matching inefficiente come descritta
Il design attuale implica: per ogni brano caricato, si scansionano/processano i video. Ma se si ri-scansiona periodicamente (sezione 10), si rischia di ri-processare più volte gli stessi video per brani diversi. **Più efficiente:** fingerprintare ogni video **una sola volta** alla scoperta, salvare i suoi landmark hash in un indice globale (inverted index), e poi ogni nuovo brano caricato interroga l'indice esistente invece di ri-scaricare/ri-processare video già visti. Cambia sia i costi stimati (sezione 10 non conta ancora il riuso) sia lo schema DB — da chiarire nel documento tecnico.

### 11.4 Incoerenza "tempo reale" vs "matching batch notturno"
Sezioni 5.1/5.5 promettono notifiche "in tempo reale", ma la roadmap (sezione 13) descrive un matching batch notturno. L'utente riceverebbe quindi la notifica ore dopo, non in tempo reale. È un dettaglio di copy ma genera aspettative sbagliate — meglio comunicare "entro 24h" internamente e nel prodotto, salvo investire per un matching più vicino al near-real-time in futuro.

### 11.5 Entity resolution mancante per DJ/venue
Il ranking (sezione 5.2) usa il "peso" del DJ/venue, ma non c'è ancora un modello che riconosca varianti dello stesso nome (es. "DJ Marco Rossi" vs "Marco Rossi DJ set" vs "@marcorossidj") come la stessa entità. Senza una tabella entità + matching fuzzy, ranking e pagina PROOF rischiano di frammentare lo stesso DJ in identità multiple.

### 11.6 Costo compute fingerprinting sottostimato a scala
La sezione 10 assume compute "trascurabile" — vero con Chromaprint a basso volume, ma se in futuro si passa a modelli embedding-based (CLAP/OpenL3, già previsto come fallback in sezione 9), il costo compute sale sensibilmente (serve CPU potente o GPU per grandi volumi). Da trattare come costo condizionale legato alla scelta del modello di fingerprinting, non come voce fissa.

---

## 12. Rischi di prodotto e conformità

| Rischio | Impatto | Mitigazione |
|---|---|---|
| TikTok/IG non hanno API pubbliche → scraping viola ToS | Alto (legale/ban) | v1 solo YouTube; TikTok/IG come moduli isolati e sperimentali, valutare rischio legale con calma prima di scalarli |
| Falsi positivi nel matching su audio "sporco" (set mixati, filtrati, EQ) | Medio (credibilità prodotto) | Soglia di confidence alta + revisione manuale prima di pubblicare su pagina PROOF pubblica |
| Costi API/scraping a scala (molti video da processare) | Medio | Iniziare con query mirate (non scan indiscriminato), throttling |
| YouTube API quota limits | Basso-medio | Caching, query efficienti, eventuale richiesta quota aumentata |
| Leak di brani unreleased caricati per il monitoraggio | Alto (danno reputazionale artista + azienda) | Storage audio grezzo cifrato, accesso ristretto, no cache pubblica del file audio originale, cancellazione post-fingerprinting se non serve conservarlo |
| Conformità GDPR (dati personali di artisti + nomi di DJ/venue derivati da scraping) | Medio-alto (legale, soprattutto lanciando in EU) | Valutare base giuridica per i dati scrapati, informativa privacy chiara, diritto di rettifica/cancellazione per i DJ/venue citati |
| Metrica "precisione" (sezione 8) perde significato con self-confirm v2 | Basso (misurazione, non prodotto) | Ridefinire la metrica per v2: non più "confermate da reviewer interno" ma "confermate dall'utente" — dato diverso, da trattare separatamente nei report |
| Nessun flusso di contestazione per detection pubblicate su PROOF | Medio (reputazionale se un DJ/venue contesta dati errati) | Prevedere un canale di segnalazione/rimozione rapida per la pagina pubblica, anche solo email in v1 |
| Osservabilità operativa della pipeline assente | Medio (rischio di problemi silenziosi: ban proxy, backlog coda, scan falliti) | Da includere nel documento tecnico: monitoring su latenza scan, tasso di errore scraper, backlog coda job |

---

## 13. Roadmap

- **Fase 1 (MVP):** Costruzione del modulo **DETECT come codice di produzione fin da subito** (non uno spike usa-e-getta) — fingerprinting + matching engine. Primo test: il socio carica i propri set **come file audio diretti** (bypassando temporaneamente lo scraping YouTube), con ground truth nota (brani suonati + timestamp), per isolare "il matching funziona?" dallo scraping. Solo dopo aver validato precision/recall accettabili si passa a integrare lo scraping YouTube reale e a costruire sopra dashboard, tier, notifiche, paywall, revisione interna (Ale + socio) su questo primo set di dati
- **Fase 2:** Pagina PROOF pubblica, ranking FLOOR completo, export press kit. La **transizione a self-confirm utente** resta pianificata ma non urgente nello scenario attuale (lancio alla cerchia DJ pugliesi, ~100 utenti attesi — vedi sezione 10); da attivare se/quando si supera quella soglia
- **Fase 3:** Aggiunta TikTok (rischio controllato)
- **Fase 4:** Aggiunta Instagram, eventuale passaggio a embedding-based matching per maggiore robustezza

---

## 14. Requisiti UI/UX

Vista la natura del prodotto (le card di detection e le notifiche sono il cuore dell'esperienza, e la pagina PROOF è il biglietto da visita pubblico), la UI/UX non è un dettaglio secondario ma un requisito centrale:

- **Card di detection**: design che comunichi "scoperta"/eccitazione (è un momento emotivo per l'artista — "il mio brano è stato suonato!") — non una riga di tabella anonima
- **Paywall visivo, non frustrante**: sul tier Free, i dettagli bloccati vanno mostrati in modo che invitino all'upgrade senza sembrare un blocco aggressivo (es. blur leggero + icona lucchetto + CTA chiara, non un semplice "contenuto nascosto")
- **Pagina PROOF pubblica**: deve essere bella e condivisibile di suo — è marketing organico (sezione 6, growth loop), quindi va trattata come una landing page curata, non come una tabella dati
- **Notifiche**: testo che comunica valore immediato anche nella preview (push notification), coerente col tier
- **Onboarding upload**: il primo upload/scansione deve essere semplicissimo (drag&drop file, feedback chiaro sullo stato "in scansione") — è il momento critico di attivazione

Consiglio pratico: vale la pena investire in un designer (anche freelance) per il flow di detection/card/PROOF page fin dal MVP, perché è la parte del prodotto più visibile e più legata alla percezione di qualità/credibilità (soprattutto per la pagina pubblica, che finisce nei press kit).

---

## 15. Domande aperte

- Nome/branding definitivo (posticipato, placeholder attuale)
- Prezzi esatti dei tier Pro e Label/Agency (vedi sezione 6, da validare con interviste target)
- Definizione precisa di "traccia monitorata" e meccanica di downgrade a fine trial (vedi sezione 6)
- Politica di conservazione/cifratura audio per brani unreleased (dettaglio implementativo da definire col documento tecnico)
- Soglia di confidence minima per proporre una detection all'utente in v2 (vedi sezione 7)
- Gestione detection proposte senza risposta e controllo anti-abuso su self-confirm (vedi sezione 7)
- Esito dello spike di validazione fingerprinting (sezione 11.1) — condiziona se si procede con Chromaprint o si valuta subito l'alternativa embedding-based
- Necessità/tempistica di una consulenza legale leggera su yt-dlp/scraping prima del lancio anche ristretto (sezione 11.2)
- Disegno dell'indice inverso di fingerprint (sezione 11.3) da chiarire nel documento tecnico
