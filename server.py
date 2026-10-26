from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from http.cookies import SimpleCookie,CookieError
from pathlib import Path
from urllib.parse import urlsplit,parse_qs
from html import escape
from string import Template
import argparse,json,mimetypes,secrets,time,threading
from model import baseline,ranked,manual_table,simulate,Elo,score_pools,sample_score
import random
from seo import metadata, home_html, robots_txt, sitemap_xml

ROOT=Path(__file__).resolve().parent
REPLAY=json.loads((ROOT/'data/replay.json').read_text(encoding='utf-8'))
SESSIONS={}; LOCK=threading.Lock(); TTL=8*60*60

def safe(value):return escape(str(value),quote=True)

def team_logo(team):
    return f'<img class="team-logo" src="/static/teams/{safe(team)}.png" alt="">'

def table_html(rows,team):
    html='<div class="table-scroll"><table><caption>Top four teams qualify for the playoffs</caption><thead><tr>'+''.join(f'<th scope="col">{h}</th>' for h in ['POS','TEAM','P','W','L','NR','T','NRR','PTS'])+'</tr></thead><tbody>'
    for i,r in enumerate(rows,1):
        html+=f'<tr class="{"selected-team" if r["team"]==team else ""}"><td class="{"top-four" if i<=4 else ""}">{i}</td><th scope="row"><span class="team-cell">{team_logo(r["team"])}{r["team"]}</span></th>'+''.join(f'<td>{r[k]}</td>' for k in ('p','w','l','nr','tie'))+f'<td>{r["nrr"]:+.3f}</td><td><strong>{r["pts"]}</strong></td></tr>'
    return html+'</tbody></table></div><p class="small">A win earns 2 points. A no result or an unresolved tie earns 1 point each. Teams with equal points are separated by wins, then NRR. <details><summary>What do the table headings mean?</summary><p>P: played · W: wins · L: losses · NR: no results · T: unresolved ties · PTS: points. NRR (net run rate) compares how quickly a team scores with how quickly it concedes runs. A higher NRR is better. Exact ties use team name as a final fallback in this replay.</p></details></p>'

def banner():
    return f'<p class="notice"><strong>Try the {REPLAY["season"]} season from match {REPLAY["cutoff"]}.</strong> This tool starts with the real scores from 28 April 2026. Explore what could happen in the 30 matches left at that point. The season has already finished; this is a replay.</p>'

def team_select(team):
    return '<label>Your team <select name="team">'+''.join(f'<option {"selected" if t==team else ""}>{t}</option>' for t in REPLAY['teams'])+'</select></label>'

def token_field(session):return f'<input type="hidden" name="csrf" value="{session["csrf"]}">'

def render(title,content):
    path = {'Computer predictions':'/calculate.html', 'Manual predictions':'/predict.html', 'How it works':'/model.html'}[title]
    return Template((ROOT/'templates/base.html').read_text(encoding='utf-8')).substitute(title=safe(title),metadata=metadata(path),content=content).encode('utf-8')

def qualification_message(team, chance):
    if chance == 0:
        return f"Sorry, {team} did not qualify in any of these simulated endings.", "No top-four finishes showed up in this run. That does not prove qualification is impossible. Try manual picks to explore another path."
    if chance < 10:
        return f"{team} need a big turnaround.", "There is still a slim path to the top four in these simulations. A few results going their way could make a difference."
    if chance < 40:
        return f"Keep the faith, {team} fans.", "The odds are against them in this run, but a top-four finish is still possible."
    if chance <= 60:
        return f"It could go either way for {team}.", "The playoff race is wide open. Every remaining match could matter."
    if chance < 90:
        return f"Looking promising for {team}!", "They reached the top four in most of these simulated endings, but there is still work to do."
    if chance < 100:
        return f"{team} are looking strong!", "They qualified in almost every simulated ending. There is still a chance of missing out, so nothing is confirmed."
    return f"A clean sweep of qualifying outcomes for {team}!", "They reached the top four in every simulated ending in this run. That is encouraging, but it is not a mathematical guarantee."


def qualification_notice(team, chance):
    title, explanation = qualification_message(team, chance)
    text = f'<p><strong>{chance:.1f}% top-four chance in this run.</strong> {safe(explanation)}</p>'
    return f'<section class="qualification-summary" aria-label="Your team result">{team_logo(team)}<h2>{safe(title)}</h2>{text}</section><dialog open class="result-notice" aria-labelledby="result-notice-title"><h2 id="result-notice-title">{safe(title)}</h2>{text}<form method="dialog"><button class="button">See results</button></form></dialog>'


def computer(session,results=None,count=2000):
    team=session.get('team','RCB')
    content='<h1>Computer predictions</h1>'+banner()
    content+='<p>Choose your team and click Calculate chances. The computer uses past IPL results to try different endings to the season.</p>'
    content+='<p class="small"><strong>Still an experiment:</strong> in testing, the model did no better than giving each team an equal chance. Use it to explore possibilities, rather than as a reliable prediction. <a href="/model.html">How it works</a>.</p>'
    content+=f'<form method="post" action="/calculate.html" class="controls">{token_field(session)}{team_select(team)}<label>Possible season endings <select name="count">'+''.join(f'<option value="{n}" {"selected" if n==count else ""}>{n:,}</option>' for n in (1000,2000,5000))+'</select></label><button class="button">Calculate chances</button></form>'
    if results:
        selected = next(r for r in results if r["team"] == team)
        content += qualification_notice(team, selected["chance"])
        content+=f'<h2>Chances of finishing in the top four</h2><p class="small">{count:,} simulated seasons. A 70% result means the team reached the top four in about 70 out of every 100 endings the computer tried. More endings give a steadier estimate, not a guarantee. The NRR range covers the middle 80% of those endings; real results can fall outside it.</p><div class="table-scroll"><table><thead><tr><th>TEAM</th><th>TOP-FOUR CHANCE</th><th>POSSIBLE NRR</th></tr></thead><tbody>'
        for r in results:
            content+=f'<tr class="{"selected-team" if r["team"]==team else ""}"><th scope="row"><span class="team-cell">{team_logo(r["team"])}{r["team"]}</span></th><td>{r["chance"]:.1f}%</td><td>{r["nrr_low"]:+.3f} to {r["nrr_high"]:+.3f}</td></tr>'
        content+='</tbody></table></div><p>The computer assumes every match has a winner. To try a washout, use Manual predictions. Injuries, player selections, the toss and weather are not included.</p>'
    content+='<details><summary>See the win chances for each match</summary><div class="table-scroll"><table><thead><tr><th>MATCH</th><th>FIXTURE</th><th>WIN CHANCES</th></tr></thead><tbody>'
    elo=Elo(**REPLAY['model']['report']['parameters']);elo.ratings=REPLAY['model']['ratings']
    for m in REPLAY['remaining']:
        a,b=m['teams'];p=elo.probability(a,b)
        content+=f'<tr><td>{m["number"]}</td><td>{a} vs {b}</td><td>{a} {p:.1%} · {b} {1-p:.1%}</td></tr>'
    content+='</tbody></table></div></details><h2>Starting points table</h2>'+table_html(ranked(baseline(REPLAY)),team)
    content+='<p><a href="/model.html">How the predictions and NRR work</a></p>'
    return render('Computer predictions',content)

def score_text(innings):
    def overs(n):return f'{n//6}.{n%6}'
    return ' · '.join(f'{safe(x["team"])} {x["runs"]} off {overs(x["nrr_balls"])} overs' for x in innings)

def manual(session,message=''):
    picks=session['picks'];team=None
    content='<h1>Manual predictions</h1>'+banner()+'<p>Pick a winner or No result. The points table updates after every pick. Click a selected option again to clear it.</p>'
    if message:content+=f'<p role="status">{safe(message)}</p>'
    content+=f'<form method="post" action="/predict.html">{token_field(session)}<button class="button" name="action" value="reset">Reset all picks</button></form><p><strong>{len(picks)} of {len(REPLAY["remaining"])} matches predicted</strong></p><div class="workspace-grid"><section><h2>Remaining fixtures</h2>'
    for m in REPLAY['remaining']:
        a,b=m['teams'];pick=picks.get(m['id'],'')
        content+=f'<div class="fixture" id="match-{m["id"]}"><h3>{team_logo(a)} {a} vs {b} {team_logo(b)}</h3><p class="small">Match {m["number"]} · {m["date"]}<br>{safe(m["venue"])}</p><form method="post" action="/predict.html#match-{m["id"]}">{token_field(session)}<div class="pick-group" role="group" aria-label="Result for {a} versus {b}">'
        for value,label in [(a,a+' win'),(b,b+' win'),('NR','No result')]:
            content+=f'<button type="submit" class="pick {"active" if pick==value else ""}" data-winner="{value}" name="pick" value="{m["id"]}:{value}" aria-pressed="{str(pick==value).lower()}">{label}</button>'
        content+='</div></form>'
        if pick and pick!='NR':
            pool,weights=score_pools(REPLAY['history'],m['venue'])
            innings=sample_score(pool,weights,m['teams'],pick,random.Random(m['id']+pick))
            content+=f'<p class="small">Example score for your pick: {score_text(innings)}. This is an estimate based on a past game. The overs shown are those used for NRR; an all-out team is counted as having used its full allowance.</p>'
        content+='</div>'
    content+='</section><section><h2>Projected standings</h2>'+table_html(manual_table(REPLAY,picks),team)
    if len(picks)==len(REPLAY['remaining']):
        content+='<p><strong>Your projected top four: '+', '.join(r['team'] for r in manual_table(REPLAY,picks)[:4])+'.</strong></p>'
    content+='<p class="small">NRR needs a score as well as a winner, so this tool uses an example from a past match for each pick. It stays the same when you refresh. Click a selected option again to undo a pick, or Reset all picks to start again. Picks last up to 8 hours and are cleared when the app restarts.</p><p><a href="/model.html">How the predictions and NRR work</a></p></section></div>'
    return render('Manual predictions',content)

def model_page():
    source=REPLAY['source'];report=REPLAY['model']['report'];metrics=report['evaluation']
    content='<h1>How it works</h1>'+banner()
    content+='<h2>What does this tool show?</h2><p>Which teams could finish in the top four? This tool takes the real points table after match 40, then tries different results for the games that were still to come.</p>'
    content+='<h2>How does the computer choose a winner?</h2><p>Each team has a strength rating based on its past results. Winning raises that rating; losing lowers it. This method is called Elo. A stronger team gets a higher chance of winning, but an upset is always possible.</p><p>The computer plays out the remaining fixtures many times. A team’s top-four percentage tells you how often it qualified in those possible endings. It does not mean the real season will follow that result.</p>'
    content+=f'<h2>How much data does it use?</h2><p>This tool uses {source["matches"]:,} IPL match records from <a href="https://cricsheet.org/downloads/">Cricsheet</a>. The ratings use {source["history_matches"]:,} records across 19 seasons, from April 2008 to 28 April 2026. Only the first 40 matches of 2026 are included, so the computer cannot see the answers to the remaining games.</p>'
    content+=f'<h2>How accurate is it?</h2><p><strong>It is still experimental.</strong> This tool was tested on {metrics["matches"]} decided matches from 2024 and 2025. It picked the winner correctly {metrics["accuracy"]:.1%} of the time. Its probability estimates did no better than giving each team a 50% chance. Treat the results as a way to explore possibilities, rather than a dependable forecast.</p><p>It does not account for injuries, playing elevens, the toss or weather. Using more possible endings makes the calculation steadier, but does not fix those limits.</p>'
    content+='<h2>What is NRR?</h2><p>Net run rate (NRR) compares how quickly a team scores with how quickly its opponents score against it. Higher is better. For example, scoring at 9 runs per over while conceding 8 gives an NRR of +1.000. The season figure uses totals across the matches that count, rather than averaging each match’s NRR.</p><p>For matches already played, this tool uses actual runs and balls. For your predicted matches, the scores are unknown. This tool borrows example scores and chase lengths from past IPL games to estimate the effect on NRR. These are possible scores, not predictions of exact totals.</p>'
    content+='<h2>What happens in manual mode?</h2><p>You choose the winner or No result, and the table updates after each pick. A win gives 2 points; No result gives each team 1 point without changing NRR. You can leave some matches unpicked, change a pick, or reset everything. Computer mode runs separately and does not use your manual picks.</p>'
    content+=f'<details><summary>Technical details and data sources</summary><p>Elo starts at 1500, uses an update rate of {report["parameters"]["k"]}, and moves ratings halfway back toward 1500 between seasons. Settings were selected using 2022–2023. Testing on 2024–2025 predicted each game before learning its result.</p><p>Brier score: {metrics["brier"]:.4f} versus 0.2500 for equal chances. Log loss: {metrics["log_loss"]:.4f} versus 0.6931. These measure the quality of probability estimates; lower is better.</p><p>Future scores come from ordinary 20-over games from 2018 onward, before the replay date. Recent matches and matching venues get more weight. Ratings stay fixed during each possible season ending. Seed 26 keeps identical runs repeatable. NRR ranges show the 10th to 90th percentiles, and have not been checked for forecast accuracy.</p><p>NRR uses legal balls; wides and no-balls add runs without adding legal balls. All-out innings use the full allowed overs. No-result matches and Super Over scores do not count toward NRR. A Super Over winner still gets the match points. Completed revised-target DLS chases use the revised target minus one for the first team; early-terminated rain-affected games need verified extra information and are flagged if unavailable. None occur in this starting table.</p><p><a href="/data/SOURCE.md">Data source and license</a> · <a href="/data/model-report.json">Full test results</a> · <a href="https://cricsheet.org/format/json/">Cricsheet data format</a> · <a href="https://documents.iplt20.com/bcci/documents/1742707993986_Match_Playing_Conditions.pdf">IPL playing conditions</a></p></details>'
    return render('How it works',content)

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,body,content_type='text/html; charset=utf-8',cookie=None):
        self.send_response(status)
        for key,value in [('Content-Type',content_type),('Content-Length',str(len(body))),('Content-Security-Policy',"default-src 'self'; script-src 'none'; style-src 'self'; font-src 'self'; img-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'"),('X-Content-Type-Options','nosniff'),('Cache-Control','no-store')]:self.send_header(key,value)
        if cookie:self.send_header('Set-Cookie',cookie)
        self.end_headers();self.wfile.write(body)
    def valid_host(self):
        return self.headers.get('Host','') in (f'127.0.0.1:{self.server.server_port}',f'localhost:{self.server.server_port}')
    def session(self):
        cookie=SimpleCookie()
        try:cookie.load(self.headers.get('Cookie',''))
        except CookieError:pass
        sid=cookie['ipl_session'].value if 'ipl_session' in cookie else ''
        now=time.monotonic()
        with LOCK:
            for key in list(SESSIONS):
                if SESSIONS[key]['expires']<now:del SESSIONS[key]
            if sid not in SESSIONS:
                if len(SESSIONS)>=1000:del SESSIONS[next(iter(SESSIONS))]
                sid=secrets.token_urlsafe(32);SESSIONS[sid]=dict(csrf=secrets.token_urlsafe(32),picks={},team='RCB',expires=now+TTL)
            result=SESSIONS[sid];result['expires']=now+TTL
        return result,f'ipl_session={sid}; HttpOnly; SameSite=Strict; Path=/'
    def do_GET(self):
        if not self.valid_host():return self.reply(403,b'Local access only','text/plain')
        path=urlsplit(self.path).path
        if path in ('/','/index.html'):
            return self.reply(200,home_html((ROOT/'index.html').read_text(encoding='utf-8')).encode('utf-8'))
        if path in ('/calculate.html','/predict.html'):
            session,cookie=self.session()
            return self.reply(200,computer(session) if path=='/calculate.html' else manual(session),cookie=cookie)
        if path=='/robots.txt':return self.reply(200,robots_txt().encode('utf-8'),'text/plain; charset=utf-8')
        if path=='/sitemap.xml':return self.reply(200,sitemap_xml().encode('utf-8'),'application/xml; charset=utf-8')
        if path=='/model.html':return self.reply(200,model_page())
        allowed={'/app.css':ROOT/'app.css','/data/model-report.json':ROOT/'data/model-report.json','/data/SOURCE.md':ROOT/'data/SOURCE.md'}
        if path.startswith('/static/'):
            candidate=(ROOT/path.lstrip('/')).resolve()
            if candidate.is_relative_to((ROOT/'static').resolve()):allowed[path]=candidate
        target=allowed.get(path)
        if not target or not target.is_file():return self.reply(404,b'Not found','text/plain')
        self.reply(200,target.read_bytes(),mimetypes.guess_type(target.name)[0] or 'application/octet-stream')
    def do_POST(self):
        if not self.valid_host():return self.reply(403,b'Local access only','text/plain')
        path=urlsplit(self.path).path
        if path not in ('/calculate.html','/predict.html'):return self.reply(404,b'Not found','text/plain')
        if self.headers.get('Content-Type','').split(';')[0]!='application/x-www-form-urlencoded':return self.reply(415,b'HTML forms only','text/plain')
        try:
            length=int(self.headers.get('Content-Length','0'))
            if not 0<length<=32000:raise ValueError('Invalid form size')
            values=parse_qs(self.rfile.read(length).decode('utf-8'),keep_blank_values=True,max_num_fields=100)
            get=lambda name,default='':values.get(name,[default])[0]
            session,cookie=self.session()
            if not secrets.compare_digest(get('csrf'),session['csrf']):return self.reply(403,b'Form expired. Reload the page and try again.','text/plain',cookie)
            if path=='/calculate.html':
                team=get('team','RCB')
                if team not in REPLAY['teams']:raise ValueError('Unknown team')
                session['team']=team
                count=int(get('count','2000'))
                body=computer(session,simulate(REPLAY,count),count)
            else:
                if get('action')=='reset':session['picks']={}
                else:
                    match_id,separator,pick=get('pick').partition(':')
                    match=next((m for m in REPLAY['remaining'] if m['id']==match_id),None)
                    if not separator or not match or pick not in match['teams']+['NR']:raise ValueError('Invalid match pick')
                    picks=dict(session['picks'])
                    if picks.get(match_id)==pick:picks.pop(match_id)
                    else:picks[match_id]=pick
                    session['picks']=picks
                body=manual(session,'Points table updated.' if get('action')!='reset' else 'All picks reset.')
            self.reply(200,body,cookie=cookie)
        except (ValueError,UnicodeError):self.reply(400,b'Invalid form. Return to the page and try again.','text/plain')

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8000);parser.add_argument('--open-browser',action='store_true');args=parser.parse_args()
    server=ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
    print(f'IPL Calculator ready: http://127.0.0.1:{args.port}\nPress Ctrl+C to stop.',flush=True)
    if args.open_browser:
        import webbrowser
        threading.Timer(.5,lambda:webbrowser.open(f'http://127.0.0.1:{args.port}')).start()
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()

if __name__=='__main__':main()
