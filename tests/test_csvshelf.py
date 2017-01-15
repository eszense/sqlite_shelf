import unittest
from es_commons.suppress2 import suppress
import os
from tests.test_mutabletable import DictTableTest
from sqlite_shelf.csvshelf import CsvTable
import tempfile

class SqliteTableTest(DictTableTest):
    
    def setUp(self):
        self._tempfile = tempfile.mkstemp()
        self.d = CsvTable(self._tempfile[1])
        
    def tearDown(self):
        self.d.close()
        os.close(self._tempfile[0])
        os.remove(self._tempfile[1])
        pass



if __name__ == '__main__':
    #unittest.TextTestRunner(verbosity=2).run(SqliteTableTest("test_get_set_del_item"))
    unittest.main()
    #import cProfile
    #cProfile.runctx('unittest.main()', locals=locals(), globals=globals())
