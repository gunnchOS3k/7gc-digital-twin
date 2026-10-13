import copy,json,unittest
from pathlib import Path
from verify_current import compare,digest,SUB,SOURCE_SHA
class VerificationTests(unittest.TestCase):
 def setUp(self):self.old=json.loads((SUB/'reproduction/rq1_gary_flagship_profiles.json').read_text())
 def rehash(self,x):x['result_sha256']=digest({k:v for k,v in x.items() if k not in ('result_sha256','wrote','statistical_artifacts')});return x
 def test_original_passes(self):self.assertTrue(compare(self.old,self.old)['scientific_payload_equal'])
 def test_scientific_alteration_fails_even_with_valid_hash(self):
  x=copy.deepcopy(self.old);x['statistical_report']['per_seed'][0]['primary']['task_completion_ratio']+=.001
  with self.assertRaisesRegex(ValueError,'Scientific payload mismatch'):compare(self.old,self.rehash(x))
 def test_benign_provenance_and_paths_validated_separately(self):
  x=copy.deepcopy(self.old)
  def change(v):
   if isinstance(v,dict):
    if 'provenance' in v:
     p=v['provenance'];p['producer']['commit']='951a91e9927354d5fcb7009819ea7bb16902c718';p['producer']['generated_at']='2026-10-13T12:00:00Z';p['content_sha256']=digest({k:a for k,a in p.items() if k!='content_sha256'})
    for a in v.values():change(a)
   elif isinstance(v,list):
    for a in v:change(a)
  change(x);x['wrote']='other/result.json';x['statistical_artifacts']={'csv':'other/stats.csv','md':'other/stats.md'}
  result=compare(self.old,self.rehash(x));self.assertTrue(result['provenance_validated']);self.assertNotEqual(result['historical_provenance'],result['fresh_provenance'])
 def test_invalid_provenance_fails(self):
  x=copy.deepcopy(self.old);x['provenance']['producer']['generated_at']='not-a-time'
  with self.assertRaises(ValueError):compare(self.old,self.rehash(x))
if __name__=='__main__':unittest.main()
