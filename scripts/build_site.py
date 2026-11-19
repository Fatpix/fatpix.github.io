import os, json, re, shutil

OUT = 'dist'
C = 'content'

with open(f'{C}/site.json', 'r', encoding='utf-8') as f:
    site = json.load(f)

def esc(s):
    if s is None: return ''
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def parse(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        raw = f.read().replace('\r\n', '\n')
    m = re.match(r'^---\n([\s\S]*?)\n---\n?([\s\S]*)$', raw)
    meta = {}
    if not m:
        return {'meta': meta, 'body': raw.strip()}
    for line in m.group(1).split('\n'):
        if ':' in line:
            idx = line.index(':')
            meta[line[:idx].strip()] = line[idx+1:].strip()
    return {'meta': meta, 'body': m.group(2).strip()}

def paras(b):
    ps = [p for p in re.split(r'\n{2,}', b) if p.strip()]
    return '\n'.join([f"<p>{esc(p).replace(chr(10), '<br>')}</p>" for p in ps])

def copy_assets(from_dir, to_dir):
    os.makedirs(to_dir, exist_ok=True)
    if not os.path.exists(from_dir):
        return
    for f in os.listdir(from_dir):
        if not f.endswith('.md'):
            src = os.path.join(from_dir, f)
            dst = os.path.join(to_dir, f)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

def generate_project_placeholders(out_dir, num, title, role):
    os.makedirs(out_dir, exist_ok=True)
    files = {
        "cover.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%">
  <rect width="1200" height="900" fill="#ebebeb"/>
  <rect x="24" y="24" width="1152" height="852" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(600, 430)" text-anchor="middle">
    <circle cx="0" cy="-60" r="48" fill="none" stroke="#b0b0b0" stroke-width="3"/>
    <text x="0" y="-48" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="32" font-weight="600" fill="#888888">{num:02d}</text>
    <text x="0" y="30" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#333333" letter-spacing="-0.5">{title}</text>
    <text x="0" y="75" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="400" fill="#777777" letter-spacing="1">{role.upper()}</text>
  </g>
</svg>""",
        "hero.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="100%">
  <rect width="1600" height="900" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="836" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(800, 420)" text-anchor="middle">
    <rect x="-140" y="-120" width="280" height="140" rx="8" fill="none" stroke="#999999" stroke-width="2.5" stroke-dasharray="6,6"/>
    <text x="0" y="-42" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="48" font-weight="700" fill="#222222" letter-spacing="-1">{title.upper()}</text>
    <text x="0" y="70" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="22" font-weight="500" fill="#666666" letter-spacing="2">HERO IDENTITY &amp; SYSTEM</text>
    <line x1="-80" y1="110" x2="80" y2="110" stroke="#d5d5d5" stroke-width="2"/>
  </g>
</svg>""",
        "concept.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%">
  <rect width="1200" height="900" fill="#ebebeb"/>
  <rect x="24" y="24" width="1152" height="852" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(600, 400)" text-anchor="middle">
    <circle cx="-120" cy="0" r="90" fill="none" stroke="#cccccc" stroke-width="1.5" stroke-dasharray="4,4"/>
    <circle cx="120" cy="0" r="90" fill="none" stroke="#cccccc" stroke-width="1.5" stroke-dasharray="4,4"/>
    <rect x="-180" y="-90" width="360" height="180" fill="none" stroke="#b0b0b0" stroke-width="2"/>
    <line x1="-240" y1="0" x2="240" y2="0" stroke="#cccccc" stroke-width="1"/>
    <line x1="0" y1="-140" x2="0" y2="140" stroke="#cccccc" stroke-width="1"/>
    <text x="0" y="8" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="32" font-weight="700" fill="#333333">{title}</text>
    <text x="0" y="160" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="500" fill="#666666" letter-spacing="1.5">CONCEPT &amp; GEOMETRIC GRID</text>
    <text x="0" y="195" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#888888">Modular Construction System</text>
  </g>
</svg>""",
        "web-01.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%">
  <rect width="1600" height="1000" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="936" rx="12" fill="#f0f0f0" stroke="#d5d5d5" stroke-width="2"/>
  <rect x="32" y="32" width="1536" height="56" rx="12" fill="#e5e5e5"/>
  <rect x="32" y="76" width="1536" height="12" fill="#e5e5e5"/>
  <circle cx="64" cy="60" r="6" fill="#cccccc"/>
  <circle cx="84" cy="60" r="6" fill="#cccccc"/>
  <circle cx="104" cy="60" r="6" fill="#cccccc"/>
  <rect x="140" y="48" width="400" height="24" rx="4" fill="#ffffff" stroke="#d5d5d5" stroke-width="1"/>
  <text x="155" y="65" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" fill="#888888">https://progetto-{num:02d}.design</text>
  <g transform="translate(800, 520)" text-anchor="middle">
    <rect x="-680" y="-380" width="1360" height="740" fill="#ffffff" rx="6" stroke="#e0e0e0" stroke-width="1.5"/>
    <text x="0" y="-30" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222" letter-spacing="-0.5">WEB EXPERIENCE 01</text>
    <text x="0" y="20" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="400" fill="#666666" letter-spacing="1">DESKTOP HOMEPAGE INTERFACE</text>
    <rect x="-120" y="60" width="240" height="40" rx="4" fill="#ebebeb" stroke="#d0d0d0" stroke-width="1"/>
    <text x="0" y="85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14" font-weight="500" fill="#666666">DESKTOP INTERFACE</text>
  </g>
</svg>""",
        "web-02.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 1000" width="100%">
  <rect width="1600" height="1000" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="936" rx="12" fill="#f0f0f0" stroke="#d5d5d5" stroke-width="2"/>
  <rect x="32" y="32" width="1536" height="56" rx="12" fill="#e5e5e5"/>
  <rect x="32" y="76" width="1536" height="12" fill="#e5e5e5"/>
  <circle cx="64" cy="60" r="6" fill="#cccccc"/>
  <circle cx="84" cy="60" r="6" fill="#cccccc"/>
  <circle cx="104" cy="60" r="6" fill="#cccccc"/>
  <rect x="140" y="48" width="400" height="24" rx="4" fill="#ffffff" stroke="#d5d5d5" stroke-width="1"/>
  <text x="155" y="65" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="12" fill="#888888">https://progetto-{num:02d}.design/catalog</text>
  <g transform="translate(800, 520)" text-anchor="middle">
    <rect x="-680" y="-380" width="1360" height="740" fill="#ffffff" rx="6" stroke="#e0e0e0" stroke-width="1.5"/>
    <text x="0" y="-30" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222" letter-spacing="-0.5">WEB EXPERIENCE 02</text>
    <text x="0" y="20" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="20" font-weight="400" fill="#666666" letter-spacing="1">INTERACTIVE CATALOG &amp; SYSTEM</text>
    <rect x="-120" y="60" width="240" height="40" rx="4" fill="#ebebeb" stroke="#d0d0d0" stroke-width="1"/>
    <text x="0" y="85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="14" font-weight="500" fill="#666666">DESKTOP INTERFACE</text>
  </g>
</svg>""",
        "banner.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1800 750" width="100%">
  <rect width="1800" height="750" fill="#ebebeb"/>
  <rect x="28" y="28" width="1744" height="694" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(900, 360)" text-anchor="middle">
    <rect x="-800" y="-280" width="1600" height="560" fill="#e2e2e2" stroke="#cccccc" stroke-width="1.5"/>
    <text x="0" y="-20" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="52" font-weight="700" fill="#222222" letter-spacing="-0.5">OUTDOOR CAMPAIGN &amp; BANNER</text>
    <text x="0" y="35" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="22" font-weight="400" fill="#666666" letter-spacing="1.5">ENVIRONMENTAL SIGNAGE — {title.upper()}</text>
    <line x1="-120" y1="80" x2="120" y2="80" stroke="#999999" stroke-width="2"/>
  </g>
</svg>""",
        "mobile-01.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1600" width="100%">
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
</svg>""",
        "mobile-02.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 1600" width="100%">
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
</svg>""",
        "merch-01.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1250" width="100%">
  <rect width="1000" height="1250" fill="#ebebeb"/>
  <rect x="24" y="24" width="952" height="1202" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(500, 600)" text-anchor="middle">
    <rect x="-360" y="-460" width="720" height="920" rx="16" fill="#f4f4f4" stroke="#dcdcdc" stroke-width="2"/>
    <rect x="-180" y="-280" width="360" height="360" rx="8" fill="none" stroke="#c0c0c0" stroke-width="2" stroke-dasharray="6,6"/>
    <text x="0" y="-85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222">TOTE BAG MOCKUP</text>
    <text x="0" y="-35" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="18" font-weight="500" fill="#777777" letter-spacing="1">MERCHANDISE &amp; COLLATERAL</text>
    <text x="0" y="200" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#999999">Physical Brand Touchpoint 01</text>
  </g>
</svg>""",
        "merch-02.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1250" width="100%">
  <rect width="1000" height="1250" fill="#ebebeb"/>
  <rect x="24" y="24" width="952" height="1202" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(500, 600)" text-anchor="middle">
    <rect x="-360" y="-460" width="720" height="920" rx="16" fill="#f4f4f4" stroke="#dcdcdc" stroke-width="2"/>
    <rect x="-180" y="-280" width="360" height="360" rx="8" fill="none" stroke="#c0c0c0" stroke-width="2" stroke-dasharray="6,6"/>
    <text x="0" y="-85" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="44" font-weight="700" fill="#222222">PRODUCT MOCKUP</text>
    <text x="0" y="-35" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="18" font-weight="500" fill="#777777" letter-spacing="1">MERCHANDISE &amp; PACKAGING</text>
    <text x="0" y="200" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#999999">Physical Brand Touchpoint 02</text>
  </g>
</svg>"""
    }
    for fname, svg_content in files.items():
        dst = os.path.join(out_dir, fname)
        if not os.path.exists(dst):
            with open(dst, "w", encoding="utf-8") as f:
                f.write(svg_content)

def generate_about_placeholder(out_dir):
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, "foto.svg")
    if not os.path.exists(dst):
        with open(dst, "w", encoding="utf-8") as f:
            f.write("""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 900" width="100%">
  <rect width="1200" height="900" fill="#ebebeb"/>
  <rect x="24" y="24" width="1152" height="852" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(600, 450)" text-anchor="middle">
    <circle cx="0" cy="-40" r="90" fill="none" stroke="#b0b0b0" stroke-width="2"/>
    <circle cx="0" cy="-60" r="35" fill="none" stroke="#999999" stroke-width="2"/>
    <path d="M -55 20 A 55 45 0 0 1 55 20 Z" fill="none" stroke="#999999" stroke-width="2"/>
    <text x="0" y="90" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="28" font-weight="600" fill="#555555" letter-spacing="1">ABOUT ME</text>
    <text x="0" y="125" font-family="'Helvetica Neue', Helvetica, Arial, sans-serif" font-size="16" font-weight="400" fill="#888888">Visual Designer &amp; Creative</text>
  </g>
</svg>""")

def page(depth=0, title='', desc='', current='', body='', root=False, back=False):
    p = '/' if root else '../' * depth
    home = p if p else './'
    full = f"{title} | {site['nome']}" if title else f"{site['nome']} | {site['ruolo']}"
    contatti_items = [
        f'<a href="{esc(x["url"])}" target="_blank" rel="noopener">{esc(x["etichetta"])}</a>'
        for x in site.get('social', [])
    ] + [f'<a href="mailto:{esc(site.get("email",""))}">{esc(site.get("etichetta_email", "Contattami"))}</a>']
    contatti = '<span class="linea linea-corta" aria-hidden="true"></span>'.join(contatti_items)

    cur_home = ' aria-current="page"' if current == "home" else ''
    cur_about = ' aria-current="page"' if current == "chi-sono" else ''
    if back:
        menu_links = f'<a href="{home}">Back</a>'
    else:
        menu_links = f'<a href="{home}"{cur_home}>Works</a>\n    <a href="{p}chi-sono/"{cur_about}>About me</a>'

    extra_body = '<div id="lightbox" class="lightbox" aria-hidden="true" role="dialog" aria-modal="true"><button type="button" class="lightbox-chiudi" aria-label="Chiudi visualizzazione a schermo pieno">x</button><img class="lightbox-img" src="" alt=""></div>' if current == 'progetto' else ''

    template = """<!doctype html>
<html lang="__LANG__">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<link rel="icon" href="__P__favicon.svg" type="image/svg+xml">
<link rel="preload" href="__P__fonts/pixelify-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="__P__css/tokens.css">
<link rel="stylesheet" href="__P__css/style.css">
</head>
<body__BODY_CLASS__>
<div id="cursorBadge" class="cursor-badge" aria-hidden="true"></div>
__EXTRA_BODY__
<a class="salta" href="#contenuto">Vai al contenuto</a>
<header class="menu">
  <button type="button" class="menu-nome" aria-label="__NOME__"><span class="nome-esteso">__NOME__</span><span class="nome-alias" aria-hidden="true">__ALIAS__</span></button>
  <nav class="menu-voci" aria-label="Principale">
    __MENU_LINKS__
  </nav>
</header>
<main id="contenuto" class="contenitore">
__BODY__
</main>
<footer class="footer">
  <p class="footer-titolo">__FOOTER_TITOLO__</p>
  <div class="footer-riga">
    <span>__NOME__</span>
    <span class="linea linea-lunga" aria-hidden="true"></span>
    <nav class="footer-contatti" aria-label="Contatti">__CONTATTI__</nav>
  </div>
</footer>
<script>
(function() {
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
      if (t.closest('.about-foto')) {
        setBadge('Hi, this is me!');
      } else if (t.closest('.progetto-hero-media, .progetto-concept-media, .progetto-showcase, .progetto-dettaglio img')) {
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
    var btnChiudi = lb.querySelector('.lightbox-chiudi');
    var openLb = function(src, alt) {
      lbImg.src = src;
      lbImg.alt = alt || '';
      lb.classList.add('aperto');
      lb.setAttribute('aria-hidden', 'false');
      document.body.style.overflow = 'hidden';
      if (badge) badge.classList.remove('visibile');
    };
    var closeLb = function() {
      lb.classList.remove('aperto');
      lb.setAttribute('aria-hidden', 'true');
      document.body.style.overflow = '';
      lbImg.src = '';
    };

    document.querySelectorAll('.progetto-hero-media img, .progetto-concept-media img, .progetto-showcase img').forEach(function(img) {
      img.addEventListener('click', function() {
        openLb(img.src, img.alt);
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
})();
</script>
</body>
</html>"""
    return (template
        .replace('__LANG__', esc(site.get('lingua', 'it')))
        .replace('__TITLE__', esc(full))
        .replace('__DESC__', esc(desc or site.get('descrizione', '')))
        .replace('__P__', p)
        .replace('__BODY_CLASS__', f' class="pagina-{current}"' if current else '')
        .replace('__EXTRA_BODY__', extra_body)
        .replace('__NOME__', esc(site['nome']))
        .replace('__ALIAS__', esc(site.get('alias', site['nome'])))
        .replace('__MENU_LINKS__', menu_links)
        .replace('__BODY__', body)
        .replace('__FOOTER_TITOLO__', esc(site.get('footer_titolo', '')))
        .replace('__CONTATTI__', contatti)
    )

def write(path_str, html):
    full_p = os.path.join(OUT, path_str)
    os.makedirs(full_p, exist_ok=True)
    with open(os.path.join(full_p, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)

if os.path.exists(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)
shutil.copytree('src/css', f'{OUT}/css')
shutil.copytree('src/static', OUT, dirs_exist_ok=True)
shutil.copytree('src/fonts', f'{OUT}/fonts')

# Lavori
lavori = []
lavori_dir = f'{C}/lavori'
for d in sorted(os.listdir(lavori_dir)):
    p_path = os.path.join(lavori_dir, d, 'progetto.md')
    if os.path.isdir(os.path.join(lavori_dir, d)) and 'esempio' not in d.lower() and os.path.exists(p_path):
        parsed = parse(p_path)
        if parsed['meta'].get('bozza') != 'true' and 'esempio' not in parsed['meta'].get('titolo', '').lower():
            lavori.append({'slug': d, 'meta': parsed['meta'], 'body': parsed['body']})

def sort_key(item):
    try:
        return int(item['meta'].get('ordine', 999))
    except:
        return 999
lavori.sort(key=sort_key)

for i, l in enumerate(lavori):
    out_proj = f"{OUT}/lavori/{l['slug']}"
    copy_assets(f"{C}/lavori/{l['slug']}", out_proj)
    generate_project_placeholders(out_proj, i + 1, l['meta'].get('titolo', f'Progetto {i+1}'), l['meta'].get('ruolo', 'Design'))

# Landing
cards_html = '\n'.join([
    f"""<li class="card"><a href="lavori/{l['slug']}/">
  <img src="lavori/{l['slug']}/{esc(l['meta'].get('cover', ''))}" alt="Anteprima di {esc(l['meta'].get('titolo', ''))}" width="1200" height="900" loading="lazy">
  <h2>{esc(l['meta'].get('titolo', ''))}</h2>
  <p>{esc(l['meta'].get('ruolo', ''))}{', ' + esc(l['meta'].get('anno')) if l['meta'].get('anno') else ''}</p>
</a></li>"""
    for l in lavori
])

asterisk_svg = """<svg class="titolo-asterisco" viewBox="0 0 84 86" aria-hidden="true">
  <g transform="translate(42, 43)">
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(72)"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(144)"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(216)"/>
    <rect x="-9.5" y="-43" width="19" height="43" fill="#000000" transform="rotate(288)"/>
  </g>
</svg>"""

home_body = f"""<div class="landing-titolo-wrap">
  {asterisk_svg}
  <h1 class="titolo-testo">My Works</h1>
</div>
<ul class="griglia">
{cards_html}
</ul>"""

with open(f'{OUT}/index.html', 'w', encoding='utf-8') as f:
    f.write(page(depth=0, current='home', desc=site.get('descrizione', ''), body=home_body))

anti_flicker = "<script>try{var r=false,n=performance.getEntriesByType('navigation')[0];if(n)r=(n.type==='reload');else if(performance.navigation)r=(performance.navigation.type===1);if(document.referrer&&new URL(document.referrer).origin===window.location.origin&&sessionStorage.getItem('portfolio_loader_shown')&&!r){document.documentElement.classList.add('skip-loader');}}catch(e){}</script>"
loader_div = '<div id="loader" aria-hidden="true"><div class="loader-inner"><div class="loader-log" id="loaderLog"></div><div class="loader-barra"><div class="loader-fill" id="loaderFill"></div></div><p class="loader-pct" id="loaderPct">0%</p></div></div>'
with open(f'{OUT}/index.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

home_html = home_html.replace('class="pagina-home">', 'class="pagina-home">' + anti_flicker + loader_div).replace('</body>', '<script src="loader.js"></script></body>')
with open(f'{OUT}/index.html', 'w', encoding='utf-8') as f:
    f.write(home_html)

# Dettagli
for i, l in enumerate(lavori):
    m = l['meta']
    prev_l = lavori[i-1] if i > 0 else None
    next_l = lavori[i+1] if i < len(lavori) - 1 else None
    
    links_list = [x.split('|') for x in m.get('link', '').replace(';', ',').split(',') if '|' in x]
    links_html = ''.join([f'<a class="pulsante" href="{esc(u.strip())}" rel="noopener">{esc(t.strip())}</a>' for t, u in links_list if u.strip()])
    
    prev_link = f'<a href="../{prev_l["slug"]}/">Precedente: {esc(prev_l["meta"]["titolo"])}</a>' if prev_l else '<span></span>'
    next_link = f'<a href="../{next_l["slug"]}/">Successivo: {esc(next_l["meta"]["titolo"])}</a>' if next_l else '<span></span>'
    nav_html = f"""<nav class="sequenza" aria-label="Altri lavori">
  {prev_link}
  {next_link}
</nav>"""

    # Metadata
    meta_items = []
    if m.get('anno'):
        meta_items.append(f'<div><dt>Anno</dt><dd>{esc(m["anno"])}</dd></div>')
    if m.get('ruolo'):
        meta_items.append(f'<div><dt>Ruolo</dt><dd>{esc(m["ruolo"])}</dd></div>')
    if m.get('team'):
        meta_items.append(f'<div><dt>Team</dt><dd>{esc(m["team"])}</dd></div>')
    if m.get('cliente'):
        meta_items.append(f'<div><dt>Cliente</dt><dd>{esc(m["cliente"])}</dd></div>')
    meta_html = '\n'.join(meta_items)

    # Modular media
    hero_img = m.get('hero')
    hero_html = f'<div class="progetto-hero-media"><img src="{esc(hero_img)}" alt="Hero di {esc(m.get("titolo", ""))}"></div>' if hero_img else ''

    concept_img = m.get('concept')
    concept_html = f'<div class="progetto-concept-media"><img src="{esc(concept_img)}" alt="Concept di {esc(m.get("titolo", ""))}"></div>' if concept_img else ''

    web_imgs = [x.strip() for x in m.get('schermi_web', '').split(',') if x.strip()]
    web_html = '\n'.join([f'<div class="showcase-item showcase-full"><img src="{esc(img)}" alt="" loading="lazy"></div>' for img in web_imgs])

    banner_img = m.get('banner')
    banner_html = f'<div class="showcase-item showcase-banner"><img src="{esc(banner_img)}" alt="" loading="lazy"></div>' if banner_img else ''

    mobile_imgs = [x.strip() for x in m.get('schermi_mobile', '').split(',') if x.strip()]
    mobile_html = f'<div class="showcase-grid-2 showcase-mobile">' + '\n'.join([f'<div class="showcase-col"><img src="{esc(img)}" alt="" loading="lazy"></div>' for img in mobile_imgs]) + '</div>' if mobile_imgs else ''

    merch_imgs = [x.strip() for x in m.get('merch', '').split(',') if x.strip()]
    merch_html = f'<div class="showcase-grid-2 showcase-merch">' + '\n'.join([f'<div class="showcase-col"><img src="{esc(img)}" alt="" loading="lazy"></div>' for img in merch_imgs]) + '</div>' if merch_imgs else ''

    # Fallback su immagini standard se non ci sono sezioni modulari
    standard_imgs = [x.strip() for x in m.get('immagini', '').split(',') if x.strip()]
    fallback_html = '\n'.join([f'<div class="showcase-item"><img src="{esc(img)}" alt="" loading="lazy"></div>' for img in standard_imgs]) if not (web_imgs or banner_img or mobile_imgs or merch_imgs) else ''

    detail_body = f"""<article class="progetto-dettaglio">
<header class="progetto-testata">
  <div class="progetto-titolo-blocco">
    <h1>{esc(m.get('titolo', ''))}</h1>
    {hero_html}
  </div>
  <dl class="meta progetto-meta">
    {meta_html}
  </dl>
</header>

<div class="progetto-intro-griglia">
  {concept_html}
  <div class="testo progetto-testo">
    {paras(l['body'])}
    {f'<p>{links_html}</p>' if links_html else ''}
  </div>
</div>

<div class="progetto-showcase">
  {web_html}
  {banner_html}
  {mobile_html}
  {merch_html}
  {fallback_html}
</div>

{nav_html}
</article>"""
    write(f"lavori/{l['slug']}", page(depth=2, current='progetto', title=m.get('titolo', ''), desc=l['body'].split('\n')[0], back=True, body=detail_body))

# Chi sono
about = parse(f'{C}/chi-sono/chi-sono.md')
copy_assets(f'{C}/chi-sono', f'{OUT}/chi-sono')
generate_about_placeholder(f'{OUT}/chi-sono')
foto_src = esc(about['meta'].get('foto', 'foto.svg'))
location = esc(about['meta'].get('location', 'Genova/Italy'))

about_body = f"""<article class="about-layout">
  <div class="about-colonna-sinistra">
    <div class="about-foto">
      <img src="{foto_src}" alt="Placeholder" width="1200" height="900">
    </div>
  </div>
  
  <div class="about-colonna-destra">
    <div class="testo about-bio">
      {paras(about['body'])}
    </div>
    
    <div class="about-location">
      <span>Located</span>
      <span class="linea-rossa-flex" aria-hidden="true"></span>
      <span>{location}</span>
    </div>
  </div>
</article>"""
write('chi-sono', page(depth=1, current='chi-sono', title='About me', desc=about['body'].split('\n')[0], body=about_body))

# 404
write_404 = page(depth=0, root=True, title='Pagina non trovata', body='<div class="testo"><h1>Pagina non trovata</h1><p>Questo indirizzo non esiste. Torna alla <a href="/">home</a> per vedere i lavori.</p></div>')
with open(f'{OUT}/404.html', 'w', encoding='utf-8') as f:
    f.write(write_404)

print(f"Build completato con successo in /{OUT}: {len(lavori)} lavori generati.")
