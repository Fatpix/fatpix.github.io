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
    
    lines = m.group(1).split('\n')
    current_key = None
    current_list = None
    current_dict = None
    multiline_key = None
    multiline_target = None
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(' '))
        
        if multiline_key is not None:
            if not stripped:
                if multiline_target.get('sep') == '\n' and multiline_target['dict'][multiline_key]:
                    multiline_target['dict'][multiline_key] += '\n'
                i += 1
                continue
            if indent > multiline_target['indent']:
                sep = multiline_target.get('sep', ' ')
                prev = multiline_target['dict'][multiline_key]
                multiline_target['dict'][multiline_key] = f"{prev}{sep}{stripped}" if prev else stripped
                i += 1
                continue
            else:
                multiline_target['dict'][multiline_key] = multiline_target['dict'][multiline_key].strip()
                multiline_key = None
                multiline_target = None

        if not stripped or stripped.startswith('#'):
            i += 1
            continue
                
        if indent == 0 and ':' in line:
            idx = line.index(':')
            key = line[:idx].strip()
            val = line[idx+1:].strip().strip('"\'')
            current_key = key
            current_list = None
            current_dict = None
            if val in ('>', '>-', '|', '|-'):
                meta[key] = ""
                multiline_key = key
                multiline_target = {'dict': meta, 'indent': 0, 'sep': '\n' if val.startswith('|') else ' '}
            else:
                meta[key] = val
            i += 1
            continue
            
        if stripped.startswith('- '):
            rest = stripped[2:].strip()
            if current_key and not isinstance(meta.get(current_key), list):
                meta[current_key] = []
            current_list = meta.get(current_key)
                
            if ':' in rest:
                k, v = rest.split(':', 1)
                k = k.strip()
                v = v.strip().strip('"\'')
                current_dict = {k: v}
                if current_list is not None:
                    current_list.append(current_dict)
                if v in ('>', '>-', '|', '|-'):
                    current_dict[k] = ""
                    multiline_key = k
                    multiline_target = {'dict': current_dict, 'indent': indent, 'sep': '\n' if v.startswith('|') else ' '}
            else:
                item_val = rest.strip('"\'')
                if current_list is not None:
                    current_list.append(item_val)
                current_dict = None
            i += 1
            continue
            
        if current_dict is not None and ':' in stripped:
            k, v = stripped.split(':', 1)
            k = k.strip()
            v = v.strip().strip('"\'')
            if v in ('>', '>-', '|', '|-'):
                current_dict[k] = ""
                multiline_key = k
                multiline_target = {'dict': current_dict, 'indent': indent, 'sep': '\n' if v.startswith('|') else ' '}
            else:
                current_dict[k] = v
            i += 1
            continue
            
        if current_key:
            if isinstance(meta.get(current_key), str):
                meta[current_key] = (meta[current_key] + ' ' + stripped).strip()
            elif isinstance(meta.get(current_key), list) and current_dict is None:
                meta[current_key].append(stripped.strip('"\''))
        i += 1
        
    return {'meta': meta, 'body': m.group(2).strip()}

def paras(b):
    ps = [p for p in re.split(r'\n{2,}', b) if p.strip()]
    return '\n'.join([f"<p>{esc(p).replace(chr(10), '<br>')}</p>" for p in ps])

def is_video(src):
    if not src: return False
    return bool(re.search(r'\.(mp4|webm|mov|ogg)$', str(src), re.I))

def render_media(src, alt='', width=None, height=None, priority=False, lazy=None, cls=''):
    if not src: return ''
    u = esc(src)
    a = esc(alt)
    w = f' width="{width}"' if width else ''
    h = f' height="{height}"' if height else ''
    prio = ' fetchpriority="high"' if priority else ''
    lazy_str = ' loading="lazy"' if lazy else (' loading="eager"' if lazy is False else '')
    cls_str = f' class="{cls}"' if cls else ''
    if is_video(src):
        return f'<video src="{u}"{cls_str}{w}{h} autoplay loop muted playsinline preload="metadata" aria-label="{a}"></video>'
    return f'<img src="{u}" alt="{a}"{cls_str}{w}{h}{prio}{lazy_str} decoding="async">'

def copy_assets(from_dir, to_dir):
    os.makedirs(to_dir, exist_ok=True)
    if not os.path.exists(from_dir):
        return
    for f in os.listdir(from_dir):
        if not f.endswith(('.md', '.json')):
            src = os.path.join(from_dir, f)
            dst = os.path.join(to_dir, f)
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)

def generate_project_placeholders(out_dir, num, title, role):
    os.makedirs(out_dir, exist_ok=True)
    files = {
        "cover.svg": f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1600 900" width="100%">
  <rect width="1600" height="900" fill="#ebebeb"/>
  <rect x="32" y="32" width="1536" height="836" fill="none" stroke="#d5d5d5" stroke-width="2"/>
  <g transform="translate(800, 430)" text-anchor="middle">
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

page_loader_html = """<div id="pageLoader" class="page-loader" aria-hidden="true">
  <div class="flip-tile-wave">
    <div class="flip-tile-grid">
      <div class="flip-tile" style="--r:0;--c:0;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:0;--c:1;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:0;--c:2;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:0;--c:3;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:1;--c:0;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:1;--c:1;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:1;--c:2;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:1;--c:3;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:2;--c:0;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:2;--c:1;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:2;--c:2;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:2;--c:3;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:3;--c:0;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:3;--c:1;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:3;--c:2;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
      <div class="flip-tile" style="--r:3;--c:3;"><div class="flip-tile-front"></div><div class="flip-tile-back"></div></div>
    </div>
  </div>
</div>"""

def page(depth=0, title='', desc='', current='', body='', root=False, back=False, hero_html=''):
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

    extra_body = '<div id="scrollProgress" class="scroll-progress" aria-hidden="true"></div><div id="lightbox" class="lightbox" aria-hidden="true" role="dialog" aria-modal="true"><button type="button" class="lightbox-chiudi" aria-label="Chiudi visualizzazione a schermo pieno">x</button><img class="lightbox-img" src="" alt="" style="display:none;"><video class="lightbox-video" src="" autoplay loop muted playsinline controls style="display:none;"></video></div>' if current == 'progetto' else ''

    theme_color = '#000000' if current in ('chi-sono', 'home') else '#f5f5f5'
    template = """<!doctype html>
<html lang="__LANG__" style="background-color:__THEME_COLOR__;">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="__THEME_COLOR__">
<title>__TITLE__</title>
<meta name="description" content="__DESC__">
<meta property="og:title" content="__TITLE__">
<meta property="og:description" content="__DESC__">
<link rel="icon" href="__P__favicon.ico" sizes="any">
<link rel="icon" href="__P__favicon.png" type="image/png" sizes="32x32">
<link rel="icon" href="__P__favicon-192.png" type="image/png" sizes="192x192">
<link rel="icon" href="__P__favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="__P__apple-touch-icon.png">
<link rel="preload" href="__P__fonts/pixelify-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="__P__css/tokens.css?v=3.0">
<link rel="stylesheet" href="__P__css/style.css?v=4.5">
</head>
<body__BODY_CLASS__>
__PAGE_LOADER_HTML__
<script>
(function() {
  var loader = document.getElementById('pageLoader');
  if (!loader) return;
  var isLoaded = false;
  var hideTimer = null;
  var showTimer = setTimeout(function() {
    if (!isLoaded) {
      loader.classList.add('mostra');
      void loader.offsetWidth;
      loader.classList.add('attivo');
    }
  }, 250);

  function dismiss() {
    isLoaded = true;
    clearTimeout(showTimer);
    clearTimeout(hideTimer);
    if (!loader.classList.contains('attivo')) {
      loader.classList.remove('mostra');
      return;
    }
    loader.classList.remove('attivo');
    hideTimer = setTimeout(function() {
      if (!loader.classList.contains('attivo')) {
        loader.classList.remove('mostra');
      }
    }, 380);
  }

  if (document.readyState === 'complete') {
    dismiss();
  } else {
    window.addEventListener('load', function() {
      setTimeout(dismiss, 100);
    });
    setTimeout(dismiss, 6000);
  }
  window.__dismissPageLoader = dismiss;
})();
</script>
<div id="cursorBadge" class="cursor-badge" aria-hidden="true"></div>
__EXTRA_BODY__
<a class="salta" href="#contenuto">Vai al contenuto</a>
<header class="menu">
  <div class="header-safe-cap" aria-hidden="true"></div>
  <button type="button" class="menu-nome" aria-label="__NOME__"><span class="nome-esteso">__NOME__</span><span class="nome-alias" aria-hidden="true">__ALIAS__</span></button>
  <nav class="menu-voci" aria-label="Principale">
    __MENU_LINKS__
  </nav>
</header>
<div class="corpo-pagina">
  __HERO_HTML__
  <main id="contenuto" class="contenitore">
__BODY__
  </main>
</div>
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

      var targetScale = 25;
      var easing = 0.22;
      var eased = 0;
      var isMasked = true;
      var exitThreshold = 0.46;
      var lastHdrChannel = null;

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
        var curAlpha = 1;

        if (eased >= exitThreshold) {
          if (isMasked) {
            mask.style.webkitMaskImage = 'none';
            mask.style.maskImage = 'none';
            isMasked = false;
          }
          curAlpha = 1;
        } else {
          var base = getInitialSize();
          var t = Math.min(1, Math.max(0, eased / exitThreshold));
          var scaleCurve = Math.pow(t, 2.8);
          var size = (base + targetScale * scaleCurve) * 100;
          var sStr = size.toFixed(2) + '% auto, 100% 100%';

          var alpha = 0;
          if (t > 0.25) {
            var aT = (t - 0.25) / (1 - 0.25);
            alpha = Math.pow(aT, 2.0);
          }
          curAlpha = alpha;

          var combinedMask;
          if (alpha <= 0.001) {
            combinedMask = maskData;
            sStr = size.toFixed(2) + '% auto';
          } else {
            var flatAlphaLayer = 'linear-gradient(rgba(0,0,0,' + alpha.toFixed(3) + '), rgba(0,0,0,' + alpha.toFixed(3) + '))';
            combinedMask = maskData + ', ' + flatAlphaLayer;
          }

          mask.style.webkitMaskImage = combinedMask;
          mask.style.maskImage = combinedMask;
          mask.style.webkitMaskSize = sStr;
          mask.style.maskSize = sStr;
          isMasked = true;
        }

        var rRect = root.getBoundingClientRect();
        var mix = (rRect.bottom <= 56) ? 1 : curAlpha;
        var c = Math.round(245 * mix);
        if (c !== lastHdrChannel) {
          var rgbTriplet = c + ', ' + c + ', ' + c;
          var rgbStr = 'rgb(' + rgbTriplet + ')';
          var isDarkDom = (c < 128);
          document.body.style.setProperty('--hdr-rgb', rgbTriplet);
          document.documentElement.style.backgroundColor = rgbStr;
          mask.style.backgroundColor = rgbStr;
          root.style.backgroundColor = rgbStr;
          document.body.classList.toggle('hero-under-header', isDarkDom);
          if (c > 0 && c < 245) {
            document.body.classList.toggle('hero-trans-dark', isDarkDom);
            document.body.classList.toggle('hero-trans-light', !isDarkDom);
          } else {
            document.body.classList.remove('hero-trans-dark', 'hero-trans-light');
          }
          var tc = document.querySelector('meta[name="theme-color"]');
          if (tc) tc.setAttribute('content', isDarkDom ? '#000000' : '#f5f5f5');
          lastHdrChannel = c;
        }

        var hHud = root.querySelector('.pixel-player-hud');
        if (hHud) {
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
      if (t.closest('#textClipReveal') || t.closest('.text-clip-reveal-root') || t.closest('#landingHero') || t.closest('.landing-hero-stage') || t.closest('.sequenza')) {
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
</html>"""
    return (template
        .replace('__LANG__', esc(site.get('lingua', 'it')))
        .replace('__THEME_COLOR__', theme_color)
        .replace('__TITLE__', esc(full))
        .replace('__DESC__', esc(desc or site.get('descrizione', '')))
        .replace('__P__', p)
        .replace('__BODY_CLASS__', ' class="pagina-home hero-under-header"' if current == 'home' else (f' class="pagina-{current}"' if current else ''))
        .replace('__PAGE_LOADER_HTML__', page_loader_html)
        .replace('__EXTRA_BODY__', extra_body)
        .replace('__NOME__', esc(site['nome']))
        .replace('__ALIAS__', esc(site.get('alias', site['nome'])))
        .replace('__MENU_LINKS__', menu_links)
        .replace('__HERO_HTML__', hero_html)
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
if os.path.exists('admin'):
    shutil.copytree('admin', f'{OUT}/admin', dirs_exist_ok=True)
shutil.copytree('src/fonts', f'{OUT}/fonts')

# Copia asset CMS (content/ e content/assets/)
if os.path.exists(f'{C}/assets'):
    shutil.copytree(f'{C}/assets', f'{OUT}/assets', dirs_exist_ok=True)
for item in os.listdir(C):
    if item.endswith(('.mp4', '.webm', '.mov', '.jpg', '.jpeg', '.png', '.webp', '.svg')):
        shutil.copy2(os.path.join(C, item), os.path.join(OUT, item))

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
  {render_media(f"lavori/{l['slug']}/{l['meta'].get('cover', '')}", f"Anteprima di {l['meta'].get('titolo', '')}", width=1600, height=900, lazy=True)}
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

# Lettura configurazione Home Page dal CMS (content/home.json)
home_conf = {}
if os.path.exists(f'{C}/home.json'):
    try:
        with open(f'{C}/home.json', 'r', encoding='utf-8') as f:
            home_conf = json.load(f)
    except Exception:
        pass

titolo_hero = home_conf.get('titolo_hero', 'PORTFOLIO') or 'PORTFOLIO'
video_hero = home_conf.get('video_hero', '') or 'reveal-video.mp4'
poster_hero = home_conf.get('poster_hero', '')
titolo_lavori = home_conf.get('titolo_lavori', 'My Works') or 'My Works'

poster_attr = f' poster="{esc(poster_hero)}"' if poster_hero else ''

hero_reveal_html = f"""<div class="text-clip-reveal-root" id="textClipReveal" data-text="{esc(titolo_hero)}">
  <div class="text-clip-sticky" id="textClipSticky">
    <video class="text-clip-video" autoplay muted loop playsinline preload="auto"{poster_attr}>
      <source src="{esc(video_hero)}" type="video/mp4">
    </video>
  </div>
</div>"""

home_body = f"""<div class="landing-titolo-wrap">
  {asterisk_svg}
  <h1 class="titolo-testo">{esc(titolo_lavori)}</h1>
</div>
<ul class="griglia">
{cards_html}
</ul>"""

with open(f'{OUT}/index.html', 'w', encoding='utf-8') as f:
    f.write(page(depth=0, current='home', desc=site.get('descrizione', ''), body=home_body, hero_html=hero_reveal_html))

anti_flicker = "<script>try{var r=false,n=performance.getEntriesByType('navigation')[0];if(n)r=(n.type==='reload');else if(performance.navigation)r=(performance.navigation.type===1);if(document.referrer&&new URL(document.referrer).origin===window.location.origin&&sessionStorage.getItem('portfolio_loader_shown')&&!r){document.documentElement.classList.add('skip-loader');}}catch(e){}</script>"
loader_div = '<div id="loader" aria-hidden="true"><div class="loader-inner"><div class="loader-log" id="loaderLog"></div><div class="loader-barra"><div class="loader-fill" id="loaderFill"></div></div><p class="loader-pct" id="loaderPct">0%</p></div></div>'
with open(f'{OUT}/index.html', 'r', encoding='utf-8') as f:
    home_html = f.read()

home_html = home_html.replace('class="pagina-home hero-under-header">', 'class="pagina-home hero-under-header">' + anti_flicker + loader_div).replace('</body>', '<script src="loader.js?v=3.2"></script></body>')
with open(f'{OUT}/index.html', 'w', encoding='utf-8') as f:
    f.write(home_html)

# Dettagli
for i, l in enumerate(lavori):
    m = l['meta']
    prev_l = lavori[i-1] if i > 0 else None
    next_l = lavori[i+1] if i < len(lavori) - 1 else None
    
    links_list = [x.split('|') for x in m.get('link', '').replace(';', ',').split(',') if '|' in x]
    links_html = ''.join([f'<a class="pulsante" href="{esc(u.strip())}" rel="noopener">{esc(t.strip())}</a>' for t, u in links_list if u.strip()])
    
    def render_seq_media(item):
        c_file = item['meta'].get('cover') or 'cover.svg'
        src = f"../{item['slug']}/{esc(c_file)}"
        if is_video(c_file):
            return f'<video src="{src}" autoplay loop muted playsinline preload="metadata" data-pixel-player-init="true" aria-hidden="true"></video>'
        return f'<img src="{src}" alt="" loading="lazy" decoding="async">'

    prev_link = f"""<a class="sequenza-item is-prev" href="../{prev_l["slug"]}/">
    <div class="sequenza-text">
      <div class="sequenza-meta"><span>Previous</span></div>
      <div class="sequenza-name"><span class="sequenza-arrow" aria-hidden="true">←</span><span>{esc(prev_l["meta"]["titolo"])}</span></div>
      {f'<div class="sequenza-role">{esc(prev_l["meta"]["ruolo"])}</div>' if prev_l["meta"].get("ruolo") else ''}
    </div>
    <div class="sequenza-thumb" aria-hidden="true">{render_seq_media(prev_l)}</div>
  </a>""" if prev_l else '<span class="sequenza-vuoto" aria-hidden="true"></span>'
    next_link = f"""<a class="sequenza-item is-next" href="../{next_l["slug"]}/">
    <div class="sequenza-thumb" aria-hidden="true">{render_seq_media(next_l)}</div>
    <div class="sequenza-text">
      <div class="sequenza-meta"><span>Next</span></div>
      <div class="sequenza-name"><span>{esc(next_l["meta"]["titolo"])}</span><span class="sequenza-arrow" aria-hidden="true">→</span></div>
      {f'<div class="sequenza-role">{esc(next_l["meta"]["ruolo"])}</div>' if next_l["meta"].get("ruolo") else ''}
    </div>
  </a>""" if next_l else '<span class="sequenza-vuoto" aria-hidden="true"></span>'
    nav_html = f"""<nav class="sequenza" aria-label="More works">
  {prev_link}
  {next_link}
</nav>"""

    # Metadata
    meta_items = []
    if m.get('titolo'):
        meta_items.append(f'<div class="progetto-meta-title"><dt>Project</dt><dd><h1>{esc(m["titolo"])}</h1></dd></div>')
    if m.get('anno'):
        meta_items.append(f'<div class="progetto-meta-year"><dt>Year</dt><dd>{esc(m["anno"])}</dd></div>')
    if m.get('ruolo'):
        meta_items.append(f'<div><dt>Role</dt><dd>{esc(m["ruolo"])}</dd></div>')
    if m.get('team'):
        meta_items.append(f'<div><dt>Team</dt><dd>{esc(m["team"])}</dd></div>')
    if m.get('cliente'):
        meta_items.append(f'<div><dt>Client</dt><dd>{esc(m["cliente"])}</dd></div>')
    meta_html = '\n'.join(meta_items)

    # Modular media
    t_val = m.get('titolo', '')
    hero_img = m.get('hero')
    hero_html = f'<div class="progetto-hero-media">{render_media(hero_img, f"Hero di {t_val}", priority=True, lazy=False)}</div>' if hero_img else ''

    concept_img = m.get('concept')
    concept_html = f'<div class="progetto-concept-media">{render_media(concept_img, f"Concept di {t_val}", lazy=False)}</div>' if concept_img else ''

    raw_web = [m.get('web_01'), m.get('web_02')]
    web_imgs = [x for x in raw_web if x] or [x.strip() for x in m.get('schermi_web', '').split(',') if x.strip()]
    web_html = '\n'.join([f'<div class="showcase-item showcase-full">{render_media(img, "", lazy=True)}</div>' for img in web_imgs])

    banner_img = m.get('banner')
    banner_html = f'<div class="showcase-item showcase-banner">{render_media(banner_img, "", lazy=True)}</div>' if banner_img else ''

    raw_mob = [m.get('mobile_01'), m.get('mobile_02')]
    mobile_imgs = [x for x in raw_mob if x] or [x.strip() for x in m.get('schermi_mobile', '').split(',') if x.strip()]
    mobile_html = f'<div class="showcase-grid-2 showcase-mobile">' + '\n'.join([f'<div class="showcase-col">{render_media(img, "", lazy=True)}</div>' for img in mobile_imgs]) + '</div>' if mobile_imgs else ''

    raw_merch = [m.get('merch_01'), m.get('merch_02')]
    merch_imgs = [x for x in raw_merch if x] or [x.strip() for x in m.get('merch', '').split(',') if x.strip()]
    merch_html = f'<div class="showcase-grid-2 showcase-merch">' + '\n'.join([f'<div class="showcase-col">{render_media(img, "", lazy=True)}</div>' for img in merch_imgs]) + '</div>' if merch_imgs else ''

    # Fallback su immagini standard se non ci sono sezioni modulari
    standard_imgs = [x.strip() for x in m.get('immagini', '').split(',') if x.strip()]
    fallback_html = '\n'.join([f'<div class="showcase-item">{render_media(img, "", lazy=True)}</div>' for img in standard_imgs]) if not (web_imgs or banner_img or mobile_imgs or merch_imgs) else ''

    detail_body = f"""<article class="progetto-dettaglio">
<header class="progetto-testata">
  <div class="progetto-testata-griglia{' senza-hero' if not hero_img else ''}">
    {hero_html}
    <dl class="meta progetto-meta">
      {meta_html}
    </dl>
  </div>
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
def read_about_json(name):
    p = f'{C}/chi-sono/{name}'
    if not os.path.exists(p):
        return {}
    try:
        with open(p, 'r', encoding='utf-8') as jf:
            return json.load(jf)
    except Exception:
        return {}

skills_conf = read_about_json('skills.json')
exp_conf = read_about_json('experience.json')
term_conf = read_about_json('terminal.json')

copy_assets(f'{C}/chi-sono', f'{OUT}/chi-sono')
generate_about_placeholder(f'{OUT}/chi-sono')
foto_src = esc(about['meta'].get('foto', 'foto.svg'))
location = esc(about['meta'].get('location', 'Genova/Italy'))
titolo_skills = esc(skills_conf.get('titolo_skills') or about['meta'].get('titolo_skills', 'Skills') or 'Skills')
titolo_experience = esc(exp_conf.get('titolo_experience') or about['meta'].get('titolo_experience', 'Experience') or 'Experience')
esperienze_raw = exp_conf.get('esperienze') or about['meta'].get('esperienze', [])
if not esperienze_raw or not isinstance(esperienze_raw, list):
    esperienze_raw = [
        {
            "azienda": "Fatpix Studio",
            "ruolo": "Founder · Creative Technologist · Motion Designer",
            "periodo": "2023-···",
            "stato": "active",
            "descrizione": "Studio indipendente di visual design e creative technology con sede a Genova. Progettazione di identità visive dinamiche, modellazione e animazione 3D, creative coding e sviluppo di interfacce web interattive ad alto impatto emotivo.",
            "ref": "FP-019",
            "durata": "±28 MO",
            "link": ""
        },
        {
            "azienda": "Visual & Web Designer Freelance",
            "ruolo": "UI/UX Designer · Creative Frontend Craft",
            "periodo": "2021-2023",
            "stato": "archive",
            "descrizione": "Progettazione e realizzazione di prodotti digitali end-to-end: wireframing e prototipazione avanzata in Figma, design systems modulari, animazioni CSS e micro-interazioni curate per startup e brand contemporanei.",
            "ref": "0AD7ED0",
            "durata": "±24 MO",
            "link": ""
        },
        {
            "azienda": "Motion Graphics & 3D Specialist",
            "ruolo": "3D Artist · Video Editor · Visual Storytelling",
            "periodo": "2020-2022",
            "stato": "archive",
            "descrizione": "Produzione di teaser animati, render volumetrici e simulazioni visive con Blender, Cinema 4D e After Effects. Post-produzione, sound design e color grading per video promozionali e campagne digitali.",
            "ref": "576602E",
            "durata": "±18 MO",
            "link": ""
        }
    ]

exp_items_html = []
for idx, exp in enumerate(esperienze_raw):
    if not isinstance(exp, dict):
        continue
    azienda = esc(str(exp.get('azienda', '')).strip())
    ruolo = esc(str(exp.get('ruolo', '')).strip())
    periodo = esc(str(exp.get('periodo', '')).strip())
    stato = esc(str(exp.get('stato', 'active')).strip().lower())
    descrizione = esc(str(exp.get('descrizione', '')).strip())
    ref_code = esc(str(exp.get('ref', '')).strip())
    durata = esc(str(exp.get('durata', '')).strip())
    link = esc(str(exp.get('link', '')).strip())

    is_active = (stato == 'active')
    dot_html = '<span class="timeline-dot-active" title="In corso" aria-hidden="true"></span>' if is_active else ''

    if link:
        company_html = f'<a class="timeline-title-link" href="{link}" target="_blank" rel="noopener">{azienda} <span class="timeline-arrow-icon" aria-hidden="true">↗</span></a>'
    else:
        company_html = f'<span class="timeline-title-text">{azienda}</span>'

    row_html = f"""        <div class="timeline-row timeline-row--{stato}" role="row">
          <div class="timeline-col col-time" role="cell">
            <span class="timeline-time-val">{periodo}</span>
            {dot_html}
          </div>
          <div class="timeline-col col-title" role="cell">
            <h3 class="timeline-title">{company_html}</h3>
          </div>
          <div class="timeline-col col-details" role="cell">
            <div class="timeline-role">{ruolo}</div>
            <div class="timeline-desc">{descrizione}</div>
          </div>
        </div>"""
    exp_items_html.append(row_html)

exp_section_html = f"""  <section class="about-experience-sezione" id="experienceSection">
    <div class="landing-titolo-wrap experience-titolo-wrap">
      <svg class="titolo-asterisco" viewBox="0 0 84 86" aria-hidden="true">
        <g transform="translate(42, 43)">
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(72)"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(144)"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(216)"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(288)"/>
        </g>
      </svg>
      <h2 class="titolo-testo">{titolo_experience}</h2>
    </div>

    <div class="timeline-container">
      <div class="timeline-table" role="table" aria-label="Cronologia esperienze e ruoli">
        <div class="timeline-header-row" role="row" aria-hidden="true">
          <div class="timeline-th th-time" role="columnheader">TIME (YEARS)</div>
          <div class="timeline-th th-title" role="columnheader">TITLE</div>
          <div class="timeline-th th-details" role="columnheader">ROLES &amp; FOCUS</div>
        </div>

        <div class="timeline-body" role="rowgroup">
{chr(10).join(exp_items_html)}
        </div>
      </div>
    </div>
  </section>"""

_mostra_term = term_conf.get('mostra_terminale') if 'mostra_terminale' in term_conf else about['meta'].get('mostra_terminale', 'true')
show_terminal = str(_mostra_term).strip().lower() != 'false'
term_title = esc(str(term_conf.get('terminale_titolo') or about['meta'].get('terminale_titolo') or 'fatpix — ~/now — -zsh').strip())
term_command = esc(str(term_conf.get('terminale_comando') or about['meta'].get('terminale_comando') or 'cat ./now.txt').strip())
term_updated = esc(str(term_conf.get('terminale_aggiornamento') or about['meta'].get('terminale_aggiornamento') or '').strip())
term_note_raw = str(term_conf.get('terminale_nota') or about['meta'].get('terminale_nota') or '').strip()

term_meta_html = f"""<div class="mac-terminal-meta">
        {f'<span class="mac-terminal-title">{term_title}</span>' if term_title else '<span></span>'}
        {f'<span class="mac-terminal-badge">{term_updated}</span>' if term_updated else ''}
      </div>""" if (term_title or term_updated) else ''
term_text_html = f'<div class="mac-terminal-text">\n{paras(term_note_raw)}\n        </div>' if term_note_raw else ''

terminal_section_html = f"""  <section class="about-terminal-sezione" id="terminalSection" aria-label="Aggiornamenti e sperimentazioni attuali">
    <div class="mac-terminal" id="macTerminalWindow">
      {term_meta_html}
      <div class="mac-terminal-body">
        <div class="mac-terminal-prompt">
          <span class="term-user">fatpix</span>
          <span class="term-sym">%</span>
          <span class="term-cmd">{term_command}</span>
        </div>
        {term_text_html}
        <div class="mac-terminal-footer-line">
          <span class="term-user">fatpix</span>
          <span class="term-sym">%</span>
          <span class="term-cursor" aria-hidden="true"></span>
        </div>
      </div>
    </div>
  </section>""" if show_terminal else ""

def extract_words(val, default_list):
    if not val:
        return default_list
    if isinstance(val, list):
        items = [str(x).strip() for x in val if str(x).strip()]
        return items if items else default_list
    if isinstance(val, str):
        if '\n' in val:
            items = [x.strip() for x in val.split('\n') if x.strip()]
        else:
            items = [x.strip() for x in val.split(',') if x.strip()]
        return items if items else default_list
    return default_list

default_left = [
  "Web Design", "Motion Graphics", "3D Modeling", "Video Making",
  "Brand Identity", "Creative Direction", "Interaction Design",
  "Visual Storytelling", "Typography & Layout", "UI & UX Craft",
  "Generative Art", "Stop Motion", "Analog Experiments", "Prototyping",
  "Sound & Atmosphere", "Editorial Design", "Digital Experiences", "Creative Coding"
]

default_right = [
  "Three.js & WebGL", "Blender 3D", "After Effects", "Figma",
  "Premiere Pro", "Cinema 4D", "Illustrator", "Photoshop",
  "Modern JavaScript", "CSS Animation", "DaVinci Resolve",
  "35mm Photography", "Hand-made Craft", "Rapid Iteration",
  "Problem Solving", "Swiss Army Knife", "Genova / Italy", "Fatpix Studio"
]

words_left = extract_words(skills_conf.get('parole_sinistra') or about['meta'].get('parole_sinistra'), default_left)
words_right = extract_words(skills_conf.get('parole_destra') or about['meta'].get('parole_destra'), default_right)
words_left_json = json.dumps(words_left, ensure_ascii=False)
words_right_json = json.dumps(words_right, ensure_ascii=False)

coin_3d_script = """<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>
(function() {
  function parseBinarySTL(buffer) {
    var reader = new DataView(buffer);
    var faces = reader.getUint32(80, true);
    var positions = new Float32Array(faces * 3 * 3);
    var normals = new Float32Array(faces * 3 * 3);
    var posOffset = 0;
    var offset = 84;

    for (var face = 0; face < faces; face++) {
      var nx = reader.getFloat32(offset, true);
      var ny = reader.getFloat32(offset + 4, true);
      var nz = reader.getFloat32(offset + 8, true);

      for (var i = 1; i <= 3; i++) {
        var vo = offset + i * 12;
        positions[posOffset] = reader.getFloat32(vo, true);
        positions[posOffset + 1] = reader.getFloat32(vo + 4, true);
        positions[posOffset + 2] = reader.getFloat32(vo + 8, true);

        normals[posOffset] = nx;
        normals[posOffset + 1] = ny;
        normals[posOffset + 2] = nz;
        posOffset += 3;
      }
      offset += 50;
    }

    var geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geom.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
    geom.center();
    geom.computeVertexNormals();
    return geom;
  }

  function init3D() {
    var container = document.getElementById('about3dContainer');
    var loading = document.getElementById('about3dLoading');
    if (!container) return;

    var w = container.clientWidth || 500;
    var h = container.clientHeight || 360;

    var scene = new THREE.Scene();
    var camera = new THREE.PerspectiveCamera(40, w / h, 1, 1000);
    camera.position.set(0, 0, 165);

    var renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(w, h);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.25;
    container.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0xffffff, 0.7));

    var key = new THREE.DirectionalLight(0xffffff, 1.8);
    key.position.set(60, 80, 100);
    scene.add(key);

    var rim = new THREE.DirectionalLight(0xddeeff, 1.5);
    rim.position.set(-60, -40, -80);
    scene.add(rim);

    var redRim = new THREE.PointLight(0xef1111, 1.2, 300);
    redRim.position.set(-80, 20, 40);
    scene.add(redRim);

    var group = new THREE.Group();
    scene.add(group);

    fetch('moneta_testa.stl')
      .then(function(res) {
        if (!res.ok) return fetch('chi-sono/moneta_testa.stl');
        return res;
      })
      .then(function(res) {
        if (!res.ok) throw new Error('HTTP ' + res.status);
        return res.arrayBuffer();
      })
      .then(function(buffer) {
        var geometry = parseBinarySTL(buffer);
        var material = new THREE.MeshStandardMaterial({
          color: 0xdedede,
          metalness: 0.88,
          roughness: 0.22
        });
        var mesh = new THREE.Mesh(geometry, material);
        group.add(mesh);
        if (loading) loading.style.opacity = '0';
        updateSize();
        if (window.__dismissPageLoader) window.__dismissPageLoader();
      })
      .catch(function(err) {
        console.error('3D loading error:', err);
        if (loading) loading.textContent = '[ 3D NON DISPONIBILE ]';
        if (window.__dismissPageLoader) window.__dismissPageLoader();
      });

    var isDragging = false;
    var prevX = 0, prevY = 0;
    var velX = 0, velY = 0;
    var rotX = 0, rotY = 0;
    var autoSpeed = 0.004;

    container.addEventListener('pointerdown', function(e) {
      isDragging = true;
      prevX = e.clientX;
      prevY = e.clientY;
      velX = 0;
      velY = 0;
      container.setPointerCapture(e.pointerId);
    });

    container.addEventListener('pointermove', function(e) {
      if (isDragging) {
        var dx = e.clientX - prevX;
        var dy = e.clientY - prevY;
        rotY += dx * 0.0028;
        rotX += dy * 0.0024;
        rotX = Math.max(-0.6, Math.min(0.6, rotX));
        velY = dx * 0.0012;
        velX = dy * 0.0012;
        prevX = e.clientX;
        prevY = e.clientY;
      }
    });

    function endDrag(e) {
      if (isDragging) {
        isDragging = false;
        try { container.releasePointerCapture(e.pointerId); } catch(_) {}
      }
    }
    container.addEventListener('pointerup', endDrag);
    container.addEventListener('pointercancel', endDrag);

    function updateSize() {
      if (!container || !renderer || !camera) return;
      var curW = container.clientWidth;
      var curH = container.clientHeight;
      if (curW > 0 && curH > 0) {
        camera.aspect = curW / curH;
        camera.updateProjectionMatrix();
        renderer.setSize(curW, curH);
      }
    }
    window.addEventListener('resize', updateSize);
    if (typeof ResizeObserver !== 'undefined') {
      new ResizeObserver(updateSize).observe(container);
    }
    setTimeout(updateSize, 300);
    setTimeout(updateSize, 1000);

    function animate() {
      requestAnimationFrame(animate);

      if (!isDragging) {
        velY += (autoSpeed - velY) * 0.04;
        velX *= 0.88;
        rotY += velY;
        rotX += velX;
        rotX = Math.max(-0.6, Math.min(0.6, rotX));
      }

      group.rotation.y = rotY;
      group.rotation.x = rotX;

      renderer.render(scene, camera);
    }
    animate();
  }

  function initCircleCredits() {
    var LEFT = __WORDS_LEFT__;
    var RIGHT = __WORDS_RIGHT__;

    var LINE = 1.65;
    var GUTTER = 0.65;
    var RADIUS = 9.0;
    var DURATION = 26;
    var GLYPHS = "abcdefghijklmnopqrstuvwxyz!@#$%^&*-_+=;:<>,".split("");
    var randomGlyph = function() { return GLYPHS[Math.floor(Math.random() * GLYPHS.length)]; };
    var SCRAMBLE = { repeat: 3, repeatDelay: 0.04, delayStep: 0.025 };

    var stage = document.getElementById('creditsStage');
    if (!stage) return;

    var rows = Math.max(LEFT.length, RIGHT.length);
    var middle = (rows - 1) / 2;
    stage.style.height = ((rows + 1) * LINE) + 'em';

    var leftSlot = function(row) { return rows - 1 - row; };
    var rightSlot = function(row) { return rows + row; };

    function createNameEl(text, slot, row) {
      if (!text) return null;
      var span = document.createElement('span');
      span.className = 'circle-credit-item';
      span.style.lineHeight = LINE;
      span.dataset.name = 'true';
      span.dataset.slot = slot;

      var inner = document.createElement('span');
      inner.dataset.inner = 'true';
      inner.dataset.row = row;
      inner.style.display = 'inline-block';

      for (var i = 0; i < text.length; i++) {
        var ch = text[i];
        if (ch === ' ') {
          inner.appendChild(document.createTextNode(' '));
        } else {
          var charSpan = document.createElement('span');
          charSpan.className = 'circle-credit-char';
          charSpan.dataset.char = 'true';
          charSpan.textContent = ch;
          inner.appendChild(charSpan);
        }
      }
      span.appendChild(inner);
      return span;
    }

    for (var r = 0; r < rows; r++) {
      var lEl = createNameEl(LEFT[r], leftSlot(r), r);
      if (lEl) stage.appendChild(lEl);
      var rEl = createNameEl(RIGHT[r], rightSlot(r), r);
      if (rEl) stage.appendChild(rEl);
    }

    var names = Array.prototype.slice.call(stage.querySelectorAll('[data-name]'));
    var slots = names.map(function(el) { return Number(el.dataset.slot); });
    var total = rows * 2;

    var em = 12;
    var cx = 0, cy = 0;
    var widths = [];
    var orbitScale = 1;
    var coinContainer = document.getElementById('about3dContainer');

    function measure() {
      em = parseFloat(getComputedStyle(stage).fontSize) || 12;
      cx = stage.clientWidth / 2;
      cy = stage.clientHeight / 2;
      widths = names.map(function(el) { return el.offsetWidth; });
      var maxW = widths.length ? Math.max.apply(null, widths) : 0;
      var nominalEquatorialInset = RADIUS * LINE * em;
      var availableHalf = Math.max(36, cx - maxW - 4);
      orbitScale = nominalEquatorialInset > 0 ? Math.min(1, availableHalf / nominalEquatorialInset) : 1;
      if (coinContainer) {
        if (orbitScale < 1) {
          var targetDiameter = Math.max(88, Math.min(17 * em, nominalEquatorialInset * orbitScale * 1.8));
          coinContainer.style.width = targetDiameter.toFixed(1) + 'px';
          coinContainer.style.height = targetDiameter.toFixed(1) + 'px';
        } else {
          coinContainer.style.width = '';
          coinContainer.style.height = '';
        }
      }
    }

    function insetAt(row, wordWidth) {
      var d = row - middle;
      var reach = Math.sqrt(Math.max(0, RADIUS * RADIUS - d * d));
      var inset = Math.max(GUTTER, reach * LINE) * em * orbitScale;
      if (typeof wordWidth === 'number' && cx > 0) {
        inset = Math.min(inset, Math.max(4, cx - wordWidth - 4));
      }
      return inset;
    }

    var lap = { progress: 0 };
    function layout() {
      for (var i = 0; i < names.length; i++) {
        var el = names[i];
        var s = (slots[i] + lap.progress * total) % total;
        var k = Math.floor(s);
        var f = s - k;
        var w = widths[i];
        var row, x, opacity = 1;

        if (k < rows - 1) {
          row = rows - 1 - k - f;
          x = -insetAt(row, w) - w;
        } else if (k === rows - 1) {
          var out = f < 0.5;
          row = out ? -f : f - 1;
          x = out ? -insetAt(row, w) - w : insetAt(row, w);
          opacity = Math.abs(1 - 2 * f);
        } else if (k < total - 1) {
          row = k - rows + f;
          x = insetAt(row, w);
        } else {
          var out = f < 0.5;
          row = out ? rows - 1 + f : rows - f;
          x = out ? insetAt(row, w) : -insetAt(row, w) - w;
          opacity = Math.abs(1 - 2 * f);
        }

        var posX = cx + x;
        var posY = cy + ((row - middle) * LINE - LINE / 2) * em;
        el.style.transform = 'translate3d(' + posX.toFixed(1) + 'px,' + posY.toFixed(1) + 'px,0)';
        el.style.opacity = opacity.toFixed(3);
      }
    }

    measure();
    layout();

    window.addEventListener('resize', function() {
      measure();
      layout();
    });

    if (window.gsap) {
      gsap.to(lap, {
        progress: 1,
        duration: DURATION,
        ease: 'none',
        repeat: -1,
        onUpdate: layout
      });

      gsap.from(stage.querySelectorAll('[data-inner]'), {
        opacity: 0,
        filter: 'blur(4px)',
        duration: 1.1,
        ease: 'power2.inOut',
        delay: function(i, el) {
          return 0.15 + Math.abs(Number(el.dataset.row) - middle) * 0.05;
        },
        clearProps: 'filter'
      });
    }

    names.forEach(function(name) {
      var chars = Array.prototype.slice.call(name.querySelectorAll('[data-char]')).map(function(el) {
        return { el: el, original: el.textContent };
      });

      name.addEventListener('mouseenter', function() {
        chars.forEach(function(item, idx) {
          if (!window.gsap) return;
          gsap.killTweensOf(item.el);
          item.el.textContent = item.original;
          item.el.style.width = item.el.getBoundingClientRect().width + 'px';

          gsap.fromTo(item.el,
            { opacity: 0 },
            {
              opacity: 1,
              duration: 0.03,
              repeat: SCRAMBLE.repeat,
              repeatRefresh: true,
              repeatDelay: SCRAMBLE.repeatDelay,
              delay: idx * SCRAMBLE.delayStep,
              ease: 'power1.out',
              textContent: randomGlyph,
              onComplete: function() {
                item.el.textContent = item.original;
                item.el.style.width = '';
              }
            }
          );
        });
      });
    });
  }

  function startWhenReady() {
    var hasThree = typeof THREE !== 'undefined';
    var hasGsap = typeof gsap !== 'undefined';
    var has3D = document.getElementById('about3dContainer');
    var hasStage = document.getElementById('creditsStage');

    if (hasThree && hasGsap && (has3D || hasStage)) {
      if (has3D) init3D();
      if (hasStage) initCircleCredits();
    } else {
      setTimeout(startWhenReady, 50);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', startWhenReady);
  } else {
    startWhenReady();
  }
})();
</script>"""

about_body = f"""<article class="about-sezione">
  <div class="about-layout">
    <div class="about-colonna-sinistra">
      <div class="about-foto">
        {render_media(foto_src, f"Foto di {site.get('nome', '')}", priority=True, lazy=False)}
      </div>
    </div>
    
    <div class="about-colonna-destra">
      <h1 class="about-titolo-marquee" aria-label="Chi Sono? Who Am I? Wer Bin Ich?">
        <span class="sr-only">Chi Sono? Who Am I? Wer Bin Ich?</span>
        <span class="about-marquee-track" aria-hidden="true">
          <span class="about-marquee-group">
            <span>Chi Sono?</span> <span class="about-marquee-star">*</span> <span>Who Am I?</span> <span class="about-marquee-star">*</span> <span>Wer Bin Ich?</span> <span class="about-marquee-star">*</span>
          </span>
          <span class="about-marquee-group" aria-hidden="true">
            <span>Chi Sono?</span> <span class="about-marquee-star">*</span> <span>Who Am I?</span> <span class="about-marquee-star">*</span> <span>Wer Bin Ich?</span> <span class="about-marquee-star">*</span>
          </span>
        </span>
      </h1>

      <div class="testo about-bio">
        {paras(about['body'])}
      </div>
      
      <div class="about-location">
        <span>Located</span>
        <span class="linea-rossa-flex" aria-hidden="true"></span>
        <span>{location}</span>
      </div>
    </div>
  </div>

  <section class="about-skills-sezione">
    <div class="landing-titolo-wrap skills-titolo-wrap">
      <svg class="titolo-asterisco" viewBox="0 0 84 86" aria-hidden="true">
        <g transform="translate(42, 43)">
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(72)"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(144)"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(216)"/>
          <rect x="-9.5" y="-43" width="19" height="43" fill="currentColor" transform="rotate(288)"/>
        </g>
      </svg>
      <h2 class="titolo-testo">{titolo_skills}</h2>
    </div>

    <div class="about-3d-wrap" id="about3dWrap">
      <div class="circle-credits-stage" id="creditsStage">
        <div class="about-3d-canvas-container" id="about3dContainer" role="img" aria-label="Oggetto 3D interattivo Fatpix">
          <div class="about-3d-loading" id="about3dLoading">[ CARICAMENTO 3D... ]</div>
        </div>
      </div>
      <div class="about-3d-hint" aria-hidden="true">[ ✦ TRASCINA PER RUOTARE ]</div>
    </div>
  </section>

{exp_section_html}
{terminal_section_html}
</article>
{coin_3d_script.replace('__WORDS_LEFT__', words_left_json).replace('__WORDS_RIGHT__', words_right_json)}"""
write('chi-sono', page(depth=1, current='chi-sono', title='About me', desc=about['body'].split('\n')[0], body=about_body))

# 404
write_404 = page(depth=0, root=True, title='Pagina non trovata', body='<div class="testo"><h1>Pagina non trovata</h1><p>Questo indirizzo non esiste. Torna alla <a href="/">home</a> per vedere i lavori.</p></div>')
with open(f'{OUT}/404.html', 'w', encoding='utf-8') as f:
    f.write(write_404)

print(f"Build completato con successo in /{OUT}: {len(lavori)} lavori generati.")
