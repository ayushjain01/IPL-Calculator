"""Small, dependency-free cricket model and points-table calculations."""
import math
import random

ALIASES = {
    'Royal Challengers Bangalore':'RCB', 'Royal Challengers Bengaluru':'RCB',
    'Chennai Super Kings':'CSK', 'Delhi Daredevils':'DC', 'Delhi Capitals':'DC',
    'Kings XI Punjab':'PBKS', 'Punjab Kings':'PBKS', 'Kolkata Knight Riders':'KKR',
    'Mumbai Indians':'MI', 'Rajasthan Royals':'RR', 'Sunrisers Hyderabad':'SRH',
    'Gujarat Titans':'GT', 'Lucknow Super Giants':'LSG', 'Deccan Chargers':'DCH',
    'Gujarat Lions':'GL', 'Kochi Tuskers Kerala':'KTK', 'Pune Warriors':'PWI',
    'Rising Pune Supergiant':'RPS', 'Rising Pune Supergiants':'RPS',
}

def balls(overs):
    parts = str(overs).split('.')
    if len(parts)>2 or not parts[0].isdigit() or (len(parts)==2 and (len(parts[1])!=1 or parts[1] not in '012345')):
        raise ValueError('Overs must use cricket notation, e.g. 19.5')
    return int(parts[0])*6+(int(parts[1]) if len(parts)==2 else 0)

def innings_summary(innings, quota):
    deliveries=[d for over in innings.get('overs',[]) for d in over['deliveries']]
    penalties=innings.get('penalty_runs',{})
    runs=sum(d['runs']['total'] for d in deliveries)+sum(penalties.values())
    legal=sum(not (d.get('extras',{}).get('wides') or d.get('extras',{}).get('noballs')) for d in deliveries)
    wickets=sum(w['kind']!='retired hurt' for d in deliveries for w in d.get('wickets',[]))
    return {'team':ALIASES[innings['team']], 'runs':runs, 'legal_balls':legal,
            'nrr_balls':quota if wickets>=10 else legal, 'wickets':wickets, 'quota':quota}

def normalize(document, match_id):
    info=document['info']; outcome=info['outcome']; raw=document.get('innings',[])[:2]
    quota=balls(info['overs'])
    innings=[innings_summary(x, balls(x.get('target',{}).get('overs',info['overs']))) for x in raw]
    winner=outcome.get('winner') or outcome.get('eliminator') or outcome.get('bowl_out')
    result=ALIASES[winner] if winner else 'NR' if outcome.get('result')=='no result' else 'TIE'
    nrr_valid=True
    if result=='NR':
        nrr=[]
    elif outcome.get('method'):
        # A completed revised-target chase: team 1 receives target minus one
        # over the full revised allocation. An early DLS termination needs a
        # verified par-score override and is deliberately not guessed here.
        target=raw[1].get('target',{}) if len(raw)>1 else {}
        finished=len(innings)==2 and (innings[1]['legal_balls']>=innings[1]['quota'] or innings[1]['wickets']>=10 or outcome.get('by',{}).get('wickets'))
        if outcome['method']=='D/L' and target.get('runs') and finished:
            nrr=[dict(innings[0],runs=target['runs']-1,nrr_balls=balls(target['overs'])),innings[1]]
        else:
            nrr=[]; nrr_valid=False
    else:
        nrr=innings
        nrr_valid=len(nrr)==2 and all(x['nrr_balls']>0 for x in nrr)
    return {'id':match_id, 'date':info['dates'][0], 'season':str(info['season']),
            'teams':[ALIASES[t] for t in info['teams']], 'venue':info['venue'],
            'number':info.get('event',{}).get('match_number'),
            'stage':info.get('event',{}).get('stage','league'),
            'result':result, 'method':outcome.get('method'), 'innings':innings,
            'nrr':nrr,'nrr_valid':nrr_valid, 'standard':quota==120 and not outcome.get('method') and len(innings)==2 and all(x['quota']==120 for x in innings) and result not in ('NR','TIE') and outcome.get('result')!='tie'}

def empty_table(teams):
    return {t:dict(team=t,p=0,w=0,l=0,nr=0,tie=0,pts=0,rf=0,bf=0,ra=0,ba=0) for t in teams}

def apply_result(table, teams, result, innings):
    a,b=(table[t] for t in teams)
    a['p']+=1; b['p']+=1
    if result in ('NR','TIE'):
        key='nr' if result=='NR' else 'tie'
        a[key]+=1; b[key]+=1; a['pts']+=1; b['pts']+=1
    else:
        winner=table[result]; loser=table[teams[1] if result==teams[0] else teams[0]]
        winner['w']+=1; winner['pts']+=2; loser['l']+=1
    if result!='NR':
        if len(innings)!=2: raise ValueError('Verified NRR innings required')
        for x,y in (innings,innings[::-1]):
            row=table[x['team']]
            row['rf']+=x['runs']; row['bf']+=x['nrr_balls']; row['ra']+=y['runs']; row['ba']+=y['nrr_balls']

def ranked(table):
    rows=[dict(r,nrr=6*r['rf']/r['bf']-6*r['ra']/r['ba'] if r['bf'] and r['ba'] else 0) for r in table.values()]
    return sorted(rows,key=lambda r:(-r['pts'],-r['w'],-r['nrr'],r['team']))

class Elo:
    def __init__(self,k=24,carry=.75,scale=400):
        self.k=k; self.carry=carry; self.scale=scale; self.ratings={}; self.season=None
    def start(self,season):
        if self.season!=season:
            self.ratings={t:1500+(r-1500)*self.carry for t,r in self.ratings.items()}
            self.season=season
    def probability(self,a,b):
        return 1/(1+10**((self.ratings.get(b,1500)-self.ratings.get(a,1500))/self.scale))
    def update(self,match):
        self.start(match['season']);a,b=match['teams']; p=self.probability(a,b)
        if match['result'] not in ('NR','TIE'):
            delta=self.k*((match['result']==a)-p)
            self.ratings[a]=self.ratings.get(a,1500)+delta
            self.ratings[b]=self.ratings.get(b,1500)-delta
        return p

def evaluate(matches,params,seasons):
    model=Elo(**params); errors=[]; correct=0; logloss=0
    for m in matches:
        model.start(m['season']); p=model.probability(*m['teams'])
        if m['season'] in seasons and m['result'] not in ('NR','TIE'):
            y=int(m['result']==m['teams'][0]); errors.append((p-y)**2)
            correct+=int((p>=.5)==bool(y)); logloss-=math.log(p if y else 1-p)
        model.update(m)
    n=len(errors)
    return dict(matches=n,brier=sum(errors)/n,log_loss=logloss/n,accuracy=correct/n)

def train(matches):
    # Development and evaluation are chronological, with online rating updates.
    # Holdout seasons never choose hyperparameters; replay future is excluded.
    candidates=[dict(k=k,carry=c,scale=400) for k in (12,24,36) for c in (.5,.75,1)]
    best=min(candidates,key=lambda p:evaluate(matches,p,{'2022','2023'})['brier'])
    validation=evaluate(matches,best,{'2024','2025'})
    model=Elo(**best)
    for m in matches: model.update(m)
    return model,dict(parameters=best,development_seasons=['2022','2023'],evaluation_seasons=['2024','2025'],evaluation=validation,coin_flip_brier=.25,coin_flip_log_loss=math.log(2),protocol='Walk-forward: predict before every match, then update using its result. Hyperparameters selected on 2022–2023 only.')

def score_pools(history,venue):
    samples=[m for m in history if m['standard'] and m['nrr_valid'] and m['date']>='2018-01-01']
    if not samples: raise ValueError('No historical scoring samples')
    # Venue and recent scoring conditions receive more weight. Never use
    # withheld outcomes or scores from the replay's future.
    weights=[(3 if m['venue'].split(',')[0]==venue.split(',')[0] else 1)*(1 if m['date']<'2023-01-01' else 3) for m in samples]
    return samples,weights

def sample_score(pool,weights,teams,winner,rng):
    template=rng.choices(pool,weights=weights,k=1)[0]
    loser=next(t for t in teams if t!=winner)
    mapping={template['result']:winner,next(t for t in template['teams'] if t!=template['result']):loser}
    return [dict(x,team=mapping[x['team']]) for x in template['nrr']]

def baseline(replay):
    table=empty_table(replay['teams'])
    for m in replay['completed']:
        if not m['nrr_valid']: raise ValueError('Unsupported NRR match in replay')
        apply_result(table,m['teams'],m['result'],m['nrr'])
    return table

def manual_table(replay,picks):
    table=baseline(replay)
    for m in replay['remaining']:
        result=picks.get(m['id'])
        if not result: continue
        if result not in m['teams']+['NR']: raise ValueError('Invalid pick')
        pool,weights=score_pools(replay['history'],m['venue'])
        # Stable empirical draw: unchanged picks always give identical NRR.
        score=[] if result=='NR' else sample_score(pool,weights,m['teams'],result,random.Random(m['id']+result))
        apply_result(table,m['teams'],result,score)
    return ranked(table)

def simulate(replay,count=2000,seed=26):
    if count not in (1000,2000,5000): raise ValueError('Unsupported simulation count')
    base=baseline(replay); rng=random.Random(seed)
    ratings=replay['model']['ratings']; params=replay['model']['report']['parameters']
    elo=Elo(**params); elo.ratings=ratings
    fixtures=[]
    for m in replay['remaining']:
        pool,weights=score_pools(replay['history'],m['venue'])
        # Precompute cumulative weights once per fixture for fast sampling.
        cumulative=[]; total=0
        for weight in weights:total+=weight;cumulative.append(total)
        fixtures.append((m,elo.probability(*m['teams']),pool,cumulative))
    hits={t:0 for t in replay['teams']}; nrrs={t:[] for t in replay['teams']}
    for _ in range(count):
        table={t:dict(row) for t,row in base.items()}
        for m,p,pool,cum in fixtures:
            winner=m['teams'][0] if rng.random()<p else m['teams'][1]
            template=rng.choices(pool,cum_weights=cum,k=1)[0]
            loser=next(t for t in m['teams'] if t!=winner)
            mapping={template['result']:winner,next(t for t in template['teams'] if t!=template['result']):loser}
            innings=[dict(x,team=mapping[x['team']]) for x in template['nrr']]
            apply_result(table,m['teams'],winner,innings)
        rows=ranked(table)
        for row in rows[:4]:hits[row['team']]+=1
        for row in rows:nrrs[row['team']].append(row['nrr'])
    results=[]
    for t in replay['teams']:
        values=sorted(nrrs[t]);p=hits[t]/count
        results.append(dict(team=t,chance=100*p,error=196*math.sqrt(p*(1-p)/count),nrr_low=values[int(count*.1)],nrr_high=values[int(count*.9)]))
    return sorted(results,key=lambda x:(-x['chance'],x['team']))
