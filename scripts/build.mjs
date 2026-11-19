// Genera il sito statico in /dist a partire da /content. Nessuna dipendenza esterna.
import { readFileSync, writeFileSync, mkdirSync, cpSync, rmSync, readdirSync, existsSync } from 'node:fs';
import { join, extname } from 'node:path';

const OUT = 'dist', C = 'content';
const site = JSON.parse(readFileSync(`${C}/site.json`, 'utf8'));
const esc = s => String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');

function parse(file) {
  const raw = readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  const m = raw.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/);
  const meta = {};
  if (!m) return { meta, body: raw.trim() };
  for (const l of m[1].split('\n')) {
    const i = l.indexOf(':');
    if (i > 0) meta[l.slice(0, i).trim()] = l.slice(i + 1).trim();
  }
  return { meta, body: m[2].trim() };
}
const paras = b => b.split(/\n{2,}/).filter(Boolean).map(p => `<p>${esc(p).replace(/\n/g, '<br>')}</p>`).join('\n');
const list = s => (s || '').split(',').map(x => x.trim()).filter(Boolean);
const copyAssets = (from, to) => {
  mkdirSync(to, { recursive: true });
  for (const f of readdirSync(from)) if (extname(f) !== '.md') cpSync(join(from, f), join(to, f));
};

// Layout comune. depth = profondità della pagina (0 = radice) per costruire i percorsi relativi.
function page({ depth, title, desc, current, body, root, back }) {
  const p = root ? '/' : '../'.repeat(depth);
  const home = p || './';
  const full = title ? `${title} | ${site.nome}` : `${site.nome} | ${site.ruolo}`;
  const contatti = [
    ...(site.social || []).map(x => `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.etichetta)}</a>`),
    `<a href="mailto:${esc(site.email)}">${esc(site.etichetta_email || 'Contattami')}</a>`
  ].join('<span class="linea linea-corta" aria-hidden="true"></span>');
  return `<!doctype html>
<html lang="${site.lingua || 'it'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(full)}</title>
<meta name="description" content="${esc(desc || site.descrizione)}">
<meta property="og:title" content="${esc(full)}">
<meta property="og:description" content="${esc(desc || site.descrizione)}">
<link rel="icon" href="${p}favicon.svg" type="image/svg+xml">
<link rel="preload" href="${p}fonts/pixelify-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="${p}css/tokens.css">
<link rel="stylesheet" href="${p}css/style.css">
</head>
<body>
<a class="salta" href="#contenuto">Vai al contenuto</a>
<header class="menu">
  <button type="button" class="menu-nome" aria-label="${esc(site.nome)}"><span class="nome-esteso">${esc(site.nome)}</span><span class="nome-alias" aria-hidden="true">${esc(site.alias || site.nome)}</span></button>
  <nav class="menu-voci" aria-label="Principale">
    ${back
      ? `<a href="${home}">Back</a>`
      : `<a href="${home}"${current === 'home' ? ' aria-current="page"' : ''}>Works</a>
    <a href="${p}chi-sono/"${current === 'chi-sono' ? ' aria-current="page"' : ''}>About me</a>`
    }
  </nav>
</header>
<main id="contenuto" class="contenitore">
${body}
</main>
<footer class="footer">
  <p class="footer-titolo">${esc(site.footer_titolo || '')}</p>
  <div class="footer-riga">
    <span>${esc(site.nome)}</span>
    <span class="linea linea-lunga" aria-hidden="true"></span>
    <nav class="footer-contatti" aria-label="Contatti">${contatti}</nav>
  </div>
</footer>
<script>
(function() {
  var el = document.querySelector('.menu-nome');
  if (!el) return;
  var timer;
  el.addEventListener('click', function() {
    el.classList.add('mostra-alias');
    clearTimeout(timer);
    timer = setTimeout(function() {
      el.classList.remove('mostra-alias');
      el.blur();
    }, 1500);
  });
})();
</script>
</body>
</html>
`;
}
const write = (path, html) => { mkdirSync(join(OUT, path), { recursive: true }); writeFileSync(join(OUT, path, 'index.html'), html); };

rmSync(OUT, { recursive: true, force: true });
mkdirSync(OUT, { recursive: true });
cpSync('src/css', `${OUT}/css`, { recursive: true });
cpSync('src/static', OUT, { recursive: true });
cpSync('src/fonts', `${OUT}/fonts`, { recursive: true });

// Lavori
const lavori = readdirSync(`${C}/lavori`, { withFileTypes: true })
  .filter(d => d.isDirectory() && existsSync(`${C}/lavori/${d.name}/progetto.md`))
  .map(d => ({ slug: d.name, ...parse(`${C}/lavori/${d.name}/progetto.md`) }))
  .filter(l => l.meta.bozza !== 'true')
  .sort((a, b) => (Number(a.meta.ordine) || 999) - (Number(b.meta.ordine) || 999));

for (const l of lavori) copyAssets(`${C}/lavori/${l.slug}`, `${OUT}/lavori/${l.slug}`);

// Landing
const cards = lavori.map(l => `<li class="card"><a href="lavori/${l.slug}/">
  <img src="lavori/${l.slug}/${esc(l.meta.cover)}" alt="Anteprima di ${esc(l.meta.titolo)}" width="1200" height="900" loading="lazy">
  <h2>${esc(l.meta.titolo)}</h2>
  <p>${esc(l.meta.ruolo)}${l.meta.anno ? ', ' + esc(l.meta.anno) : ''}</p>
</a></li>`).join('\n');
writeFileSync(`${OUT}/index.html`, page({
  depth: 0, current: 'home', desc: site.descrizione,
  body: `<section class="intro"><h1>${esc(site.nome)}</h1><p>${esc(site.ruolo)}</p></section>\n<ul class="griglia">\n${cards}\n</ul>`
}));

// Inietta loader e cursore badge nella home
const antiFlicker = `<script>try{var r=false,n=performance.getEntriesByType('navigation')[0];if(n)r=(n.type==='reload');else if(performance.navigation)r=(performance.navigation.type===1);if(document.referrer&&new URL(document.referrer).origin===window.location.origin&&sessionStorage.getItem('portfolio_loader_shown')&&!r){document.documentElement.classList.add('skip-loader');}}catch(e){}</script>`;
const loaderDiv = `<div id="loader" aria-hidden="true"><div class="loader-inner"><div class="loader-log" id="loaderLog"></div><div class="loader-barra"><div class="loader-fill" id="loaderFill"></div></div><p class="loader-pct" id="loaderPct">0%</p></div></div>`;
const cursorBadge = `<div id="cursorBadge" class="cursor-badge" aria-hidden="true">Learn More</div>`;
const cursorScript = `<script>
(function() {
  if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
  var b = document.getElementById('cursorBadge');
  if (!b) return;
  var over = false;
  document.querySelectorAll('.griglia .card a').forEach(function(a) {
    a.addEventListener('mouseenter', function() { over = true; b.classList.add('visibile'); });
    a.addEventListener('mouseleave', function() { over = false; b.classList.remove('visibile'); });
  });
  window.addEventListener('mousemove', function(e) {
    if (over) b.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0) translate(-50%,-50%)';
  }, { passive: true });
})();
</script>`;
let homeHtml = readFileSync(`${OUT}/index.html`, 'utf8');
homeHtml = homeHtml.replace('<body>', '<body>' + antiFlicker + loaderDiv + cursorBadge).replace('</body>', '<script src="loader.js"></script>' + cursorScript + '</body>');
writeFileSync(`${OUT}/index.html`, homeHtml);

// Dettaglio
lavori.forEach((l, i) => {
  const m = l.meta, prev = lavori[i - 1], next = lavori[i + 1];
  const links = list(m.link?.replace(/;/g, ',')).map(x => x.split('|').map(s => s.trim()))
    .filter(([, u]) => u).map(([t, u]) => `<a class="pulsante" href="${esc(u)}" rel="noopener">${esc(t)}</a>`).join('');
  const imgs = list(m.immagini).map(f => `<img src="${esc(f)}" alt="" loading="lazy">`).join('\n');
  const nav = `<nav class="sequenza" aria-label="Altri lavori">
  ${prev ? `<a href="../${prev.slug}/">Precedente: ${esc(prev.meta.titolo)}</a>` : '<span></span>'}
  ${next ? `<a href="../${next.slug}/">Successivo: ${esc(next.meta.titolo)}</a>` : '<span></span>'}
</nav>`;
  write(`lavori/${l.slug}`, page({
    depth: 2, title: m.titolo, desc: l.body.split('\n')[0], back: true,
    body: `<article>
<header class="dettaglio-testa">
  <h1>${esc(m.titolo)}</h1>
  <dl class="meta">
    ${m.anno ? `<div><dt>Anno</dt><dd>${esc(m.anno)}</dd></div>` : ''}
    ${m.ruolo ? `<div><dt>Ruolo</dt><dd>${esc(m.ruolo)}</dd></div>` : ''}
  </dl>
</header>
<div class="testo">${paras(l.body)}${links ? `<p>${links}</p>` : ''}</div>
<div class="galleria">
${imgs}
</div>
${nav}
</article>`
  }));
});

// Chi sono
const about = parse(`${C}/chi-sono/chi-sono.md`);
copyAssets(`${C}/chi-sono`, `${OUT}/chi-sono`);
write('chi-sono', page({
  depth: 1, current: 'chi-sono', title: about.meta.titolo, desc: about.body.split('\n')[0],
  body: `<div class="chi-sono">
<div class="testo"><h1>${esc(about.meta.titolo)}</h1>
${paras(about.body)}</div>
${about.meta.foto ? `<img src="${esc(about.meta.foto)}" alt="Ritratto di ${esc(site.nome)}">` : ''}
</div>`
}));

// 404: i link e gli stili usano percorsi dalla radice, perché la pagina viene servita a indirizzi qualsiasi
writeFileSync(`${OUT}/404.html`, page({
  depth: 0, root: true, title: 'Pagina non trovata',
  body: `<div class="testo"><h1>Pagina non trovata</h1><p>Questo indirizzo non esiste. Torna alla <a href="/">home</a> per vedere i lavori.</p></div>`
}));
console.log(`Sito generato in /${OUT}: ${lavori.length} lavori.`);
