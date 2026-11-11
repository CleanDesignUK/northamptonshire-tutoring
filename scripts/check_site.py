#!/usr/bin/env python3
"""Quick no-dependency HTML, sitemap, SEO and internal-link checker."""
from pathlib import Path
from html.parser import HTMLParser
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
files=[p for p in ROOT.rglob('*.html') if '/source/' not in str(p) and '/components/' not in str(p) and not p.name.startswith('preview-')]
errs=[]
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.tags=[];self.h1=0;self.title=0;self.description=0;self.canonical=0;self.links=[];self.meta=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='h1':self.h1+=1
        if tag=='title':self.title+=1
        if tag=='meta' and a.get('name')=='description':self.description+=1
        if tag=='link' and a.get('rel')=='canonical':self.canonical+=1
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if tag in ('script','img') and 'src' in a:self.links.append(a['src'])
        if tag=='link' and 'href' in a:self.links.append(a['href'])
for p in files:
    html=p.read_text('utf-8')
    scan=Scan();scan.feed(html)
    for name,value in [('h1',scan.h1),('title',scan.title),('description',scan.description),('canonical',scan.canonical)]:
        if value!=1:errs.append(f'{p.relative_to(ROOT)}: expected one {name}, got {value}')
    for href in scan.links:
        if not href.startswith('/') or href.startswith('//'):continue
        path=href.split('?')[0].split('#')[0]
        if not path or path=='/':continue
        if not (ROOT/path.lstrip('/')).exists():errs.append(f'{p.relative_to(ROOT)}: broken local path {href}')
    if 'application/ld+json' not in html:errs.append(f'{p.relative_to(ROOT)}: missing schema')
urls=len(re.findall(r'<loc>',(ROOT/'sitemap.xml').read_text('utf-8')))
print(f'Checked {len(files)} generated HTML pages; sitemap entries: {urls}')
if len(files)!=urls:errs.append(f'Expected {len(files)} sitemap URLs; found {urls}')

# Site-launch regressions: branded previews, consent-aware tag, and honest reviews.
from html import unescape
reviews=json.loads((ROOT/'data/testimonials.json').read_text(encoding='utf-8'))
logo=ROOT/'assets/images/nwt-group-social-1200x630.jpg'
if not logo.exists():errs.append('Social preview image is missing')
if 'GTM-56GZFL5S' not in (ROOT/'assets/js/gtm-consent.js').read_text(encoding='utf-8'):
    errs.append('Google Tag Manager container is missing')
for page in files:
    data=page.read_text(encoding='utf-8')
    rel=page.relative_to(ROOT).as_posix()
    for token in ('nwt-group-social-1200x630.jpg','og:image:width','twitter:image','mobile-cards.js','gtm-consent.js'):
        if token not in data:errs.append(f'{rel}: missing {token}')
    if rel in ('index.html','about.html','contact.html'):
        if 'id="nt-group-testimonials"' not in data:errs.append(f'{rel}: parent-group reviews missing')
        for review in reviews:
            if review['quote'] not in unescape(data):errs.append(f'{rel}: review wording changed ({review["name"]})')
safe=(ROOT/'safeguarding.html').read_text(encoding='utf-8')
if 'Guidance &amp; external reporting' in safe:
    errs.append('External guidance panel still visible')

if errs:
    print('\n'.join('ERROR '+e for e in errs))
    sys.exit(1)
print('PASS: no broken local links, missing canonical/description/title/H1 or schema.')
