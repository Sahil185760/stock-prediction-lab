import copy,json,unittest,datetime
from pathlib import Path
import engine
from models import fit_ridge,predict
class Tests(unittest.TestCase):
 def setUp(self):self.data=json.loads(Path(__file__).with_name('example.json').read_text())
 def test_known_linear_fit(self):
  model=fit_ridge([[i] for i in range(10)],[2*i+3 for i in range(10)],1e-8)
  self.assertAlmostEqual(predict(model,[20]),43,places=6)
 def test_constant_price_baseline(self):
  for r in self.data['observations']:r['close']=100
  out=engine.run(self.data)
  self.assertEqual(out['metrics']['Walk-forward MAE'],0)
  self.assertEqual(out['metrics']['Zero-return baseline MAE'],0)
 def test_future_prices_do_not_change_earlier_prediction(self):
  first=engine.run(self.data);changed=copy.deepcopy(self.data);changed['observations'][-1]['close']*=1.2
  second=engine.run(changed)
  self.assertEqual([r['predicted_return'] for r in first['rows']],[r['predicted_return'] for r in second['rows']])
 def test_future_date_rejected(self):
  self.data['observations'][-1]['date']='2025-12-01'
  with self.assertRaises(ValueError):engine.run(self.data)
 def test_duplicate_date_rejected(self):
  self.data['observations'][-1]['date']=self.data['observations'][-2]['date']
  with self.assertRaises(ValueError):engine.run(self.data)
 def test_invalid_prices(self):
  for bad in [0,-1,float('nan'),float('inf')]:
   self.data['observations'][0]['close']=bad
   with self.assertRaises(ValueError):engine.run(self.data)
 def test_prediction_date_alignment(self):
  out=engine.run(self.data)
  self.assertEqual(out['rows'][-1]['date'],self.data['observations'][-1]['date'])
  actual=self.data['observations'][-1]['close']/self.data['observations'][-2]['close']-1
  self.assertAlmostEqual(out['rows'][-1]['actual_return'],actual)
 def test_bundled_data_is_before_september(self):
  self.assertEqual(self.data['as_of'],'2025-08-29')
  self.assertEqual(self.data['observations'][-1]['date'],'2025-08-29')
  self.assertTrue(all(r['date']<'2025-09-01' for r in self.data['observations']))
if __name__=='__main__':unittest.main()
