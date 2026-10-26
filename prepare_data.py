"""Download public Cricsheet data and build the offline replay/model files."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,urllib.request,zipfile
from model import normalize,train,baseline,ranked

ROOT=Path(__file__).resolve().parent
URL='https://cricsheet.org/downloads/ipl_male_json.zip'

def prepare(archive=None):
    folder=ROOT/'data';folder.mkdir(exist_ok=True)
    archive=Path(archive) if archive else folder/'raw/ipl_male_json.zip'
    if not archive.exists():
        archive.parent.mkdir(parents=True,exist_ok=True)
        print('Downloading public IPL data from Cricsheet…',flush=True)
        with urllib.request.urlopen(URL,timeout=120) as response: archive.write_bytes(response.read())
    matches=[]
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.endswith('.json'):
                matches.append(normalize(json.loads(z.read(name)),Path(name).stem))
    matches.sort(key=lambda m:(m['date'],m['number'] or 1000,int(m['id'])))
    # Explicitly replay 2026 after league match 40: no future scores or results
    # appear in remaining fixtures, training history, or empirical score pools.
    season='2026';league=[m for m in matches if m['season']==season and m['stage']=='league']
    if len(league)!=70 or {m['number'] for m in league}!=set(range(1,71)):
        raise ValueError('Replay requires all 70 numbered 2026 league fixtures')
    completed=[m for m in league if m['number']<=40]
    last_date=max(m['date'] for m in completed)
    cutoff_ids={m['id'] for m in completed}
    history=[m for m in matches if m['date']<min(x['date'] for x in league) or m['id'] in cutoff_ids]
    model,report=train(history)
    replay=dict(season=season,cutoff=40,cutoff_date=last_date,teams=sorted({t for m in league for t in m['teams']}),
        completed=completed,remaining=[{k:m[k] for k in ('id','date','teams','venue','number')} for m in league if m['number']>40],
        history=history,model=dict(ratings=model.ratings,report=report),source=dict(url=URL,provider='Cricsheet',license='ODC-BY 1.0',sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),downloaded_at=datetime.now(timezone.utc).isoformat(),matches=len(matches),history_matches=len(history),last_training_date=last_date))
    table=baseline(replay)
    assert sum(r['p'] for r in table.values())==80
    assert all(m['date']<=last_date for m in history)
    assert not any('result' in m or 'innings' in m for m in replay['remaining'])
    # Store only parsed match summaries. Raw delivery files stay in the archive.
    (folder/'replay.json').write_text(json.dumps(replay,separators=(',',':')),encoding='utf-8')
    (folder/'model-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    (folder/'SOURCE.md').write_text(f'''# Historical data
Provider: [Cricsheet](https://cricsheet.org/). Download: {URL}
License: Open Data Commons Attribution License (ODC-BY 1.0), https://cricsheet.org/licensing/
Archive SHA-256: {replay['source']['sha256']}
Downloaded at: {replay['source']['downloaded_at']}
Parsed matches: {len(matches)}. Model training history: {len(history)}.
Replay: 2026, after league match 40 ({last_date}). Future results excluded.
Normalized aliases combine Bangalore/Bengaluru, Delhi and Punjab renames;
Deccan Chargers and SRH remain distinct franchises.
Raw files are retained locally in data/raw; replay.json contains derived summaries.
''',encoding='utf-8')
    print(json.dumps(dict(source=replay['source'],report=report,standings=ranked(table)),indent=2))

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--archive');args=parser.parse_args()
    prepare(args.archive)
