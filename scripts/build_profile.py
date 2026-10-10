"""Dependency-free profile builder; fetch failure leaves existing assets untouched."""
import argparse
import datetime as dt
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ESC = html.escape

class Calendar(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tips = {}
        self.tip_id = None
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('data-date') and 'data-level' in a:
            date = a['data-date']
            dt.date.fromisoformat(date)
            self.cells[date] = {'date': date, 'level': int(a['data-level']), 'id': a.get('id', '')}
        if tag == 'tool-tip':
            self.tip_id = a.get('for')
    def handle_data(self, data):
        if self.tip_id:
            self.tips[self.tip_id] = self.tips.get(self.tip_id, '') + data
    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tip_id = None
    def days(self):
        result = []
        for d in sorted(self.cells.values(), key=lambda x: x['date']):
            tip = self.tips.get(d.pop('id'), '')
            m = re.search(r'([\d,]+) contribution', tip)
            d['count'] = int(m[1].replace(',', '')) if m else (0 if 'No contributions' in tip else None)
            if not 0 <= d['level'] <= 4:
                raise ValueError('Unexpected contribution level')
            result.append(d)
        if len(result) < 300 or any(d['count'] is None for d in result):
            raise ValueError('Incomplete contribution calendar; GitHub markup may have changed')
        return result

def svg(body, height, label):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="960" height="{height}" viewBox="0 0 960 {height}" role="img" aria-labelledby="title"><title id="title">{ESC(label)}</title><style>text{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}.reveal{{animation:in .65s ease-out both}}@keyframes in{{from{{opacity:0;transform:translateY(5px)}}to{{opacity:1;transform:translateY(0)}}}}@media(prefers-reduced-motion:reduce){{.reveal{{animation:none}}}}</style><rect x="1" y="1" width="958" height="{height-2}" rx="18" fill="#0d1117" stroke="#30363d"/>{body}</svg>'''

def header(config):
    name = config['name']
    if len(name) > 43 or len(config['tagline']) > 80:
        raise ValueError('Keep name <=43 characters and tagline <=80 characters')
    b = '<circle cx="29" cy="27" r="5" fill="#ff7b72"/><circle cx="47" cy="27" r="5" fill="#e3b341"/><circle cx="65" cy="27" r="5" fill="#3fb950"/>'
    b += '<text x="90" y="32" fill="#8b949e" font-size="12">~/profile · engineering</text>'
    b += f'<g class="reveal"><text x="32" y="87" fill="#79c0ff" font-size="12">$ whoami</text><text x="32" y="126" fill="#f0f6fc" font-size="27" font-weight="600">{ESC(name)}</text><text x="32" y="158" fill="#8b949e" font-size="14">{ESC(config["tagline"])}</text></g>'
    for i, value in enumerate(config['focus'][:3]):
        if len(value) > 43:
            raise ValueError('Focus labels must be <=43 characters')
        b += f'<text class="reveal" style="animation-delay:{.2+i*.12}s" x="32" y="{202+i*26}" fill="#c9d1d9" font-size="14"><tspan fill="#58a6ff">0{i+1}</tspan>  {ESC(value)}</text>'
    monogram = [" SSSSS   KK   KK", "SS       KK  KK ", " SSSSS   KKKKK  ", "     SS  KK  KK ", " SSSSS   KK   KK"]
    for i, line in enumerate(monogram):
        b += f'<text class="reveal" style="animation-delay:{.3+i*.13}s" xml:space="preserve" x="650" y="{204+i*20}" fill="#79c0ff" font-size="20">{ESC(line)}</text>'
    return svg(b, 330, name + ': ' + config['tagline'])

def heatmap(days):
    colors = ['#161b22','#173152','#24558a','#388bfd','#79c0ff']
    b = '<text x="32" y="38" fill="#79c0ff" font-size="13">$ activity --last-year</text>'
    if not days:
        b += '<text x="32" y="85" fill="#c9d1d9" font-size="16">Contribution calendar ready to connect.</text><text x="32" y="117" fill="#8b949e" font-size="13">Run the workflow in your profile repository to load real activity.</text>'
        return svg(b, 165, 'Contribution calendar awaiting GitHub data')
    first = dt.date.fromisoformat(days[0]['date'])
    start = first - dt.timedelta(days=(first.weekday()+1)%7)
    last = dt.date.fromisoformat(days[-1]['date'])
    cols = (last-start).days//7+1
    pitch = min(16, 856/cols)
    for d in days:
        date = dt.date.fromisoformat(d['date'])
        col, row = divmod((date-start).days, 7)
        b += f'<rect class="reveal" style="animation-delay:{(col+row)*.012:.3f}s" x="{48+col*pitch:.2f}" y="{65+row*18}" width="{pitch-3:.2f}" height="14" rx="3" fill="{colors[d["level"]]}"><title>{d["date"]}: {d["count"]} contributions</title></rect>'
    total = sum(d['count'] for d in days)
    b += f'<text x="32" y="222" fill="#c9d1d9" font-size="13">{total:,} contributions · {days[0]["date"]} to {days[-1]["date"]}</text>'
    for i,c in enumerate(colors):
        b += f'<rect x="{810+i*18}" y="211" width="13" height="13" rx="3" fill="{c}"/>'
    return svg(b, 250, f'{total} GitHub contributions from {days[0]["date"]} to {days[-1]["date"]}')

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--fetch', action='store_true')
    args = p.parse_args()
    config = json.loads((ROOT/'profile.json').read_text())
    username = config['username'] or os.environ.get('PROFILE_USERNAME', '')
    days = []
    data_path = ROOT/'data/contributions.json'
    if args.fetch:
        if not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?', username):
            raise ValueError('Set username in profile.json or PROFILE_USERNAME')
        req = urllib.request.Request(f'https://github.com/users/{username}/contributions', headers={'User-Agent':'github-profile-builder','Accept-Language':'en-US'})
        with urllib.request.urlopen(req, timeout=30) as r:
            parser = Calendar()
            parser.feed(r.read().decode())
        days = parser.days()
    elif data_path.exists():
        cache = json.loads(data_path.read_text())
        if cache['username'] == username:
            days = cache['days']
    intro = header(config)
    graph = heatmap(days)
    readme = f'''<p align="center">\n  <img src="assets/profile.svg" width="960" alt="{ESC(config['name'], quote=True)} — software engineering and DevOps" />\n</p>\n\nM.S. Computer Science student at NC State, based in Raleigh, NC. Building backend systems, full-stack products, and grounded AI tools. Seeking software engineering opportunities for May 2027 graduation.\n'''
    if config['stack']:
        readme += '\n### Toolbox\n\n' + ' · '.join(config['stack']) + '\n'
    if config['projects']:
        readme += '\n### Selected work\n\n'
        for item in config['projects']:
            readme += f"- **[{item['name']}]({item['url']})** — {item['description']}\n"
    if config['links']:
        readme += '\n' + ' · '.join(f'[{name}]({url})' for name,url in config['links'].items()) + '\n'
    readme += '\n<p align="center">\n  <img src="assets/contributions.svg" width="960" alt="GitHub contribution calendar; refreshed daily" />\n</p>\n\n<!-- Edit profile.json, then run python scripts/build_profile.py. -->\n'
    (ROOT/'assets/profile.svg').write_text(intro)
    (ROOT/'assets/contributions.svg').write_text(graph)
    (ROOT/'README.md').write_text(readme)
    if args.fetch:
        data_path.write_text(json.dumps({'username':username,'days':days},indent=2)+'\n')

if __name__ == '__main__':
    main()
