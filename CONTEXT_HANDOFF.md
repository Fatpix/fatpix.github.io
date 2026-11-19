# Passaggio Consegne e Contesto Progetto (Context Handoff)

Questo file riassume l'intero stato del progetto, le preferenze dell'utente, i requisiti implementati e l'architettura tecnica per permettere a qualsiasi nuova istanza di Antigravity (su un altro computer) di riprendere immediatamente il lavoro senza perdere alcuna informazione.

---

## 1. Profilo Utente & Progetto
- **Proprietario:** Filippo Arpe (alias *"Fatpix"*).
- **Progetto:** Portfolio personale per designer / art director.
- **URL di pubblicazione:** `https://fatpix.github.io` (ospitato su GitHub Pages).
- **Repository GitHub:** `fatpix/fatpix.github.io` (o `portfolio 6`).
- **Deploy:** GitHub Actions su push del ramo `main` tramite `.github/workflows/deploy.yml`.

---

## 2. Requisiti Grafici & Funzionali Rispettati
1. **Identità e Tipografia:**
   - Display font: **Anton** (`src/fonts/anton-latin-400-normal.woff2`).
   - Monospace font: **Pixelify Sans** (`src/fonts/pixelify-sans-latin-400-normal.woff2`). Sostituisce Roboto Mono per tutti i testi tecnici, date, link e cursor badge.
   - Colore accento / hover: `#ef1111` (Rosso vivo).
2. **Layout Progetti (Home):**
   - 9 progetti in esposizione (`progetto-01` fino a `progetto-09`).
   - Disposizione rigorosamente a **colonna singola verticale** (`.griglia { grid-template-columns: 1fr; }`), uno sotto all'altro.
3. **Header Mobile (`@media (max-width: 44rem)`):**
   - **Sfondo trasparente:** Nessuna barra bianca di sfondo.
   - **Inversione cromatica negativa:** Il testo del menu usa `mix-blend-mode: difference` per invertire automaticamente il colore rispetto al contenuto/immagini sottostanti (diventa nero su sfondi chiari e bianco su sfondi scuri).
   - **Stato attivo & hover inalterato:** La voce attiva (es. "Works" in home) e gli stati hover restano **rosso solido `#ef1111`** (`mix-blend-mode: normal`).
   - **Posizionamento orizzontale fisso:**
     - A sinistra: *"Filippo Arpe"* (`top: 1.25rem; left: 1.5rem;`).
     - A destra: *"Works"* e *"About me"* sulla stessa linea orizzontale (`top: 1.35rem; right: 1.5rem;`), affiancati e senza alcuna sovrapposizione.
   - **Interazione Logo:** Toccando *"Filippo Arpe"*, la scritta si trasforma in *"Fatpix"* in rosso solido per 1.5 secondi e ritorna automaticamente a *"Filippo Arpe"*. **Non** funge da link per tornare alla home.
4. **Pagine Dettaglio Progetto (`content/lavori/*/`):**
   - Il menu di navigazione in alto a destra mostra **esclusivamente la voce `Back`** al primo posto (niente "Works" o "About me").
   - Nessun pulsante ridondante *"vedi il progetto"*.
5. **Schermata di Loading Retro-Terminal:**
   - Terminale animato con 5 passaggi numerati (percentuale tabular-nums, barra e `OK` rosso).
   - Mostrata **solo al primo accesso o su ricaricamento pagina (F5 / Cmd+R)**.
   - **Non** si attiva quando si torna alla home da una pagina interna (gestito via `sessionStorage`, `performance.navigation` e `referrer`).
6. **Custom Cursor Badge (Desktop):**
   - In hover sulle schede dei progetti, il cursore standard è nascosto e sostituito da un badge rettangolare *"Learn More"* in font Pixelify Sans con `mix-blend-mode: difference`.

---

## 3. Struttura del Codice e Build System
- `src/css/tokens.css`: Variabili CSS globali (`--font-mono: "Pixelify Sans"`).
- `src/css/style.css`: Stili completi. Nota architetturale fondamentale: le coordinate desktop del menu sono strettamente confinate in `@media (min-width: 44.0625rem)`, mentre mobile è in `@media (max-width: 44rem)` con elementi fissi diretti per preservare il blend mode `difference` sul body.
- `scripts/build.mjs`: Generatore statico in Node.js (usato da GitHub Actions).
- `scripts/build_site.py`: Mirror Python del generatore statico (usato per build locali rapide).
- `content/`: File Markdown dei contenuti (`site.json`, `chi-sono/`, `lavori/progetto-01` .. `progetto-09`).
- `dist/`: Cartella di output generata e servita online.

---

## 4. Regole per l'Agente
- Generare sempre in automatico lo zip aggiornato in `/Users/thedocks/Downloads/portfolio-aggiornato.zip` dopo ogni modifica significativa.
- Mantenere la coerenza tra `scripts/build_site.py` e `scripts/build.mjs`.
