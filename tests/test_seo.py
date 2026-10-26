import importlib.util
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from seo import PAGES, metadata, robots_txt, sitemap_xml, home_html, public_url
from server import computer, manual, model_page, ROOT


class MetadataTests(unittest.TestCase):
    def test_distinct_titles_descriptions_and_absolute_social_urls(self):
        titles = set()
        for path in PAGES:
            head = metadata(path)
            titles.add(re.search(r'<title>(.*?)</title>', head).group(1))
            self.assertIn(f'href="{public_url()+path}"', head)
            self.assertIn('name="description"', head)
            self.assertIn('property="og:image"', head)
            self.assertIn(public_url()+'/static/Cover.png', head)
            self.assertIn('summary_large_image', head)
            self.assertNotIn('localhost', head)
        self.assertEqual(len(titles), 4)

    def test_pages_have_one_title_and_metadata(self):
        session = dict(team='RCB', picks={}, csrf='test')
        pages = [home_html((ROOT/'index.html').read_text(encoding='utf-8')), computer(session).decode(), manual(session).decode(), model_page().decode()]
        for html in pages:
            self.assertEqual(html.count('<title>'), 1)
            self.assertEqual(html.count('rel="canonical"'), 1)
            self.assertEqual(html.count('name="description"'), 1)
            self.assertNotIn('<script', html)

    def test_sitemap_contains_only_public_canonical_pages(self):
        root = ET.fromstring(sitemap_xml())
        urls = [x.text for x in root.findall('{*}url/{*}loc')]
        self.assertEqual(urls, [public_url()+p for p in PAGES])
        self.assertIn('Sitemap: '+public_url()+'/sitemap.xml', robots_txt())
        self.assertNotIn('Disallow: /\n', robots_txt())

    def test_url_and_search_console_configuration(self):
        with patch.dict('os.environ', {'PUBLIC_URL':'https://ipl.example.com/', 'GOOGLE_SITE_VERIFICATION':'verification-token'}):
            self.assertIn('https://ipl.example.com/calculate.html', metadata('/calculate.html'))
            self.assertIn('google-site-verification', metadata('/'))
            self.assertIn('verification-token', metadata('/'))
            self.assertIn('https://ipl.example.com/sitemap.xml', robots_txt())
        with patch.dict('os.environ', {'PUBLIC_URL':'https://example.com/?bad=1'}):
            self.assertRaises(ValueError, public_url)

    @unittest.skipUnless(importlib.util.find_spec('flask'), 'Install requirements.txt to test hosted SEO endpoints')
    def test_public_endpoints_and_indexing_headers(self):
        from app import create_app
        client = create_app(dict(TESTING=True, SECRET_KEY='test')).test_client()
        for path in ('/robots.txt', '/sitemap.xml', '/static/Cover.png'):
            response = client.get(path)
            self.assertEqual(response.status_code, 200)
            response.close()
        response = client.get('/index.html')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.location, '/')
        self.assertNotIn('noindex', client.get('/').headers.get('X-Robots-Tag',''))
        self.assertIn('noindex', client.get('/healthz').headers['X-Robots-Tag'])
        response = client.get('/calculate.html')
        token = re.search(r'name="csrf" value="([^"]+)', response.get_data(as_text=True)).group(1)
        result = client.post('/calculate.html', data=dict(csrf=token, team='RCB', count=1000))
        self.assertEqual(result.status_code, 200)
        self.assertIn('noindex', result.headers['X-Robots-Tag'])


if __name__ == '__main__':
    unittest.main()
