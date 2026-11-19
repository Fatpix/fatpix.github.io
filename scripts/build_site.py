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
    for f in os.listdir(from_dir):
        if not f.endswith('.md'):
            src = os.path.join(from_dir, f)
            dst = os.path.join(to_dir, f)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

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
</html>"""
    return (template
        .replace('__LANG__', esc(site.get('lingua', 'it')))
        .replace('__TITLE__', esc(full))
        .replace('__DESC__', esc(desc or site.get('descrizione', '')))
        .replace('__P__', p)
        .replace('__BODY_CLASS__', f' class="pagina-{current}"' if current else '')
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
    if os.path.isdir(os.path.join(lavori_dir, d)) and os.path.exists(p_path):
        parsed = parse(p_path)
        if parsed['meta'].get('bozza') != 'true':
            lavori.append({'slug': d, 'meta': parsed['meta'], 'body': parsed['body']})

def sort_key(item):
    try:
        return int(item['meta'].get('ordine', 999))
    except:
        return 999
lavori.sort(key=sort_key)

for l in lavori:
    copy_assets(f"{C}/lavori/{l['slug']}", f"{OUT}/lavori/{l['slug']}")

# Landing
cards_html = '\n'.join([
    f"""<li class="card"><a href="lavori/{l['slug']}/">
  <img src="lavori/{l['slug']}/{esc(l['meta'].get('cover', ''))}" alt="Anteprima di {esc(l['meta'].get('titolo', ''))}" width="1200" height="900" loading="lazy">
  <h2>{esc(l['meta'].get('titolo', ''))}</h2>
  <p>{esc(l['meta'].get('ruolo', ''))}{', ' + esc(l['meta'].get('anno')) if l['meta'].get('anno') else ''}</p>
</a></li>"""
    for l in lavori
])

home_body = f"""<section class="intro"><h1>{esc(site['nome'])}</h1><p>{esc(site.get('ruolo', ''))}</p></section>\n<ul class="griglia">\n{cards_html}\n</ul>"""

with open(f'{OUT}/index.html', 'w', encoding='utf-8') as f:
    f.write(page(depth=0, current='home', desc=site.get('descrizione', ''), body=home_body))

anti_flicker = "<script>try{var r=false,n=performance.getEntriesByType('navigation')[0];if(n)r=(n.type==='reload');else if(performance.navigation)r=(performance.navigation.type===1);if(document.referrer&&new URL(document.referrer).origin===window.location.origin&&sessionStorage.getItem('portfolio_loader_shown')&&!r){document.documentElement.classList.add('skip-loader');}}catch(e){}</script>"
loader_div = '<div id="loader" aria-hidden="true"><div class="loader-inner"><div class="loader-log" id="loaderLog"></div><div class="loader-barra"><div class="loader-fill" id="loaderFill"></div></div><p class="loader-pct" id="loaderPct">0%</p></div></div>'
cursor_badge = '<div id="cursorBadge" class="cursor-badge" aria-hidden="true">Learn More</div>'
cursor_script = """<script>
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
</script>"""

with open(f'{OUT}/index.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

home_html = home_html.replace('<body__BODY_CLASS__>', '<body__BODY_CLASS__>' + anti_flicker + loader_div + cursor_badge).replace('</body>', '<script src="loader.js"></script>' + cursor_script + '</body>')
with open(f'{OUT}/index.html', 'w', encoding='utf-8') as f:
    f.write(home_html)

# Dettagli
for i, l in enumerate(lavori):
    m = l['meta']
    prev_l = lavori[i-1] if i > 0 else None
    next_l = lavori[i+1] if i < len(lavori) - 1 else None
    
    links_list = [x.split('|') for x in m.get('link', '').replace(';', ',').split(',') if '|' in x]
    links_html = ''.join([f'<a class="pulsante" href="{esc(u.strip())}" rel="noopener">{esc(t.strip())}</a>' for t, u in links_list if u.strip()])
    
    imgs = [x.strip() for x in m.get('immagini', '').split(',') if x.strip()]
    imgs_html = '\n'.join([f'<img src="{esc(img)}" alt="" loading="lazy">' for img in imgs])
    
    prev_link = f'<a href="../{prev_l["slug"]}/">Precedente: {esc(prev_l["meta"]["titolo"])}</a>' if prev_l else '<span></span>'
    next_link = f'<a href="../{next_l["slug"]}/">Successivo: {esc(next_l["meta"]["titolo"])}</a>' if next_l else '<span></span>'
    nav_html = f"""<nav class="sequenza" aria-label="Altri lavori">
  {prev_link}
  {next_link}
</nav>"""

    anno_html = f'<div><dt>Anno</dt><dd>{esc(m["anno"])}</dd></div>' if m.get('anno') else ''
    ruolo_html = f'<div><dt>Ruolo</dt><dd>{esc(m["ruolo"])}</dd></div>' if m.get('ruolo') else ''

    detail_body = f"""<article>
<header class="dettaglio-testa">
  <h1>{esc(m.get('titolo', ''))}</h1>
  <dl class="meta">
    {anno_html}
    {ruolo_html}
  </dl>
</header>
<div class="testo">{paras(l['body'])}{f'<p>{links_html}</p>' if links_html else ''}</div>
<div class="galleria">
{imgs_html}
</div>
{nav_html}
</article>"""
    write(f"lavori/{l['slug']}", page(depth=2, title=m.get('titolo', ''), desc=l['body'].split('\n')[0], back=True, body=detail_body))

# Chi sono
about = parse(f'{C}/chi-sono/chi-sono.md')
copy_assets(f'{C}/chi-sono', f'{OUT}/chi-sono')
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
