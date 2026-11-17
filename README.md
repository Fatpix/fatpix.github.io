# Portfolio

Sito statico generato da `content/`. Pubblicato su GitHub Pages a ogni caricamento sul ramo `main`.

## Aggiungere un lavoro
1. Copia la cartella `content/lavori/esempio-progetto` e rinominala (es. `brand-xyz`: è l'indirizzo del lavoro, solo minuscole, numeri e trattini).
2. Sostituisci le immagini (consigliato WebP, max ~1600 px di larghezza).
3. Modifica `progetto.md`:
   - `titolo`, `anno`, `ruolo`
   - `ordine`: numero più basso = più in alto nella landing
   - `bozza: true` per nasconderlo finché non è pronto
   - `cover`: immagine della card (formato 4:3)
   - `immagini`: file della galleria, separati da virgola, in ordine
   - `link`: `Etichetta | https://...`; più link separati da `;`
   - Sotto la seconda riga `---` va la descrizione (paragrafi separati da riga vuota)
4. Carica le modifiche su GitHub: dopo circa un minuto il sito è aggiornato.

## Altri contenuti
- Testi e foto di "Chi sono": `content/chi-sono/`
- Nome, email, social: `content/site.json`
- Colori, font, spaziature: `src/css/tokens.css`

## Provarlo in locale (facoltativo, serve Node 20+)
    node scripts/build.mjs
    npx serve dist

## Prima pubblicazione
1. Crea un repository **pubblico** su GitHub (per l'indirizzo `nome.github.io` chiamalo `nome.github.io`).
2. Carica tutti i file di questa cartella.
3. In *Settings → Pages* imposta *Source* su **GitHub Actions**.
4. In *Actions* controlla che il workflow "Pubblica il sito" sia verde.
