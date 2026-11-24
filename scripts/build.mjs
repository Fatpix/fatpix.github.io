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
const isVideo = src => /\.(mp4|webm|mov|ogg)$/i.test(src || '');
const renderMedia = (src, alt = '', opts = {}) => {
  if (!src) return '';
  const u = esc(src);
  const a = esc(alt);
  const w = opts.width ? ` width="${opts.width}"` : '';
  const h = opts.height ? ` height="${opts.height}"` : '';
  const prio = opts.priority ? ' fetchpriority="high"' : '';
  const lazy = opts.lazy ? ' loading="lazy"' : (opts.lazy === false ? ' loading="eager"' : '');
  const cls = opts.cls ? ` class="${opts.cls}"` : '';
  if (isVideo(src)) {
    return `<video src="${u}"${cls}${w}${h} autoplay loop muted playsinline preload="metadata" aria-label="${a}"></video>`;
  }
  return `<img src="${u}" alt="${a}"${cls}${w}${h}${prio}${lazy} decoding="async">`;
};

let sharp = null;
try {
  sharp = (await import('sharp')).default;
} catch (e) {}

async function copyAssets(from, to) {
  mkdirSync(to, { recursive: true });
  if (!existsSync(from)) return;
  for (const f of readdirSync(from)) {
    const ext = extname(f).toLowerCase();
    if (ext === '.md') continue;
    const src = join(from, f);
    const dst = join(to, f);
    if (sharp && ['.jpg', '.jpeg', '.png', '.webp'].includes(ext)) {
      try {
        const metadata = await sharp(src).metadata();
        let pipeline = sharp(src);
        if (metadata.width > 2000 || metadata.height > 2000) {
          pipeline = pipeline.resize(2000, 2000, { fit: 'inside', withoutEnlargement: true });
        }
        if (ext === '.jpg' || ext === '.jpeg') {
          await pipeline.jpeg({ quality: 84, progressive: true, mozjpeg: true }).toFile(dst);
        } else if (ext === '.png') {
          await pipeline.png({ quality: 85, compressionLevel: 8 }).toFile(dst);
        } else if (ext === '.webp') {
          await pipeline.webp({ quality: 84 }).toFile(dst);
        } else {
          cpSync(src, dst);
        }
      } catch (err) {
        cpSync(src, dst);
      }
    } else {
      cpSync(src, dst);
    }
  }
}

function generateProjectPlaceholders(outDir, num, title, role) {
  mkdirSync(outDir, { recursive: true });
  const pad = String(num).padStart(2, '0');
  const files = {
    'cover.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="100%">
  <rect width="1600" height="900" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="836" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(800, 430)" text-anchor="middle">
    <circle cx="0" cy="-60" r="48" fill="none" stroke="#b0b0b0" stroke-width="3"/>
    <text x="0" y="-48" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="32" font-weight="600" fill="#888888">${pad}</text>
    <text x="0" y="30" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#333333" letter-spacing="-0.5">${esc(title)}</text>
    <text x="0" y="75" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="400" fill="#777777" letter-spacing="1">${esc(role).toUpperCase()}</text>
  </g>
</svg>`,
    'hero.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="100%">
  <rect width="1600" height="900" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="836" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(800, 420)" text-anchor="middle">
    <rect x="-140" y="-120" width="280" height="140" rx="8" fill="none" stroke="#999999" stroke-width="2.5" stroke-dasharray="6,6"/>
    <text x="0" y="-42" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="48" font-weight="700" fill="#222222" letter-spacing="-1">${esc(title).toUpperCase()}</text>
    <text x="0" y="70" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="22" font-weight="500" fill="#666666" letter-spacing="2">HERO IDENTITY &amp; SYSTEM</text>
    <line x1="-80" y1="110" x2="80" y2="110" stroke="#d5d5d5" stroke-width="2"/>
  </g>
</svg>`,
    'concept.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%">
  <rect width="1200" height="900" fill="#ebebeb"/>
  <rect x="24" y="24" width="1152" height="852" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(600, 400)" text-anchor="middle">
    <circle cx="-120" cy="0" r="90" fill="none" stroke="#cccccc" stroke-width="1.5" stroke-dasharray="4,4"/>
    <circle cx="120" cy="0" r="90" fill="none" stroke="#cccccc" stroke-width="1.5" stroke-dasharray="4,4"/>
    <rect x="-180" y="-90" width="360" height="180" fill="none" stroke="#b0b0b0" stroke-width="2"/>
    <line x1="-240" y1="0" x2="240" y2="0" stroke="#cccccc" stroke-width="1"/>
    <line x1="0" y1="-140" x2="0" y2="140" stroke="#cccccc" stroke-width="1"/>
    <text x="0" y="8" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="32" font-weight="700" fill="#333333">${esc(title)}</text>
    <text x="0" y="160" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="500" fill="#666666" letter-spacing="1.5">CONCEPT &amp; GEOMETRIC GRID</text>
    <text x="0" y="195" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#888888">Modular Construction System</text>
  </g>
</svg>`,
    'web-01.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%">
  <rect width="1600" height="1000" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="936" rx="12" fill="#f0f0f0" stroke="#d5d5d5" stroke-width="2"/>
  <rect x="32" y="32" width="1536" height="56" rx="12" fill="#e5e5e5"/>
  <rect x="32" y="76" width="1536" height="12" fill="#e5e5e5"/>
  <circle cx="64" cy="60" r="6" fill="#cccccc"/>
  <circle cx="84" cy="60" r="6" fill="#cccccc"/>
  <circle cx="104" cy="60" r="6" fill="#cccccc"/>
  <rect x="140" y="48" width="400" height="24" rx="4" fill="#ffffff" stroke="#d5d5d5" stroke-width="1"/>
  <text x="155" y="65" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" fill="#888888">https://progetto-${pad}.design</text>
  <g transform="translate(800, 520)" text-anchor="middle">
    <rect x="-680" y="-380" width="1360" height="740" fill="#ffffff" rx="6" stroke="#e0e0e0" stroke-width="1.5"/>
    <text x="0" y="-30" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222" letter-spacing="-0.5">WEB EXPERIENCE 01</text>
    <text x="0" y="20" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="400" fill="#666666" letter-spacing="1">DESKTOP HOMEPAGE INTERFACE</text>
    <rect x="-120" y="60" width="240" height="40" rx="4" fill="#ebebeb" stroke="#d0d0d0" stroke-width="1"/>
    <text x="0" y="85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14" font-weight="500" fill="#666666">DESKTOP INTERFACE</text>
  </g>
</svg>`,
    'web-02.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%">
  <rect width="1600" height="1000" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="936" rx="12" fill="#f0f0f0" stroke="#d5d5d5" stroke-width="2"/>
  <rect x="32" y="32" width="1536" height="56" rx="12" fill="#e5e5e5"/>
  <rect x="32" y="76" width="1536" height="12" fill="#e5e5e5"/>
  <circle cx="64" cy="60" r="6" fill="#cccccc"/>
  <circle cx="84" cy="60" r="6" fill="#cccccc"/>
  <circle cx="104" cy="60" r="6" fill="#cccccc"/>
  <rect x="140" y="48" width="400" height="24" rx="4" fill="#ffffff" stroke="#d5d5d5" stroke-width="1"/>
  <text x="155" y="65" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" fill="#888888">https://progetto-${pad}.design/catalog</text>
  <g transform="translate(800, 520)" text-anchor="middle">
    <rect x="-680" y="-380" width="1360" height="740" fill="#ffffff" rx="6" stroke="#e0e0e0" stroke-width="1.5"/>
    <text x="0" y="-30" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222" letter-spacing="-0.5">WEB EXPERIENCE 02</text>
    <text x="0" y="20" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="400" fill="#666666" letter-spacing="1">INTERACTIVE CATALOG &amp; SYSTEM</text>
    <rect x="-120" y="60" width="240" height="40" rx="4" fill="#ebebeb" stroke="#d0d0d0" stroke-width="1"/>
    <text x="0" y="85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14" font-weight="500" fill="#666666">DESKTOP INTERFACE</text>
  </g>
</svg>`,
    'banner.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 750" width="100%">
  <rect width="1800" height="750" fill="#ebebeb"/>
  <rect x="28" y="28" width="1744" height="694" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(900, 360)" text-anchor="middle">
    <rect x="-800" y="-280" width="1600" height="560" fill="#e2e2e2" stroke="#cccccc" stroke-width="1.5"/>
    <text x="0" y="-20" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="52" font-weight="700" fill="#222222" letter-spacing="-0.5">OUTDOOR CAMPAIGN &amp; BANNER</text>
    <text x="0" y="35" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="22" font-weight="400" fill="#666666" letter-spacing="1.5">ENVIRONMENTAL SIGNAGE — ${esc(title).toUpperCase()}</text>
    <line x1="-120" y1="80" x2="120" y2="80" stroke="#999999" stroke-width="2"/>
  </g>
</svg>`,
    'mobile-01.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1600" width="100%">
  <rect width="900" height="1600" fill="#ebebeb"/>
  <rect x="40" y="40" width="820" height="1520" rx="48" fill="#f8f8f8" stroke="#d5d5d5" stroke-width="3"/>
  <rect x="360" y="68" width="180" height="32" rx="16" fill="#e0e0e0"/>
  <g transform="translate(450, 780)" text-anchor="middle">
    <rect x="-350" y="-620" width="700" height="1240" rx="24" fill="#ffffff" stroke="#e0e0e0" stroke-width="1.5"/>
    <circle cx="0" cy="-280" r="50" fill="none" stroke="#cccccc" stroke-width="2"/>
    <text x="0" y="-268" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="32" font-weight="700" fill="#666666">01</text>
    <text x="0" y="-120" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="40" font-weight="700" fill="#222222">MOBILE VIEW 01</text>
    <text x="0" y="-70" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="18" font-weight="400" fill="#666666" letter-spacing="1">FEED &amp; COMMUNITY SCREEN</text>
    <rect x="-280" y="20" width="560" height="160" rx="12" fill="#f5f5f5" stroke="#e8e8e8" stroke-width="1"/>
    <rect x="-280" y="210" width="560" height="160" rx="12" fill="#f5f5f5" stroke="#e8e8e8" stroke-width="1"/>
    <rect x="-280" y="400" width="560" height="160" rx="12" fill="#f5f5f5" stroke="#e8e8e8" stroke-width="1"/>
  </g>
</svg>`,
    'mobile-02.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1600" width="100%">
  <rect width="900" height="1600" fill="#ebebeb"/>
  <rect x="40" y="40" width="820" height="1520" rx="48" fill="#f8f8f8" stroke="#d5d5d5" stroke-width="3"/>
  <rect x="360" y="68" width="180" height="32" rx="16" fill="#e0e0e0"/>
  <g transform="translate(450, 780)" text-anchor="middle">
    <rect x="-350" y="-620" width="700" height="1240" rx="24" fill="#ffffff" stroke="#e0e0e0" stroke-width="1.5"/>
    <circle cx="0" cy="-280" r="50" fill="none" stroke="#cccccc" stroke-width="2"/>
    <text x="0" y="-268" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="32" font-weight="700" fill="#666666">02</text>
    <text x="0" y="-120" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="40" font-weight="700" fill="#222222">MOBILE VIEW 02</text>
    <text x="0" y="-70" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="18" font-weight="400" fill="#666666" letter-spacing="1">DETAILED VIEW &amp; INTERACTION</text>
    <rect x="-280" y="20" width="560" height="160" rx="12" fill="#f5f5f5" stroke="#e8e8e8" stroke-width="1"/>
    <rect x="-280" y="210" width="560" height="160" rx="12" fill="#f5f5f5" stroke="#e8e8e8" stroke-width="1"/>
    <rect x="-280" y="400" width="560" height="160" rx="12" fill="#f5f5f5" stroke="#e8e8e8" stroke-width="1"/>
  </g>
</svg>`,
    'merch-01.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1250" width="100%">
  <rect width="1000" height="1250" fill="#ebebeb"/>
  <rect x="24" y="24" width="952" height="1202" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(500, 600)" text-anchor="middle">
    <rect x="-360" y="-460" width="720" height="920" rx="16" fill="#f4f4f4" stroke="#dcdcdc" stroke-width="2"/>
    <rect x="-180" y="-280" width="360" height="360" rx="8" fill="none" stroke="#c0c0c0" stroke-width="2" stroke-dasharray="6,6"/>
    <text x="0" y="-85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222">TOTE BAG MOCKUP</text>
    <text x="0" y="-35" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="18" font-weight="500" fill="#777777" letter-spacing="1">MERCHANDISE &amp; COLLATERAL</text>
    <text x="0" y="200" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#999999">Physical Brand Touchpoint 01</text>
  </g>
</svg>`,
    'merch-02.svg': `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1250" width="100%">
  <rect width="1000" height="1250" fill="#ebebeb"/>
  <rect x="24" y="24" width="952" height="1202" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(500, 600)" text-anchor="middle">
    <rect x="-360" y="-460" width="720" height="920" rx="16" fill="#f4f4f4" stroke="#dcdcdc" stroke-width="2"/>
    <rect x="-180" y="-280" width="360" height="360" rx="8" fill="none" stroke="#c0c0c0" stroke-width="2" stroke-dasharray="6,6"/>
    <text x="0" y="-85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222">PRODUCT MOCKUP</text>
    <text x="0" y="-35" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="18" font-weight="500" fill="#777777" letter-spacing="1">MERCHANDISE &amp; PACKAGING</text>
    <text x="0" y="200" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#999999">Physical Brand Touchpoint 02</text>
  </g>
</svg>`
  };
  for (const [fname, content] of Object.entries(files)) {
    const dst = join(outDir, fname);
    if (!existsSync(dst)) writeFileSync(dst, content, 'utf8');
  }
}

function generateAboutPlaceholder(outDir) {
  mkdirSync(outDir, { recursive: true });
  const dst = join(outDir, 'foto.svg');
  if (!existsSync(dst)) {
    writeFileSync(dst, `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%">
  <rect width="1200" height="900" fill="#ebebeb"/>
  <rect x="24" y="24" width="1152" height="852" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(600, 450)" text-anchor="middle">
    <circle cx="0" cy="-40" r="90" fill="none" stroke="#b0b0b0" stroke-width="2"/>
    <circle cx="0" cy="-60" r="35" fill="none" stroke="#999999" stroke-width="2"/>
    <path d="M -55 20 A 55 45 0 0 1 55 20 Z" fill="none" stroke="#999999" stroke-width="2"/>
    <text x="0" y="90" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="28" font-weight="600" fill="#555555" letter-spacing="1">ABOUT ME</text>
    <text x="0" y="125" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#888888">Visual Designer &amp; Creative</text>
  </g>
</svg>`, 'utf8');
  }
}

// Layout comune. depth = profondità della pagina (0 = radice) per costruire i percorsi relativi.
function page({ depth, title, desc, current, body, root, back, hero_html = '' }) {
  const p = root ? '/' : '../'.repeat(depth);
  const home = p || './';
  const full = title ? `${title} | ${site.nome}` : `${site.nome} | ${site.ruolo}`;
  const contatti = [
    ...(site.social || []).map(x => `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(x.etichetta)}</a>`),
    `<a href="mailto:${esc(site.email)}">${esc(site.etichetta_email || 'Contattami')}</a>`
  ].join('<span class="linea linea-corta" aria-hidden="true"></span>');
  const extraBody = current === 'progetto' ? `<div id="scrollProgress" class="scroll-progress" aria-hidden="true"></div><div id="lightbox" class="lightbox" aria-hidden="true" role="dialog" aria-modal="true"><button type="button" class="lightbox-chiudi" aria-label="Chiudi visualizzazione a schermo pieno">x</button><img class="lightbox-img" src="" alt="" style="display:none;"><video class="lightbox-video" src="" autoplay loop muted playsinline controls style="display:none;"></video></div>` : '';
  return `<!doctype html>
<html lang="${site.lingua || 'it'}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>${esc(full)}</title>
<meta name="description" content="${esc(desc || site.descrizione)}">
<meta property="og:title" content="${esc(full)}">
<meta property="og:description" content="${esc(desc || site.descrizione)}">
<link rel="icon" href="${p}favicon.ico" sizes="any">
<link rel="icon" href="${p}favicon.png" type="image/png" sizes="32x32">
<link rel="icon" href="${p}favicon-192.png" type="image/png" sizes="192x192">
<link rel="icon" href="${p}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="${p}apple-touch-icon.png">
<link rel="preload" href="${p}fonts/pixelify-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="${p}css/tokens.css?v=3.0">
<link rel="stylesheet" href="${p}css/style.css?v=3.2">
</head>
<body${current ? ` class="pagina-${current}"` : ''}>
<div id="cursorBadge" class="cursor-badge" aria-hidden="true"></div>
${extraBody}
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
<div class="corpo-pagina">
  ${hero_html}
  <main id="contenuto" class="contenitore">
${body}
  </main>
</div>
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
  if (document.body.classList.contains('pagina-home')) {
    // ── Scroll-driven Text-Clip Mask Reveal ──
    (function() {
      var root = document.getElementById('textClipReveal');
      var mask = document.getElementById('textClipSticky');
      if (!root || !mask) return;

      var text = root.getAttribute('data-text') || 'PORTFOLIO';
      var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="260" viewBox="0 0 1400 260">' +
        '<text x="50%" y="54%" dominant-baseline="central" text-anchor="middle" ' +
        'font-family="Anton, Impact, sans-serif" font-weight="900" font-size="220" letter-spacing="1">' +
        text + '</text></svg>';

      var maskData = 'url("data:image/svg+xml,' + encodeURIComponent(svg) + '")';
      mask.style.webkitMaskImage = maskData;
      mask.style.maskImage = maskData;

      function getInitialSize() {
        var w = window.innerWidth || document.documentElement.clientWidth || 1000;
        if (w <= 640) {
          return 0.96;
        }
        return Math.min(0.92, 1400 / w);
      }

      var targetScale = 160;
      var easing = 0.15;
      var eased = 0;
      var isMasked = true;

      function rawProgress() {
        var rect = root.getBoundingClientRect();
        var vh = window.innerHeight || document.documentElement.clientHeight;
        var distance = rect.height - vh;
        if (distance <= 0) return 0;
        return Math.min(1, Math.max(0, -rect.top / distance));
      }

      function loop() {
        var p = rawProgress();
        eased += (p - eased) * easing;

        if (eased >= 0.65) {
          if (isMasked) {
            mask.style.webkitMaskImage = 'none';
            mask.style.maskImage = 'none';
            isMasked = false;
          }
        } else {
          if (!isMasked) {
            mask.style.webkitMaskImage = maskData;
            mask.style.maskImage = maskData;
            isMasked = true;
          }
          var base = getInitialSize();
          var t = Math.min(1, Math.max(0, eased / 0.65));
          var scaleCurve = Math.pow(t, 2.2);
          var size = (base + targetScale * scaleCurve) * 100;
          var sStr = size.toFixed(2) + '% auto';
          mask.style.webkitMaskSize = sStr;
          mask.style.maskSize = sStr;
        }

        var hHud = root.querySelector('.pixel-player-hud');
        if (hHud) {
          var rRect = root.getBoundingClientRect();
          if (rRect.bottom <= 40) {
            hHud.style.display = 'none';
          } else {
            hHud.style.display = 'flex';
          }
        }

        requestAnimationFrame(loop);
      }

      loop();
    })();

    
    var updateCardHeight = function() {
      var c = document.querySelector('.griglia .card');
      if (c && c.offsetHeight > 0) {
        document.documentElement.style.setProperty('--altezza-card', c.offsetHeight + 'px');
      }
    };
    updateCardHeight();
    window.addEventListener('resize', updateCardHeight, { passive: true });
    window.addEventListener('load', updateCardHeight, { passive: true });

    // ── Animazione Scroll Lavori Legata allo Scroll e Velocità ──
    var cards = Array.prototype.slice.call(document.querySelectorAll('.griglia .card'));
    if (cards.length > 0 && !window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      var cardMetrics = [];
      var measureCards = function() {
        var scrollY = window.pageYOffset || document.documentElement.scrollTop;
        var H = window.innerHeight || document.documentElement.clientHeight;
        cardMetrics = cards.map(function(card, index) {
          var rect = card.getBoundingClientRect();
          var top = rect.top + scrollY;
          return {
            card: card,
            isOdd: index % 2 === 0,
            top: top,
            height: card.offsetHeight || rect.height,
            initInView: top < H * 0.9
          };
        });
      };

      measureCards();
      window.addEventListener('resize', measureCards, { passive: true });
      window.addEventListener('load', measureCards, { passive: true });

      var ticking = false;
      var updateCardScroll = function() {
        var scrollY = window.pageYOffset || document.documentElement.scrollTop;
        var H = window.innerHeight || document.documentElement.clientHeight;
        var enterDist = Math.max(200, H * 0.55);

        for (var i = 0; i < cardMetrics.length; i++) {
          var m = cardMetrics[i];
          var relTop = m.top - scrollY;

          // Quando si scorre verso il basso: entra dal lato e rimane fissa al centro (non esce in alto)
          // Quando si risale verso l'alto: le card che tornano verso il basso escono lateralmente legate allo scroll
          var p = 1;
          if (m.initInView && scrollY < enterDist) {
            p = 1;
          } else {
            if (relTop >= H) {
              p = 0;
            } else if (relTop <= H - enterDist) {
              p = 1;
            } else {
              p = (H - relTop) / enterDist;
            }
          }

          if (p < 0) p = 0;
          if (p > 1) p = 1;

          // Easing smoothstep: 3p^2 - 2p^3 legato alla velocità e posizione di scroll
          var eased = p * p * (3 - 2 * p);

          var sign = m.isOdd ? -1 : 1;
          var tx = (1 - eased) * 100 * sign;

          m.card.style.transform = 'translate3d(' + tx.toFixed(2) + '%, 0, 0)';
          m.card.style.opacity = eased.toFixed(3);
        }
        ticking = false;
      };

      var onScroll = function() {
        if (!ticking) {
          window.requestAnimationFrame(updateCardScroll);
          ticking = true;
        }
      };

      window.addEventListener('scroll', onScroll, { passive: true });
      updateCardScroll();
    }
  }

  var el = document.querySelector('.menu-nome');
  if (el) {
    var timer;
    el.addEventListener('click', function() {
      el.classList.add('mostra-alias');
      clearTimeout(timer);
      timer = setTimeout(function() {
        el.classList.remove('mostra-alias');
        el.blur();
      }, 1500);
    });
  }

  var badge = document.getElementById('cursorBadge');
  if (badge && window.matchMedia('(hover: hover) and (pointer: fine)').matches) {
    var setBadge = function(text) {
      badge.textContent = text;
      badge.classList.add('visibile');
    };
    var hideBadge = function() {
      badge.classList.remove('visibile');
    };

    window.addEventListener('mousemove', function(e) {
      badge.style.transform = 'translate3d(' + e.clientX + 'px,' + e.clientY + 'px,0) translate(-50%,-50%)';
    }, { passive: true });

    document.addEventListener('mouseover', function(e) {
      var t = e.target;
      if (!t) return;
      if (t.closest('#textClipReveal') || t.closest('.text-clip-reveal-root') || t.closest('#landingHero') || t.closest('.landing-hero-stage')) {
        hideBadge();
      } else if (t.closest('.about-foto')) {
        setBadge('Hi, this is me!');
      } else if (t.closest('.progetto-hero-media, .progetto-concept-media, .progetto-showcase, .progetto-dettaglio img, .progetto-dettaglio video')) {
        setBadge('Take a look');
      } else if (t.closest('.griglia .card')) {
        setBadge('Learn More');
      } else {
        hideBadge();
      }
    });

    document.addEventListener('mouseleave', function() {
      hideBadge();
    });
  }

  var lb = document.getElementById('lightbox');
  if (lb) {
    var lbImg = lb.querySelector('.lightbox-img');
    var lbVideo = lb.querySelector('.lightbox-video');
    var btnChiudi = lb.querySelector('.lightbox-chiudi');
    var openLb = function(mediaEl) {
      var isVid = mediaEl.tagName.toLowerCase() === 'video' || /\.(mp4|webm|mov|ogg)$/i.test(mediaEl.currentSrc || mediaEl.src || '');
      if (isVid) {
        if (lbImg) { lbImg.style.display = 'none'; lbImg.src = ''; }
        if (lbVideo) {
          lbVideo.src = mediaEl.currentSrc || mediaEl.src;
          lbVideo.style.display = 'block';
          lbVideo.play().catch(function() {});
        }
      } else {
        if (lbVideo) {
          lbVideo.pause();
          lbVideo.src = '';
          lbVideo.style.display = 'none';
        }
        if (lbImg) {
          lbImg.src = mediaEl.currentSrc || mediaEl.src;
          lbImg.alt = mediaEl.alt || '';
          lbImg.style.display = 'block';
        }
      }
      lb.classList.add('aperto');
      lb.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      if (badge) badge.classList.remove('visibile');
    };
    var closeLb = function() {
      lb.classList.remove('aperto');
      lb.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      if (lbVideo) {
        lbVideo.pause();
        lbVideo.src = '';
        lbVideo.style.display = 'none';
      }
      if (lbImg) {
        lbImg.src = '';
        lbImg.style.display = 'none';
      }
    };

    document.querySelectorAll('.progetto-hero-media img, .progetto-hero-media video, .progetto-concept-media img, .progetto-concept-media video, .progetto-showcase img, .progetto-showcase video').forEach(function(el) {
      el.addEventListener('click', function() {
        openLb(el);
      });
    });

    if (btnChiudi) btnChiudi.addEventListener('click', closeLb);
    lb.addEventListener('click', function(e) {
      if (e.target === lb) closeLb();
    });
    window.addEventListener('keydown', function(e) {
      if (e.key === 'Escape' && lb.classList.contains('aperto')) closeLb();
    });
  }

  var progress = document.getElementById('scrollProgress');
  if (progress && (!window.CSS || !CSS.supports || !CSS.supports('animation-timeline', 'scroll()'))) {
    var updateProgress = function() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      var p = h > 0 ? (window.pageYOffset || document.documentElement.scrollTop) / h : 0;
      progress.style.transform = 'scaleX(' + Math.min(Math.max(p, 0), 1) + ')';
    };
    window.addEventListener('scroll', updateProgress, { passive: true });
    window.addEventListener('resize', updateProgress, { passive: true });
    updateProgress();
  }

  // ── Custom Pixel Video Player (Fatpix Style) ──
  function initPixelVideoPlayers() {
    var videos = document.querySelectorAll('video');
    videos.forEach(function(video) {
      if (video.getAttribute('data-pixel-player-init')) return;
      video.setAttribute('data-pixel-player-init', 'true');

      video.muted = true;
      video.setAttribute('playsinline', '');

      var hud = document.createElement('div');
      hud.className = 'pixel-player-hud';
      hud.setAttribute('role', 'toolbar');
      hud.setAttribute('aria-label', 'Pixel Video Player');

      var playBtn = document.createElement('button');
      playBtn.type = 'button';
      playBtn.className = 'pixel-btn pixel-btn-play' + (!video.paused ? ' attivo' : '');
      playBtn.innerHTML = '<span class="pixel-icon">' + (!video.paused ? '❚❚' : '▶') + '</span><span class="pixel-lbl">' + (!video.paused ? 'PAUSE' : 'PLAY') + '</span>';

      var timeline = document.createElement('div');
      timeline.className = 'pixel-timeline';
      timeline.setAttribute('role', 'slider');
      timeline.setAttribute('aria-label', 'Avanzamento video');
      timeline.tabIndex = 0;

      var track = document.createElement('div');
      track.className = 'pixel-timeline-track';
      var fill = document.createElement('div');
      fill.className = 'pixel-timeline-fill';
      var thumb = document.createElement('div');
      thumb.className = 'pixel-timeline-thumb';

      track.appendChild(fill);
      track.appendChild(thumb);
      timeline.appendChild(track);

      var timeDisplay = document.createElement('span');
      timeDisplay.className = 'pixel-time';
      timeDisplay.textContent = '00:00 / 00:00';

      var muteBtn = document.createElement('button');
      muteBtn.type = 'button';
      muteBtn.className = 'pixel-btn pixel-btn-mute' + (!video.muted ? ' attivo' : '');
      muteBtn.innerHTML = '<span class="pixel-icon">' + (!video.muted ? '🔊' : '🔇') + '</span><span class="pixel-lbl">' + (!video.muted ? 'SOUND' : 'MUTE') + '</span>';

      hud.appendChild(playBtn);
      hud.appendChild(timeline);
      hud.appendChild(timeDisplay);
      hud.appendChild(muteBtn);

      var parent = video.parentElement;
      var rootHero = document.getElementById('textClipReveal');
      if (parent.classList.contains('text-clip-sticky') && rootHero) {
        rootHero.appendChild(hud);
      } else if (parent.classList.contains('text-clip-sticky')) {
        parent.appendChild(hud);
      } else if (parent.classList.contains('lightbox')) {
        parent.appendChild(hud);
      } else {
        if (!parent.classList.contains('pixel-video-wrap')) {
          var wrap = document.createElement('div');
          wrap.className = 'pixel-video-wrap';
          parent.insertBefore(wrap, video);
          wrap.appendChild(video);
          wrap.appendChild(hud);
        } else {
          parent.appendChild(hud);
        }
      }

      playBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (video.paused) {
          video.play().catch(function() {});
        } else {
          video.pause();
        }
      });

      muteBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        if (video.muted) {
          document.querySelectorAll('video').forEach(function(v) {
            if (v !== video) {
              v.muted = true;
              v.dispatchEvent(new Event('volumechange'));
            }
          });
          video.muted = false;
        } else {
          video.muted = true;
        }
        video.dispatchEvent(new Event('volumechange'));
      });

      video.addEventListener('play', function() {
        var ic = playBtn.querySelector('.pixel-icon');
        var lb = playBtn.querySelector('.pixel-lbl');
        if (ic) ic.textContent = '❚❚';
        if (lb) lb.textContent = 'PAUSE';
        playBtn.classList.add('attivo');
      });

      video.addEventListener('pause', function() {
        var ic = playBtn.querySelector('.pixel-icon');
        var lb = playBtn.querySelector('.pixel-lbl');
        if (ic) ic.textContent = '▶';
        if (lb) lb.textContent = 'PLAY';
        playBtn.classList.remove('attivo');
        var w = video.closest('.pixel-video-wrap');
        if (w) w.classList.add('mostra-hud');
      });

      video.addEventListener('volumechange', function() {
        var ic = muteBtn.querySelector('.pixel-icon');
        var lb = muteBtn.querySelector('.pixel-lbl');
        if (video.muted) {
          if (ic) ic.textContent = '🔇';
          if (lb) lb.textContent = 'MUTE';
          muteBtn.classList.remove('attivo');
        } else {
          if (ic) ic.textContent = '🔊';
          if (lb) lb.textContent = 'SOUND';
          muteBtn.classList.add('attivo');
        }
      });

      function formatTime(s) {
        if (isNaN(s) || !isFinite(s) || s < 0) return '00:00';
        var m = Math.floor(s / 60);
        var sec = Math.floor(s % 60);
        return (m < 10 ? '0' + m : m) + ':' + (sec < 10 ? '0' + sec : sec);
      }

      function updateProgress() {
        var cur = video.currentTime || 0;
        var dur = video.duration || 0;
        var pct = dur > 0 ? (cur / dur) * 100 : 0;
        fill.style.width = pct + '%';
        thumb.style.left = pct + '%';
        timeDisplay.textContent = formatTime(cur) + ' / ' + formatTime(dur);
      }

      video.addEventListener('timeupdate', updateProgress);
      video.addEventListener('loadedmetadata', updateProgress);
      video.addEventListener('durationchange', updateProgress);
      updateProgress();

      var isDragging = false;
      function seek(e) {
        var rect = track.getBoundingClientRect();
        var clientX = e.touches ? e.touches[0].clientX : e.clientX;
        var pos = Math.min(1, Math.max(0, (clientX - rect.left) / rect.width));
        if (video.duration) {
          video.currentTime = pos * video.duration;
        }
        updateProgress();
      }

      timeline.addEventListener('mousedown', function(e) {
        e.preventDefault();
        e.stopPropagation();
        isDragging = true;
        seek(e);
      });
      window.addEventListener('mousemove', function(e) {
        if (isDragging) {
          e.preventDefault();
          seek(e);
        }
      });
      window.addEventListener('mouseup', function() {
        isDragging = false;
      });

      timeline.addEventListener('touchstart', function(e) {
        e.stopPropagation();
        isDragging = true;
        seek(e);
      }, { passive: false });
      window.addEventListener('touchmove', function(e) {
        if (isDragging) {
          seek(e);
        }
      });
      window.addEventListener('touchend', function() {
        isDragging = false;
      });
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPixelVideoPlayers);
  } else {
    initPixelVideoPlayers();
  }

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
if (existsSync('admin')) cpSync('admin', `${OUT}/admin`, { recursive: true });
cpSync('src/fonts', `${OUT}/fonts`, { recursive: true });

// Copia asset CMS (content/ e content/assets/)
if (existsSync(`${C}/assets`)) cpSync(`${C}/assets`, `${OUT}/assets`, { recursive: true });
for (const item of readdirSync(C)) {
  if (/\.(mp4|webm|mov|jpg|jpeg|png|webp|svg)$/i.test(item)) {
    cpSync(join(C, item), join(OUT, item));
  }
}

// Lavori
const lavori = readdirSync(`${C}/lavori`, { withFileTypes: true })
  .filter(d => d.isDirectory() && !d.name.toLowerCase().includes('esempio') && existsSync(`${C}/lavori/${d.name}/progetto.md`))
  .map(d => ({ slug: d.name, ...parse(`${C}/lavori/${d.name}/progetto.md`) }))
  .filter(l => l.meta.bozza !== 'true' && !l.meta.titolo?.toLowerCase().includes('esempio'))
  .sort((a, b) => (Number(a.meta.ordine) || 999) - (Number(b.meta.ordine) || 999));

for (let i = 0; i < lavori.length; i++) {
  const l = lavori[i];
  const outProj = `${OUT}/lavori/${l.slug}`;
  await copyAssets(`${C}/lavori/${l.slug}`, outProj);
  generateProjectPlaceholders(outProj, i + 1, l.meta.titolo || `Progetto ${i+1}`, l.meta.ruolo || 'Design');
}

// Landing
const cards = lavori.map(l => `<li class="card"><a href="lavori/${l.slug}/">
  ${renderMedia(`lavori/${l.slug}/${l.meta.cover}`, `Anteprima di ${l.meta.titolo}`, { width: 1600, height: 900, lazy: true })}
  <h2>${esc(l.meta.titolo)}</h2>
  <p>${esc(l.meta.ruolo)}${l.meta.anno ? ', ' + esc(l.meta.anno) : ''}</p>
</a></li>`).join('\n');

const asteriskSvg = `<svg class="titolo-asterisco" viewBox="0 0 84 86" aria-hidden="true">
  <g transform="translate(42, 43)">
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(72)"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(144)"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(216)"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(288)"/>
  </g>
</svg>`;

let homeConf = {};
if (existsSync(`${C}/home.json`)) {
  try {
    homeConf = JSON.parse(readFileSync(`${C}/home.json`, 'utf8'));
  } catch (e) {}
}

const titoloHero = homeConf.titolo_hero || 'PORTFOLIO';
const videoHero = homeConf.video_hero || 'reveal-video.mp4';
const posterHero = homeConf.poster_hero || '';
const titoloLavori = homeConf.titolo_lavori || 'My Works';
const posterAttr = posterHero ? ` poster="${esc(posterHero)}"` : '';

const heroRevealHtml = `<div class="text-clip-reveal-root" id="textClipReveal" data-text="${esc(titoloHero)}">
  <div class="text-clip-sticky" id="textClipSticky">
    <video class="text-clip-video" autoplay muted loop playsinline preload="auto"${posterAttr}>
      <source src="${esc(videoHero)}" type="video/mp4">
    </video>
  </div>
</div>`;

const homeBody = `<div class="landing-titolo-wrap">
  ${asteriskSvg}
  <h1 class="titolo-testo">${esc(titoloLavori)}</h1>
</div>
<ul class="griglia">
${cards}
</ul>`;

writeFileSync(`${OUT}/index.html`, page({
  depth: 0, current: 'home', desc: site.descrizione,
  hero_html: heroRevealHtml,
  body: homeBody
}));

// Inietta loader nella home
const antiFlicker = `<script>try{var r=false,n=performance.getEntriesByType('navigation')[0];if(n)r=(n.type==='reload');else if(performance.navigation)r=(performance.navigation.type===1);if(document.referrer&&new URL(document.referrer).origin===window.location.origin&&sessionStorage.getItem('portfolio_loader_shown')&&!r){document.documentElement.classList.add('skip-loader');}}catch(e){}</script>`;
const loaderDiv = `<div id="loader" aria-hidden="true"><div class="loader-inner"><div class="loader-log" id="loaderLog"></div><div class="loader-barra"><div class="loader-fill" id="loaderFill"></div></div><p class="loader-pct" id="loaderPct">0%</p></div></div>`;
let homeHtml = readFileSync(`${OUT}/index.html`, 'utf8');
homeHtml = homeHtml.replace(/class="pagina-home">/, '$&' + antiFlicker + loaderDiv).replace('</body>', '<script src="loader.js?v=3.2"></script></body>');
writeFileSync(`${OUT}/index.html`, homeHtml);

// Dettaglio
lavori.forEach((l, i) => {
  const m = l.meta, prev = lavori[i - 1], next = lavori[i + 1];
  const links = list(m.link?.replace(/;/g, ',')).map(x => x.split('|').map(s => s.trim()))
    .filter(([, u]) => u).map(([t, u]) => `<a class="pulsante" href="${esc(u)}" rel="noopener">${esc(t)}</a>`).join('');
  const nav = `<nav class="sequenza" aria-label="More works">
  ${prev ? `<a href="../${prev.slug}/">Previous: ${esc(prev.meta.titolo)}</a>` : '<span></span>'}
  ${next ? `<a href="../${next.slug}/">Next: ${esc(next.meta.titolo)}</a>` : '<span></span>'}
</nav>`;

  const metaItems = [
    m.anno ? `<div><dt>Year</dt><dd>${esc(m.anno)}</dd></div>` : '',
    m.ruolo ? `<div><dt>Role</dt><dd>${esc(m.ruolo)}</dd></div>` : '',
    m.team ? `<div><dt>Team</dt><dd>${esc(m.team)}</dd></div>` : '',
    m.cliente ? `<div><dt>Client</dt><dd>${esc(m.cliente)}</dd></div>` : ''
  ].filter(Boolean).join('\n');

  const heroHtml = m.hero ? `<div class="progetto-hero-media">${renderMedia(m.hero, `Hero di ${m.titolo}`, { priority: true, lazy: false })}</div>` : '';
  const conceptHtml = m.concept ? `<div class="progetto-concept-media">${renderMedia(m.concept, `Concept di ${m.titolo}`, { lazy: false })}</div>` : '';

  const webImgs = [m.web_01, m.web_02].filter(Boolean);
  const finalWeb = webImgs.length ? webImgs : list(m.schermi_web);
  const webHtml = finalWeb.map(f => `<div class="showcase-item showcase-full">${renderMedia(f, '', { lazy: true })}</div>`).join('\n');

  const bannerHtml = m.banner ? `<div class="showcase-item showcase-banner">${renderMedia(m.banner, '', { lazy: true })}</div>` : '';

  const mobImgs = [m.mobile_01, m.mobile_02].filter(Boolean);
  const finalMob = mobImgs.length ? mobImgs : list(m.schermi_mobile);
  const mobileHtml = finalMob.length ? `<div class="showcase-grid-2 showcase-mobile">${finalMob.map(f => `<div class="showcase-col">${renderMedia(f, '', { lazy: true })}</div>`).join('\n')}</div>` : '';

  const merchList = [m.merch_01, m.merch_02].filter(Boolean);
  const finalMerch = merchList.length ? merchList : list(m.merch);
  const merchHtml = finalMerch.length ? `<div class="showcase-grid-2 showcase-merch">${finalMerch.map(f => `<div class="showcase-col">${renderMedia(f, '', { lazy: true })}</div>`).join('\n')}</div>` : '';

  const fallbackImgs = list(m.immagini);
  const fallbackHtml = (!finalWeb.length && !m.banner && !finalMob.length && !finalMerch.length)
    ? fallbackImgs.map(f => `<div class="showcase-item">${renderMedia(f, '', { lazy: true })}</div>`).join('\n')
    : '';

  const detailBody = `<article class="progetto-dettaglio">
<header class="progetto-testata">
  <div class="progetto-titolo-blocco">
    <h1>${esc(m.titolo)}</h1>
    ${heroHtml}
  </div>
  <dl class="meta progetto-meta">
    ${metaItems}
  </dl>
</header>

<div class="progetto-intro-griglia">
  ${conceptHtml}
  <div class="testo progetto-testo">
    ${paras(l.body)}
    ${links ? `<p>${links}</p>` : ''}
  </div>
</div>

<div class="progetto-showcase">
  ${webHtml}
  ${bannerHtml}
  ${mobileHtml}
  ${merchHtml}
  ${fallbackHtml}
</div>

${nav}
</article>`;

  write(`lavori/${l.slug}`, page({
    depth: 2, current: 'progetto', title: m.titolo, desc: l.body.split('\n')[0], back: true,
    body: detailBody
  }));
});

// Chi sono
const about = parse(`${C}/chi-sono/chi-sono.md`);
await copyAssets(`${C}/chi-sono`, `${OUT}/chi-sono`);
generateAboutPlaceholder(`${OUT}/chi-sono`);
const fotoSrc = esc(about.meta.foto || 'foto.svg');
const location = esc(about.meta.location || 'Genova/Italy');

const aboutBody = `<article class="about-layout">
  <div class="about-colonna-sinistra">
    <div class="about-foto">
      ${renderMedia(fotoSrc, `Foto di ${site.nome}`, { priority: true, lazy: false })}
    </div>
  </div>
  
  <div class="about-colonna-destra">
    <div class="testo about-bio">
      ${paras(about.body)}
    </div>
    
    <div class="about-location">
      <span>Located</span>
      <span class="linea-rossa-flex" aria-hidden="true"></span>
      <span>${location}</span>
    </div>
  </div>
</article>`;

write('chi-sono', page({
  depth: 1, current: 'chi-sono', title: 'About me', desc: about.body.split('\n')[0],
  body: aboutBody
}));

// 404: i link e gli stili usano percorsi dalla radice, perché la pagina viene servita a indirizzi qualsiasi
writeFileSync(`${OUT}/404.html`, page({
  depth: 0, root: true, title: 'Pagina non trovata',
  body: `<div class="testo"><h1>Pagina non trovata</h1><p>Questo indirizzo non esiste. Torna alla <a href="/">home</a> per vedere i lavori.</p></div>`
}));
console.log(`Sito generato in /${OUT}: ${lavori.length} lavori.`);
