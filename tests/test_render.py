"""Hosted-app checks; install requirements.txt to run these tests."""
import importlib.util
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
HAS_FLASK = importlib.util.find_spec('flask') is not None
if HAS_FLASK:
    from app import create_app
    from server import REPLAY


@unittest.skipUnless(HAS_FLASK, 'Install requirements.txt to test Render hosting')
class RenderTests(unittest.TestCase):
    def setUp(self):
        self.config = dict(TESTING=True, SECRET_KEY='test-only-secret', TRUSTED_HOSTS=['localhost', 'ipl-example.onrender.com'])
        self.app = create_app(self.config)
        self.client = self.app.test_client()

    def token(self, client=None):
        result = (client or self.client).get('/predict.html')
        return re.search(r'name="csrf" value="([^"]+)', result.get_data(as_text=True)).group(1)

    def test_public_host_health_assets_and_script_free_pages(self):
        for path in ('/', '/predict.html', '/calculate.html', '/model.html', '/healthz', '/app.css', '/static/favicon.ico'):
            result = self.client.get(path, base_url='https://ipl-example.onrender.com')
            self.assertEqual(result.status_code, 200, path)
            self.assertIn("script-src 'none'", result.headers['Content-Security-Policy'])
            result.close()
        self.assertEqual(self.client.get('/', base_url='https://unknown.example').status_code, 400)

    def test_picks_survive_worker_restart_and_browsers_are_independent(self):
        token = self.token()
        m = REPLAY['remaining'][0]
        result = self.client.post('/predict.html', data=dict(csrf=token, pick=m['id']+':'+m['teams'][0]))
        self.assertEqual(result.status_code, 303)
        self.assertEqual(result.location, '/predict.html#match-'+m['id'])
        cookie = self.client.get_cookie('ipl_session')
        restarted = create_app(self.config).test_client()
        restarted.set_cookie('ipl_session', cookie.value)
        self.assertIn(b'1 of 30 matches predicted', restarted.get('/predict.html').data)
        self.assertIn(b'0 of 30 matches predicted', self.app.test_client().get('/predict.html').data)
        # A GET refresh does not toggle the selected match off.
        self.assertIn(b'1 of 30 matches predicted', restarted.get('/predict.html').data)

    def test_change_clear_reset_and_computer_independence(self):
        token = self.token(); m = REPLAY['remaining'][0]
        for pick in (m['teams'][0], m['teams'][1], 'NR'):
            self.client.post('/predict.html', data=dict(csrf=token, pick=m['id']+':'+pick))
            self.assertIn(b'1 of 30 matches predicted', self.client.get('/predict.html').data)
        result = self.client.post('/calculate.html', data=dict(csrf=token, team='RCB', count=1000))
        self.assertEqual(result.status_code, 200)
        self.assertIn(b'1,000 simulated seasons', result.data)
        self.assertIn(b'1 of 30 matches predicted', self.client.get('/predict.html').data)
        self.client.post('/predict.html', data=dict(csrf=token, pick=m['id']+':NR'))
        self.assertIn(b'0 of 30 matches predicted', self.client.get('/predict.html').data)
        self.client.post('/predict.html', data=dict(csrf=token, pick=m['id']+':NR'))
        self.client.post('/predict.html', data=dict(csrf=token, action='reset'))
        self.assertIn(b'0 of 30 matches predicted', self.client.get('/predict.html').data)

    def test_invalid_forms_and_private_files(self):
        token = self.token()
        self.assertEqual(self.client.post('/predict.html', data=dict(csrf='bad')).status_code, 403)
        self.assertEqual(self.client.post('/predict.html', data=dict(csrf=token, pick='unknown:RCB')).status_code, 400)
        self.assertEqual(self.client.post('/calculate.html', data=dict(csrf=token, count=999999)).status_code, 400)
        for path in ('/data/replay.json', '/server.py', '/static/../server.py'):
            self.assertEqual(self.client.get(path).status_code, 404)

    def test_session_cookie_cannot_be_forged(self):
        self.token()
        self.client.set_cookie('ipl_session', 'forged-data')
        self.assertIn(b'0 of 30 matches predicted', self.client.get('/predict.html').data)

    def test_render_requires_secret_and_uses_secure_cookie(self):
        with patch.dict('os.environ', {'RENDER':'true', 'SECRET_KEY':''}):
            with self.assertRaises(RuntimeError):
                create_app()
        with patch.dict('os.environ', {'RENDER':'true', 'SECRET_KEY':'production-test-secret', 'RENDER_EXTERNAL_HOSTNAME':'ipl-example.onrender.com'}):
            client = create_app().test_client()
            result = client.get('/predict.html', base_url='https://ipl-example.onrender.com')
            self.assertEqual(result.status_code, 200)
            cookie = result.headers['Set-Cookie']
            self.assertIn('Secure;', cookie); self.assertIn('HttpOnly;', cookie)


if __name__ == '__main__':
    unittest.main()
