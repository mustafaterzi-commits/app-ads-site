#!/usr/bin/env python3
"""rizeteknoloji.com.tr sayfalarını üretir: şablon + çeviri JSON'undan dil başına statik HTML.

  python3 _src/build.py

Kaynaklar: _src/template.html (sayfa şablonu), _src/strings.json (dil başına metin), bu dosyadaki APPS listesi.
Çıktı: index.html (İngilizce, kök), <dil>/index.html, sitemap.xml.
Yayın: GitHub Pages main dalının kökünü yayınlar; commit + push = canlı. `_src/` alt çizgiyle başladığı için yayınlanmaz.

Bir uygulama Google Play'e çıkınca: APPS'te o satırın `live` değerini True yap, betiği çalıştır.
Yeni dil: strings.json'a aynı anahtarlarla bir blok ekle, betiği çalıştır.
"""
import datetime, html, json, os, sys

SRC = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SRC)
BASE = 'https://rizeteknoloji.com.tr'

# Beam'in kendi dil sayfaları var; o dillerde bağlantı doğrudan oraya gider.
BEAM_PATHS = {'tr': 'tr/', 'pt-BR': 'pt-br/', 'de': 'de/', 'es': 'es/', 'fr': 'fr/', 'nl': 'nl/', 'hi': 'hi/'}

# (kimlik, ad, simge, site, paket, live, etiketler). {…} etiketleri strings.json'dan çevrilir.
APPS = [
    ('tv', 'Wavvy TV Plus', 'wavvy-tv-plus.png', 'https://tvplus.rizeteknoloji.com.tr/', 'com.wavvy.tvplus', True,
     ['Android TV', '{phone}', '{tablet}', '{langs43}']),
    ('cam', 'Wavvy IP Camera', 'wavvy-cam.png', 'https://cam.rizeteknoloji.com.tr/', 'com.wavvy.cam', True,
     ['Android TV', '{phone}', '{tablet}', 'RTSP · ONVIF']),
    ('player', 'Wavvy Player', 'wavvy-player.png', 'https://player.rizeteknoloji.com.tr/', 'com.wavvy.player', False,
     ['Android TV', '{phone}', '{tablet}', 'MKV · 4K · SMB']),
    ('vault', 'Wavvy Vault', 'wavvy-vault.png', 'https://vault.rizeteknoloji.com.tr/', 'com.wavvy.vault', False,
     ['{phone}', '{tablet}', '{offline}']),
    ('beam', 'Wavvy Beam', 'wavvy-beam.png', 'https://beam.rizeteknoloji.com.tr/', 'com.wavvy.beam', False,
     ['{phone}', '{tablet}', 'Android TV', 'Chromecast · DLNA']),
    ('words', 'Wavvy Words', 'wavvy-words.png', 'https://words.rizeteknoloji.com.tr/', 'com.wavvy.words', False,
     ['{phone}', '{tablet}', 'A1 → C1']),
]

# Her uygulamanın ne yaptığını gösteren küçük ekran çizimi (160×100, süs; ekran okuyucudan gizli).
_ROW = ('<rect x="12" y="{y}" width="136" height="20" rx="5" fill="#fff" opacity=".07"/>'
        '<rect x="18" y="{y4}" width="12" height="12" rx="3.5" fill="{c}"/>'
        '<rect x="36" y="{y8}" width="58" height="4" rx="2" fill="#fff" opacity=".3"/>'
        '<g fill="#fff" opacity=".75"><circle cx="124" cy="{y10}" r="1.6"/><circle cx="130" cy="{y10}" r="1.6"/>'
        '<circle cx="136" cy="{y10}" r="1.6"/><circle cx="142" cy="{y10}" r="1.6"/></g>')


def _vault():
    rows = ''.join(_ROW.format(y=y, y4=y + 4, y8=y + 8, y10=y + 10, c=c)
                   for y, c in ((14, '#7d93ad'), (40, '#ffc233'), (66, '#7d93ad')))
    return '<rect width="160" height="100" fill="#0a1226"/>' + rows


def _words():
    fills = {'c': '#d3e6e1', 'ok': '#e2f0dc', 's': '#ffe3a8', 'cur': '#ffc04a'}
    grid = [['c', 'c', 'c', 'c', 'c'],
            ['c', ('ok', 'S'), ('ok', 'E'), ('ok', 'A'), ('ok', 'T')],
            ['c', ('s', 'P'), ('s', 'A'), 'cur', ('ok', 'E')]]
    out = ['<rect width="160" height="100" fill="#f6f1e4"/>',
           '<g stroke="#2a3b3a" stroke-width=".7" font-family="system-ui,-apple-system,Segoe UI,Roboto,Arial,sans-serif" '
           'font-weight="700" font-size="11" text-anchor="middle">']
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            kind, ch = cell if isinstance(cell, tuple) else (cell, '')
            x, y = 25 + c * 22, 17 + r * 22
            out.append(f'<rect x="{x}" y="{y}" width="22" height="22" fill="{fills[kind]}"/>')
            if ch:
                out.append(f'<text x="{x + 11}" y="{y + 15}" stroke="none" fill="{"#2f7d3b" if kind == "ok" else "#1f2a2a"}">{ch}</text>')
    out.append('</g>')
    return ''.join(out)


SCENES = {
    'tv': ('<rect width="160" height="100" fill="#0a1226"/><circle cx="16" cy="15" r="4" fill="#1f4fd8"/>'
           '<rect x="25" y="13" width="36" height="4" rx="2" fill="#fff" opacity=".16"/>'
           '<rect x="12" y="30" width="41" height="38" rx="5" fill="#1f4fd8"/>'
           '<rect x="9.5" y="27.5" width="46" height="43" rx="7" fill="none" stroke="#ffc233" stroke-width="1.6"/>'
           '<path d="M28 41v16l13-8z" fill="#fff"/><rect x="60" y="30" width="41" height="38" rx="5" fill="#9248a6"/>'
           '<rect x="107" y="30" width="41" height="38" rx="5" fill="#fff" opacity=".16"/>'
           '<rect x="12" y="80" width="95" height="4" rx="2" fill="#fff" opacity=".16"/>'
           '<rect x="12" y="89" width="62" height="4" rx="2" fill="#fff" opacity=".16"/>'),
    'cam': ('<defs><pattern id="ns" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            '<rect width="4" height="8" fill="#1c2748"/></pattern></defs>'
            '<rect width="160" height="100" fill="#0a1226"/>'
            '<rect x="6" y="6" width="72" height="42" rx="3" fill="#8ec5ee"/><path d="M6 29.5h72V45a3 3 0 0 1-3 3H9a3 3 0 0 1-3-3z" fill="#5f9a57"/>'
            '<circle cx="72" cy="12" r="2.4" fill="#ff4d4d"/>'
            '<rect x="82" y="6" width="72" height="42" rx="3" fill="#1b2a52"/><path d="M82 32h72v13a3 3 0 0 1-3 3H85a3 3 0 0 1-3-3z" fill="#27324a"/>'
            '<circle cx="140" cy="16" r="4" fill="#f4e7b0"/>'
            '<rect x="6" y="52" width="72" height="42" rx="3" fill="#d9c6a4"/><path d="M6 72h72v19a3 3 0 0 1-3 3H9a3 3 0 0 1-3-3z" fill="#a8845c"/>'
            '<rect x="82" y="52" width="72" height="42" rx="3" fill="#141c33"/><rect x="82" y="52" width="72" height="42" rx="3" fill="url(#ns)"/>'
            '<g fill="#000" opacity=".45"><rect x="10" y="41" width="18" height="3" rx="1.5"/><rect x="86" y="41" width="18" height="3" rx="1.5"/>'
            '<rect x="10" y="87" width="18" height="3" rx="1.5"/><rect x="86" y="87" width="18" height="3" rx="1.5"/></g>'),
    'player': ('<defs><linearGradient id="pl" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4b2c92"/>'
               '<stop offset=".75" stop-color="#0a1226"/></linearGradient></defs>'
               '<rect width="160" height="100" fill="url(#pl)"/><circle cx="80" cy="40" r="14" fill="#fff" opacity=".18"/>'
               '<path d="M75.5 33v14l11.5-7z" fill="#fff"/><rect x="45" y="68" width="70" height="7" rx="2.2" fill="#000" opacity=".55"/>'
               '<rect x="13" y="86" width="134" height="3" rx="1.5" fill="#fff" opacity=".22"/>'
               '<rect x="13" y="86" width="56" height="3" rx="1.5" fill="#ffc233"/>'),
    'vault': _vault(),
    'beam': ('<rect width="160" height="100" fill="#0a1226"/>'
             '<rect x="18" y="22" width="26" height="56" rx="5" fill="#6a2f0a" stroke="#fff" stroke-opacity=".8" stroke-width="1.8"/>'
             '<g fill="none" stroke="#ffc233" stroke-width="1.8" stroke-linecap="round"><path d="M52.95 45.05a7 7 0 0 1 0 9.9"/>'
             '<path d="M57.19 40.81a13 13 0 0 1 0 18.38"/><path d="M61.44 36.56a19 19 0 0 1 0 26.88"/></g>'
             '<rect x="74" y="22" width="74" height="46" rx="4" fill="#b84e0c"/>'
             '<rect x="100" y="72" width="22" height="3.5" rx="1.75" fill="#fff" opacity=".35"/><path d="M105.5 37v16l13-8z" fill="#fff"/>'),
    'words': _words(),
}

GP = '<svg aria-hidden="true"><use href="#gp"/></svg>'


def esc(s):
    return html.escape(s, quote=False)


def att(s):
    return html.escape(s, quote=True)


def tile(app, t, code):
    aid, name, icon, site, pkg, live, tags = app
    if aid == 'beam':
        site += BEAM_PATHS.get(code, '')
    tag_html = ''.join(f'<li>{esc(x.format(**t))}</li>' for x in tags)
    play = (f'<a class="btn solid" href="https://play.google.com/store/apps/details?id={pkg}&amp;hl={t["play_hl"]}">{GP}Google Play</a>'
            if live else '')
    status = f'<span class="st{" live" if live else ""}">{esc(t["live"] if live else t["soon"])}</span>'
    return (f'    <article class="tile{" wide" if aid == "tv" else ""}" style="--c:var(--{aid})">\n'
            f'     <div class="txt">\n'
            f'      <div class="top"><img src="/img/{icon}" alt="" width="48" height="48" loading="lazy">{status}</div>\n'
            f'      <h3>{name}</h3>\n'
            f'      <p>{esc(t[aid])}</p>\n'
            f'      <ul class="tags">{tag_html}</ul>\n'
            f'      <div class="acts">{play}<a class="btn ghost" href="{site}">{esc(t["site"])}</a></div>\n'
            f'     </div>\n'
            f'     <div class="art"><svg viewBox="0 0 160 100" aria-hidden="true">{SCENES[aid]}</svg></div>\n'
            f'    </article>')


def root_script(strings):
    """Kök sayfa: dil seçilmemişse tarayıcı diline uyan sayfaya bir kez yönlendirir (eski EN/TR otomatiğinin karşılığı)."""
    m = {}
    for code, t in strings.items():
        if code == 'en':
            continue
        m[code.lower()] = t['path']
        m.setdefault(code.split('-')[0].lower(), t['path'])
    return ('<script>(function(){var m=' + json.dumps(m, separators=(',', ':')) +
            ',s=null;try{s=localStorage.getItem("lang")}catch(e){}'
            'var l=(s||navigator.language||"").toLowerCase(),p=m[l]||m[l.split("-")[0]];'
            'if(p)location.replace(p)})();</script>')


def main():
    with open(os.path.join(SRC, 'strings.json'), encoding='utf-8') as f:
        strings = json.load(f)
    with open(os.path.join(SRC, 'template.html'), encoding='utf-8') as f:
        template = f.read()

    keys = set(strings['en'])
    for code, t in strings.items():
        if set(t) != keys:
            sys.exit(f'{code}: anahtarlar İngilizce ile aynı değil: {sorted(set(t) ^ keys)}')

    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{c}" href="{BASE}{t["path"]}">' for c, t in strings.items())
    hreflang += f'\n<link rel="alternate" hreflang="x-default" href="{BASE}/">'
    today = datetime.date.today()
    fonts = 'https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Instrument+Sans:wght@400..700'

    for code, t in strings.items():
        v = {k: esc(x) for k, x in t.items()}
        v.update(
            html_lang=t['html_lang'], og_locale=t['og_locale'], path=t['path'], url=BASE + t['path'],
            title=esc(t['title']), description=att(t['description']), og_description=att(t['og_description']),
            nav_label=att(t['nav_label']), lang_label=att(t['lang_label']), lang_name=esc(t['name']), lang_short=code.split('-')[0].upper(),
            h1=t['h1'], hreflang=hreflang, year=str(today.year),
            ld_langs=json.dumps(list(strings)),
            fonts_url=fonts + ('&family=Noto+Sans+Devanagari:wght@400;600;800' if code == 'hi' else '') + '&display=swap',
            font_extra='"Noto Sans Devanagari",' if code == 'hi' else '',
            dev_url=f'https://play.google.com/store/apps/developer?id=Rize+Teknoloji&amp;hl={t["play_hl"]}',
            root_script=root_script(strings) if code == 'en' else '',
            langmenu='\n'.join(
                f'    <li><a href="{o["path"]}" hreflang="{c}" lang="{o["html_lang"]}"'
                f'{" aria-current=" + chr(34) + "page" + chr(34) if c == code else ""}>{esc(o["name"])}</a></li>'
                for c, o in strings.items()),
            tiles='\n'.join(tile(a, t, code) for a in APPS),
        )
        page = template
        for k, x in v.items():
            page = page.replace('{{' + k + '}}', x)
        if '{{' in page:
            sys.exit(f'{code}: doldurulmamış alan kaldı: {page[page.index("{{"):][:40]}')
        out = os.path.join(ROOT, t['path'].strip('/'), 'index.html')
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8') as f:
            f.write(page)
        print(f'{code:6} {os.path.relpath(out, ROOT)}')

    urls = []
    for t in strings.values():
        alts = ''.join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{BASE}{o["path"]}"/>' for c, o in strings.items())
        urls.append(f'  <url><loc>{BASE}{t["path"]}</loc><lastmod>{today.isoformat()}</lastmod>'
                    f'<priority>{"1.0" if t["path"] == "/" else "0.8"}</priority>{alts}</url>')
    with open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
                + '\n'.join(urls) + '\n</urlset>\n')
    print('sitemap.xml')


if __name__ == '__main__':
    main()
