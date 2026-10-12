"""Check local HTML references and package the static site plus recruiter documents."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
from zipfile import ZipFile, ZIP_DEFLATED

root = Path(__file__).resolve().parents[1]
public = root / 'public'

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        self.links.extend(v for k, v in attrs if k in ('src', 'href') and v)

checked = 0
for page in public.rglob('*.html'):
    parser = Links()
    parser.feed(page.read_text(encoding='utf-8'))
    for href in parser.links:
        url = urlsplit(href)
        if url.scheme or url.netloc or not url.path:
            continue
        target = (public / unquote(url.path).lstrip('/')) if url.path.startswith('/') else (page.parent / unquote(url.path))
        if target.is_dir():
            target /= 'index.html'
        assert target.is_file(), f'Broken reference: {page.name} -> {href}'
        checked += 1

output = root / 'artifacts'
output.mkdir(exist_ok=True)
for folder, filename in [(public, 'plusminus-static-site.zip'), (root / 'docs/recruiter', 'plusminus-recruiter-kit.zip')]:
    with ZipFile(output / filename, 'w', ZIP_DEFLATED) as archive:
        for path in sorted(folder.rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(folder))
    print(f'{filename}: {(output / filename).stat().st_size:,} bytes')
print(f'Validated {checked} local HTML asset/link references.')
