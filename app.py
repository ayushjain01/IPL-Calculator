from datetime import timedelta
import os
import secrets

from flask import Flask, Response, redirect, request, send_file, send_from_directory, session
from server import ROOT, REPLAY, computer, manual, model_page
from seo import home_html, robots_txt, sitemap_xml, public_url
from model import simulate


def create_app(config=None):
    app = Flask(__name__, static_folder=None)
    hosted = os.environ.get('RENDER', '').lower() == 'true'
    secret = os.environ.get('SECRET_KEY')
    if hosted and not secret and not (config and config.get('TESTING')):
        raise RuntimeError('Set SECRET_KEY in Render Environment settings before starting the app.')
    from urllib.parse import urlsplit
    hosts = ['localhost', '127.0.0.1', urlsplit(public_url()).hostname]
    for name in ('RENDER_EXTERNAL_HOSTNAME', 'RENDER_INTERNAL_HOSTNAME'):
        if os.environ.get(name):
            hosts.append(os.environ[name])
    hosts.extend(h.strip() for h in os.environ.get('ALLOWED_HOSTS', '').split(',') if h.strip())
    app.config.update(
        SECRET_KEY=secret or secrets.token_hex(32),
        TRUSTED_HOSTS=hosts,
        SESSION_COOKIE_NAME='ipl_session',
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=hosted,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=32000,
        MAX_FORM_MEMORY_SIZE=32000,
        MAX_FORM_PARTS=100,
    )
    if config:
        app.config.update(config)
    dataset = f"{REPLAY['season']}-{REPLAY['cutoff']}-{REPLAY['source']['sha256'][:12]}"

    def state():
        # Signed cookies carry the small set of picks between workers/restarts.
        if session.get('dataset') != dataset:
            session.clear()
            session.update(dataset=dataset, picks={}, team='RCB', csrf=secrets.token_urlsafe(32))
        session.permanent = True
        return session

    def check_form():
        if request.mimetype != 'application/x-www-form-urlencoded':
            return Response('Please use the form on the page.', status=415)
        if not secrets.compare_digest(request.form.get('csrf', ''), state()['csrf']):
            return Response('This form has expired. Reload the page and try again.', status=403)

    @app.after_request
    def headers(response):
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'none'; style-src 'self'; font-src 'self'; img-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Cache-Control'] = 'no-store'
        if request.method == 'POST' or response.status_code >= 400 or request.path.startswith('/data/') or request.path == '/healthz' or (request.path == '/predict.html' and session.get('picks')):
            response.headers['X-Robots-Tag'] = 'noindex, follow'
        return response

    @app.get('/')
    def home():
        return Response(home_html((ROOT / 'index.html').read_text(encoding='utf-8')), content_type='text/html; charset=utf-8')

    @app.get('/index.html')
    def home_alias():
        return redirect('/', code=301)

    @app.get('/robots.txt')
    def robots():
        return Response(robots_txt(), content_type='text/plain; charset=utf-8')

    @app.get('/sitemap.xml')
    def sitemap():
        return Response(sitemap_xml(), content_type='application/xml; charset=utf-8')

    @app.route('/calculate.html', methods=['GET', 'POST'])
    def calculate():
        data = state()
        if request.method == 'GET':
            return Response(computer(data), content_type='text/html; charset=utf-8')
        error = check_form()
        if error is not None:
            return error
        try:
            team = request.form.get('team', 'RCB')
            if team not in REPLAY['teams']:
                raise ValueError('Unknown team')
            count = int(request.form.get('count', '2000'))
            results = simulate(REPLAY, count)
            data['team'] = team
            return Response(computer(data, results, count), content_type='text/html; charset=utf-8')
        except ValueError:
            return Response('Choose a valid team and number of season endings.', status=400)

    @app.route('/predict.html', methods=['GET', 'POST'])
    def predict():
        data = state()
        if request.method == 'GET':
            body = manual(data, data.pop('message', ''))
            body = body.replace(b' and are cleared when the app restarts', b'')
            return Response(body, content_type='text/html; charset=utf-8')
        error = check_form()
        if error is not None:
            return error
        anchor = ''
        if request.form.get('action') == 'reset':
            data['picks'] = {}
            data['message'] = 'All picks reset.'
        else:
            match_id, sep, pick = request.form.get('pick', '').partition(':')
            match = next((m for m in REPLAY['remaining'] if m['id'] == match_id), None)
            if not sep or not match or pick not in match['teams'] + ['NR']:
                return Response('Choose a valid match result.', status=400)
            picks = dict(data['picks'])
            if picks.get(match_id) == pick:
                picks.pop(match_id)
            else:
                picks[match_id] = pick
            data['picks'] = picks
            data['message'] = 'Points table updated.'
            anchor = '#match-' + match_id
        # Reloading the resulting page must not submit/toggle the pick again.
        return redirect('/predict.html' + anchor, code=303)

    @app.get('/model.html')
    def explanation():
        return Response(model_page(), content_type='text/html; charset=utf-8')

    @app.get('/app.css')
    def stylesheet():
        return send_file(ROOT / 'app.css')

    @app.get('/static/<path:filename>')
    def assets(filename):
        return send_from_directory(ROOT / 'static', filename)

    @app.get('/data/<name>')
    def public_data(name):
        if name not in ('SOURCE.md', 'model-report.json'):
            return Response('Not found', status=404)
        return send_file(ROOT / 'data' / name)

    @app.get('/healthz')
    def health():
        return {'status': 'ok'}

    return app


app = create_app()
