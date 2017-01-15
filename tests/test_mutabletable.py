import unittest
import pickle
import cProfile
from sqlite_shelf.mutabletable import DictTable

class DictTableTest(unittest.TestCase):
    
    def setUp(self):
        self.d = DictTable()
    def tearDown(self):
        pass
    
    def test_contains(self):
        self.assertFalse('0' in self.d)
        
        self.d.update({'0':{'0':'1'}, '1':{'1':'0'}})
        self.assertTrue('0' in self.d)
        self.assertFalse('2' in self.d)
        self.assertTrue('0' in self.d['0'])
        self.assertTrue('1' in self.d['0'])
        self.assertFalse('2' in self.d['0'])

                
    def test_eq_ge_gt_le_lt_ne(self):
        self.assertTrue(self.d == {})
                       
        self.d.update({'5':{'5':'1', '6':'1'}, '6':{'6':'1'}})
        self.assertTrue(self.d == {'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'1'}})
        self.assertFalse(self.d != {'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'1'}})
        self.assertFalse(self.d == {'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'0'}})
        self.assertTrue(self.d != {'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'0'}})
        self.assertTrue({'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'1'}} == self.d)
        self.assertTrue({'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'0'}} != self.d)

        with self.assertRaises(TypeError):
            self.assertTrue(self.d >  {'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'0'}})
        with self.assertRaises(TypeError):
            self.assertFalse(self.d <  {'5':{'5':'1', '6':'1'}, '6':{'5':None, '6':'0'}})

        d2 = DictTable()
        d2.update({'5':{'5':'1', '6':'1'}, '6':{'6':'1'}})
        self.assertTrue(d2 == self.d)
        self.assertFalse(d2 != self.d)
                       
        d2['6']['6'] = '0'
        self.assertFalse(d2 == self.d)
        self.assertTrue(d2 != self.d)

        with self.assertRaises(TypeError):
            self.assertTrue(self.d > d2)
        with self.assertRaises(TypeError):
            self.assertFalse(self.d < d2)
        
        
    def test_get_set_del_item(self):
        with self.assertRaises(KeyError):
            self.d['0']
        self.assertEqual(self.d.get('0',{'5':'55'}), {'5':'55'})
        self.assertEqual(self.d, {})
        
        with self.assertRaises(KeyError):
            self.d['0']['0']
        
        self.d['0'] = {'0':'1'}
        self.assertEqual(self.d['0'], {'0':'1'})
        self.assertEqual(self.d['0'], self.d['0'])
        self.assertEqual(self.d['0']['0'], '1')
        self.assertEqual(self.d.get('0',{'5':'55'}), {'0':'1'})
        self.assertEqual(self.d['0'].get('0','5'), '1')
        self.assertEqual(self.d['0'].get('1','5'), '5')

        self.d['1'] = {}
        self.d['1']['1'] = '1'
        self.assertEqual(self.d['0'], {'0':'1', '1':None})
        self.assertEqual(self.d['0'].get('1','1'), '1')
        
        del self.d['0']['0']
        self.assertEqual(self.d['0'], {'0':None, '1':None})
        self.assertEqual(self.d['0']['0'], None)

        del self.d['0']
        with self.assertRaises(KeyError):
            self.d['0']
            
        
        
    def test_iter(self):
        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'6':'66'}})

        _expected_a = ['6','5']
        _expected_b = ['6','5','6','5']
        _expected_c = [{'5':None, '6':'66'},{'5':'55', '6':'56'}]
        _expected_d = ['66',None,'56','55']
       
        

        expected_a = _expected_a.copy()
        expected_b = _expected_b.copy()
        for row in self.d:
            expected_a.remove(row)
            for col in self.d[row]:
                expected_b.remove(col)
        self.assertListEqual(expected_a, [])
        self.assertListEqual(expected_b, [])
        
        expected_a = _expected_a.copy()
        expected_b = _expected_b.copy()
        for row in self.d.keys():
            expected_a.remove(row)
            for col in self.d[row].keys():
                expected_b.remove(col)
        self.assertListEqual(expected_a, [])
        self.assertListEqual(expected_b, [])

        expected_c = _expected_c.copy()
        expected_d = _expected_d.copy()
        for row in self.d.values():
            expected_c.remove(row)
            for value in row.values():
                expected_d.remove(value)
        self.assertListEqual(expected_c, [])
        self.assertListEqual(expected_d, [])

       
        expected_a = _expected_a.copy()
        expected_b = _expected_b.copy()
        expected_c = _expected_c.copy()
        expected_d = _expected_d.copy()
        for row_key, row in self.d.items():
            expected_a.remove(row_key)
            expected_c.remove(row)
            for col_key, value in row.items():
                expected_b.remove(col_key)
                expected_d.remove(value)
        self.assertListEqual(expected_a, [])
        self.assertListEqual(expected_b, [])
        self.assertListEqual(expected_c, [])
        self.assertListEqual(expected_d, [])

        
    def test_len(self):
        self.assertEqual(len(self.d),0)
        with self.assertRaises(KeyError):
            len(self.d['0'])
            
        self.d['0'] = {'0':'1'}
        self.assertEqual(len(self.d),1)
        self.assertEqual(len(self.d['0']),1)
        with self.assertRaises(KeyError):
            len(self.d['1'])
        
        self.d['1'] = {'1':'1'}
        self.assertEqual(len(self.d),2)
        self.assertEqual(len(self.d['0']),2)
        
                

##    def test_reduce_ex(self):
##        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'6':'66'}})
##        self.assertEqual(pickle.loads(pickle.dumps(self.d)), self.d)
    
    def test_repr_str(self):
        self.assertEqual(str(self.d), "{}")
        self.assertEqual(repr(self.d), "{}")

        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'6':'66'}})

        expected = "{'6': {'6': '66', '5': None}, '5': {'6': '56', '5': '55'}}" #"{'5': {'5': '55', '6': '56'}, '6': {'5': None, '6': '66'}}"
        try:
            self.assertEqual(str(self.d), expected)
            self.assertEqual(repr(self.d), expected)
        except AssertionError:
            expected = "{'5': {'5': '55', '6': '56'}, '6': {'5': None, '6': '66'}}"
            self.assertEqual(str(self.d), expected)
            self.assertEqual(repr(self.d), expected)
        
    def test_clear(self):
        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'6':'66'}})
        
        self.d['5'].clear()
        self.assertEqual(self.d, {'5':{'5':None, '6':None}, '6':{'5':None, '6':'66'}})
        self.d.clear()
        self.assertEqual(self.d, {})


    def test_pop(self):
        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'6':'66'}})
        
        with self.assertRaises(KeyError):
            self.d.pop('7')
        self.assertEqual(self.d.pop('7','7'), '7')

        with self.assertRaises(KeyError):
            self.d['6'].pop('7')
        self.assertEqual(self.d['6'].pop('8','8'), '8')
        
        self.assertEqual(self.d['5'].pop('6'), '56')
        self.assertEqual(self.d, {'5':{'5':'55', '6':None}, '6':{'5':None, '6':'66'}})
        self.assertEqual(self.d.pop('5'), {'5':'55', '6':None})
        self.assertEqual(self.d, {'6':{'5':None, '6':'66'}})
        self.assertEqual(self.d['6'].pop('5'), None)
        
        self.assertEqual(self.d['6'].pop('6','7'), '66')
        self.assertEqual(self.d['6'].pop('5','7'), '7')
        self.assertEqual(self.d, {'6':{'5':None,'6':None}})



        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'6':'66'}})
        template = {'5':{'5':'55', '6':'56'}, '6':{'5':None, '6':'66'}}
        with self.assertRaises(KeyError):
                self.d['7'].popitem()
                
        for n in range(2):
            pair = self.d['5'].popitem()
            self.assertEqual(template['5'][pair[0]], pair[1])
            template['5'][pair[0]] = None
            self.assertEqual(self.d, template)
        with self.assertRaises(KeyError):
            self.d['5'].popitem()

        for n in range(2):
            pair = self.d.popitem()
            self.assertEqual(template.pop(pair[0]), pair[1])
            self.assertEqual(self.d, template)
        with self.assertRaises(KeyError):
            self.d.popitem()
    
        
    def test_setdefault(self):
        self.assertEqual(self.d.setdefault('5', {'5':'55'}),{'5':'55'}) 
        self.assertEqual(self.d, {'5':{'5':'55'}})
        self.assertEqual(self.d.setdefault('5', {'6':'56'}),{'5':'55'}) 
        self.assertEqual(self.d, {'5':{'5':'55'}})
        
        self.assertEqual(self.d.setdefault('6', {'6':'66'}),{'5':None, '6':'66'}) 
        self.assertEqual(self.d, {'5':{'5':'55', '6':None}, '6':{'5':None, '6':'66'}})
        
        self.assertEqual(self.d['5'].setdefault('5', '550'), '55') 
        self.assertEqual(self.d, {'5':{'5':'55', '6':None}, '6':{'5':None, '6':'66'}})
        
        self.assertEqual(self.d['5'].setdefault('6', '560'), '560') 
        self.assertEqual(self.d, {'5':{'5':'55', '6':'560'}, '6':{'5':None, '6':'66'}})

        self.assertEqual(self.d['5'].setdefault('7', '570'), '570') 
        self.assertEqual(self.d, {'5':{'5':'55', '6':'560', '7':'570'}, '6':{'5':None, '6':'66', '7':None}})
        
    def test_update(self):
        self.d.update({'5':{'5':'55', '6':'56'}, '6':{'5':None, '6':'66'}})
        self.assertEqual(self.d, {'5':{'5':'55', '6':'56'}, '6':{'5':None, '6':'66'}})
        
        self.d.update({'5':{'6':'560'}, '6':{'5':'650'}})
        self.assertEqual(self.d, {'5':{'5':'55', '6':'560'}, '6':{'5':'650', '6':'66'}})
        
        self.d.update({'5':{'7':'57'}})
        self.assertEqual(self.d, {'5':{'5':'55', '6':'560', '7':'57'}, '6':{'5':'650', '6':'66', '7':None}})
        
        self.d.update({'5':None})
        self.assertEqual(self.d, {'6':{'5':'650', '6':'66', '7':None}})
        
        self.d.update({'7':None})
        self.assertEqual(self.d, {'6':{'5':'650', '6':'66', '7':None}})
        
        
        self.d['6'].update({'5':None, '6':'660'})
        self.assertEqual(self.d, {'6':{'5':None, '6':'660', '7':None}})
        
        self.d['6'].update({'8':'68'})
        self.assertEqual(self.d, {'6':{'5':None, '6':'660', '7':None, '8':'68'}})

##    def test_profile(self):
##        cProfile.runctx('self.test_update()', locals=locals(), globals=globals())
##        
    def test_type(self):
        self.d.update({'5':{'5':55}})
        self.assertIsInstance(self.d['5']['5'], int)
        

if __name__ == '__main__':
    unittest.main()
