from html import escape
import os
import re
from urllib.parse import urlsplit

DEFAULT_URL = 'https://ipl-calculator-l4co.onrender.com'
PAGES = {
    '/': ('IPL Playoffs Calculator – Will My Team Qualify?', 'Explore IPL playoff chances with computer predictions or your own match picks. Try a historical IPL replay and see how results change points and net run rate.'),
    '/calculate.html': ('IPL Qualification Chances – Computer Predictions | IPL Calculator', 'Calculate each team’s IPL top-four chances using historical match data. Explore possible season endings and estimated net run rate in a 2026 replay.'),
    '/predict.html': ('IPL Points Table Predictor – Pick Match Winners | IPL Calculator', 'Pick IPL match winners or no results and see the projected points table change after each choice. Explore playoff scenarios with a historical 2026 replay.'),
    '/model.html': ('How IPL Predictions and Net Run Rate Work | IPL Calculator', 'Understand the IPL calculator’s historical data, team ratings, net run rate calculations and model accuracy. Learn what its qualification percentages mean.'),
}


def public_url():
    value = os.environ.get('PUBLIC_URL', DEFAULT_URL).strip().rstrip('/')
    parts = urlsplit(value)
    if parts.scheme not in ('https', 'http') or not parts.netloc or parts.username or parts.password or parts.query or parts.fragment or parts.path:
        raise ValueError('PUBLIC_URL must be the public origin, e.g. https://ipl.example.com')
    return value


def metadata(path):
    path = '/' if path == '/index.html' else path
    title, description = PAGES[path]
    origin = public_url()
    canonical = origin + path
    image = origin + '/static/Cover.png'
    def meta(name, value, attribute='name'):
        return f'<meta {attribute}="{name}" content="{escape(value, quote=True)}">'
    tags = [f'<title>{escape(title)}</title>', meta('description', description),
            meta('author', 'Ayush Jain'), meta('theme-color', '#001030'),
            meta('robots', 'index, follow, max-image-preview:large'),
            f'<link rel="canonical" href="{escape(canonical, quote=True)}">']
    for key, value in {'og:type':'website', 'og:site_name':'IPL Calculator', 'og:title':title,
                       'og:description':description, 'og:url':canonical, 'og:image':image,
                       'og:image:secure_url':image, 'og:image:type':'image/png',
                       'og:image:width':'1200', 'og:image:height':'630',
                       'og:image:alt':'IPL Calculator – Will my team qualify? Blue calculator logo on a navy background.'}.items():
        tags.append(meta(key, value, 'property'))
    for key, value in {'twitter:card':'summary_large_image', 'twitter:title':title,
                       'twitter:description':description, 'twitter:image':image,
                       'twitter:image:alt':'IPL Calculator – Will my team qualify?'}.items():
        tags.append(meta(key, value))
    if os.environ.get('GOOGLE_SITE_VERIFICATION'):
        tags.append(meta('google-site-verification', os.environ['GOOGLE_SITE_VERIFICATION']))
    return '\n'.join(tags)


def home_html(source):
    head = '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + metadata('/') + '<link rel="icon" type="image/x-icon" href="/static/favicon.ico"><link rel="stylesheet" href="/app.css"></head>'
    source = re.sub(r'<link itemprop="url" href="[^"]*">', lambda _: '<link itemprop="url" href="'+escape(public_url()+'/', quote=True)+'">', source)
    return re.sub(r'<head>.*?</head>', lambda _: head, source, count=1, flags=re.S)


def robots_txt():
    return 'User-agent: *\nAllow: /\nDisallow: /data/\nDisallow: /healthz\n\nSitemap: ' + public_url() + '/sitemap.xml\n'


def sitemap_xml():
    entries = ''.join(f'<url><loc>{escape(public_url()+path)}</loc></url>' for path in PAGES)
    return '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + entries + '</urlset>\n'
