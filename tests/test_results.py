import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import qualification_message, computer

class ResultMessages(unittest.TestCase):
    def test_all_probability_ranges(self):
        cases=[(0,'did not qualify'),(.1,'big turnaround'),(9.9,'big turnaround'),(10,'Keep the faith'),(39.9,'Keep the faith'),(40,'either way'),(60,'either way'),(60.1,'promising'),(89.9,'promising'),(90,'strong'),(99.9,'strong'),(100,'clean sweep')]
        for chance,phrase in cases:
            with self.subTest(chance=chance):
                title,text=qualification_message('RCB',chance)
                self.assertIn(phrase,title)
                self.assertIn('RCB',title)
        self.assertIn('does not prove',qualification_message('RCB',0)[1])
        self.assertIn('not a mathematical guarantee',qualification_message('RCB',100)[1])
    def test_notice_uses_selected_team_and_only_appears_after_run(self):
        session=dict(team='MI',csrf='test')
        self.assertNotIn(b'<dialog',computer(session))
        results=[dict(team='RCB',chance=99,nrr_low=0,nrr_high=1),dict(team='MI',chance=0,nrr_low=-1,nrr_high=0)]
        html=computer(session,results).decode()
        self.assertIn('Sorry, MI did not qualify',html)
        self.assertIn('<dialog open',html)
        self.assertIn('method="dialog"',html)
        self.assertNotIn('<script',html)

if __name__=='__main__':unittest.main()
