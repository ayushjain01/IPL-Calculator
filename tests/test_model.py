import copy,json,math,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import balls,normalize,innings_summary,empty_table,apply_result,ranked,Elo,baseline,manual_table,simulate

ROOT=Path(__file__).resolve().parents[1]

class CricketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.replay=json.loads((ROOT/'data/replay.json').read_text())
    def test_cricket_overs(self):
        self.assertEqual(balls('19.5'),119)
        for invalid in ('19.6','1.12','-2','1.5.3'):self.assertRaises(ValueError,balls,invalid)
    def test_legal_balls_extras_penalties(self):
        innings={'team':'Mumbai Indians','penalty_runs':{'pre':5,'post':2},'overs':[{'deliveries':[{'runs':{'total':2},'extras':{'wides':2}},{'runs':{'total':5},'extras':{'noballs':1}},{'runs':{'total':4}}]}]}
        score=innings_summary(innings,120)
        self.assertEqual(score['runs'],18);self.assertEqual(score['legal_balls'],1)
    def test_all_out_uses_full_quota(self):
        innings={'team':'Mumbai Indians','overs':[{'deliveries':[{'runs':{'total':0},'wickets':[{'kind':'bowled'}]} for _ in range(10)]}]}
        score=innings_summary(innings,120)
        self.assertEqual(score['legal_balls'],10);self.assertEqual(score['nrr_balls'],120)
    def test_no_result_changes_only_points(self):
        table=empty_table(['A','B']);apply_result(table,['A','B'],'NR',[])
        self.assertEqual(table['A']['pts'],1);self.assertEqual(table['B']['pts'],1)
        self.assertEqual(table['A']['bf'],0);self.assertEqual(table['B']['nr'],1)
    def test_nrr_uses_totals_and_balls(self):
        table=empty_table(['A','B'])
        apply_result(table,['A','B'],'A',[dict(team='A',runs=180,nrr_balls=114),dict(team='B',runs=160,nrr_balls=120)])
        self.assertAlmostEqual(ranked(table)[0]['nrr'],180*6/114-8)
    def test_replay_is_real_balanced_schedule(self):
        r=self.replay
        self.assertEqual(len(r['completed']),40);self.assertEqual(len(r['remaining']),30)
        self.assertEqual(len({m['id'] for m in r['completed']+r['remaining']}),70)
        for t in r['teams']:self.assertEqual(sum(t in m['teams'] for m in r['completed']+r['remaining']),14)
    def test_no_future_leakage(self):
        r=self.replay;ids={m['id'] for m in r['remaining']}
        self.assertTrue(all(m['id'] not in ids and m['date']<=r['cutoff_date'] for m in r['history']))
        self.assertTrue(all(set(m)=={'id','date','teams','venue','number'} for m in r['remaining']))
    def test_real_starting_points_and_nrr_regression(self):
        table=baseline(self.replay)
        self.assertEqual(sum(r['p'] for r in table.values()),80)
        self.assertEqual(sum(r['pts'] for r in table.values()),80)
        self.assertEqual(table['PBKS']['pts'],13);self.assertEqual(table['RCB']['pts'],12)
        self.assertEqual(f"{next(x for x in ranked(table) if x['team']=='RCB')['nrr']:.3f}",'1.919')
    def test_super_over_is_excluded(self):
        m=next(m for m in self.replay['completed'] if m['number']==38)
        self.assertEqual(m['result'],'KKR');self.assertEqual(len(m['nrr']),2)
        self.assertEqual([x['runs'] for x in m['nrr']],[155,155])
    def test_manual_reset_and_recompute(self):
        m=self.replay['remaining'][0];saved=copy.deepcopy(self.replay)
        a=manual_table(self.replay,{m['id']:m['teams'][0]})
        b=manual_table(self.replay,{m['id']:m['teams'][0]})
        self.assertEqual(a,b);self.assertEqual(self.replay,saved)
        base=baseline(self.replay);picked=next(x for x in a if x['team']==m['teams'][0])
        self.assertEqual(picked['pts'],base[picked['team']]['pts']+2)
        nr=next(x for x in manual_table(self.replay,{m['id']:'NR'}) if x['team']==m['teams'][0])
        self.assertEqual(nr['bf'],base[nr['team']]['bf'])
        self.assertEqual(manual_table(self.replay,{}),ranked(base))
    def test_all_manual_results_complete_season(self):
        picks={m['id']:m['teams'][0] for m in self.replay['remaining']}
        for r in manual_table(self.replay,picks):self.assertEqual(r['p'],14)
    def test_elo_updates_in_right_direction_and_shrinks(self):
        elo=Elo(k=24,carry=.5);elo.start('2025')
        elo.update(dict(season='2025',teams=['A','B'],result='A'))
        self.assertAlmostEqual(elo.ratings['A'],1512)
        self.assertGreater(elo.probability('A','B'),.5)
        elo.start('2026');self.assertEqual(elo.ratings['A'],1506)
    def test_simulation_repeatable_and_four_qualifiers(self):
        a=simulate(self.replay,1000);b=simulate(self.replay,1000)
        self.assertEqual(a,b);self.assertAlmostEqual(sum(r['chance'] for r in a),400)
        self.assertTrue(all(0<=r['chance']<=100 and r['nrr_low']<=r['nrr_high'] for r in a))
        self.assertRaises(ValueError,simulate,self.replay,1000000)
    def test_dls_completed_revised_target_and_unsupported_termination(self):
        def inns(team,run):return {'team':team,'overs':[{'deliveries':[{'runs':{'total':run}} for _ in range(6)]}]}
        doc={'info':dict(overs=1,dates=['2026-01-01'],season='2026',teams=['Mumbai Indians','Delhi Capitals'],venue='Test',outcome={'winner':'Delhi Capitals','by':{'wickets':9},'method':'D/L'}),'innings':[inns('Mumbai Indians',2),inns('Delhi Capitals',3)]}
        doc['innings'][1]['target']={'runs':15,'overs':1}
        m=normalize(doc,'test');self.assertEqual(m['nrr'][0]['runs'],14);self.assertEqual(m['nrr'][0]['nrr_balls'],6)
        doc['info']['outcome']={'winner':'Mumbai Indians','by':{'runs':2},'method':'D/L'}
        doc['innings'][1]['overs'][0]['deliveries']=doc['innings'][1]['overs'][0]['deliveries'][:2]
        self.assertFalse(normalize(doc,'test')['nrr_valid'])

if __name__=='__main__':unittest.main()
