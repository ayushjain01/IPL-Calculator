import http.client,json,re,sys,threading,unittest
from pathlib import Path
from urllib.parse import urlencode
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from server import Handler,ThreadingHTTPServer,REPLAY

class BrowserContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True);cls.thread.start()
    @classmethod
    def tearDownClass(cls):cls.server.shutdown();cls.server.server_close()
    def request(self,method,path,body=None,cookie=None,host=None):
        c=http.client.HTTPConnection('127.0.0.1',self.server.server_port)
        headers={}
        if cookie:headers['Cookie']=cookie
        if body is not None:headers['Content-Type']='application/x-www-form-urlencoded'
        if host:headers['Host']=host
        c.request(method,path,body=urlencode(body) if body is not None else None,headers=headers)
        response=c.getresponse();data=response.read().decode();result=(response.status,dict(response.getheaders()),data);c.close();return result
    def test_every_page_is_script_free_and_csp_blocks_scripts(self):
        for path in ('/','/calculate.html','/predict.html','/model.html'):
            status,headers,body=self.request('GET',path)
            self.assertEqual(status,200);self.assertNotIn('<script',body.lower());self.assertIn("script-src 'none'",headers['Content-Security-Policy'])
    def test_manual_form_session_reset_and_computer_independence(self):
        _,headers,body=self.request('GET','/predict.html')
        cookie=headers['Set-Cookie'].split(';')[0];token=re.search('name="csrf" value="([^"]+)',body).group(1)
        match=REPLAY['remaining'][0]
        fields={'csrf':token,'team':'RCB','action':'update','pick_'+match['id']:match['teams'][0]}
        status,_,body=self.request('POST','/predict.html',fields,cookie)
        self.assertEqual(status,200);self.assertIn('1 of 30 matches predicted',body)
        _,_,body=self.request('GET','/predict.html',cookie=cookie);self.assertIn('1 of 30 matches predicted',body)
        status,_,body=self.request('POST','/calculate.html',dict(csrf=token,team='RCB',count='1000'),cookie)
        self.assertEqual(status,200);self.assertIn('1,000 simulated seasons',body)
        _,_,body=self.request('GET','/predict.html',cookie=cookie);self.assertIn('1 of 30 matches predicted',body)
        status,_,body=self.request('POST','/predict.html',dict(csrf=token,team='RCB',action='reset'),cookie)
        self.assertEqual(status,200);self.assertIn('0 of 30 matches predicted',body)
    def test_bad_forms_hosts_and_private_files_are_rejected(self):
        self.assertEqual(self.request('POST','/predict.html',dict(csrf='wrong'))[0],403)
        self.assertEqual(self.request('GET','/data/replay.json')[0],404)
        self.assertEqual(self.request('GET','/server.py')[0],404)
        self.assertEqual(self.request('GET','/app.js')[0],404)
        self.assertEqual(self.request('GET','/',host='external.example')[0],403)
        self.assertEqual(self.request('GET','/static/../server.py')[0],404)

if __name__=='__main__':unittest.main()
