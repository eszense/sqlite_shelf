import unittest
from es_commons.suppress2 import suppress
import sqlite3
import os
import tempfile
from tests.test_mutabletable import DictTableTest
from sqlite_shelf.sqliteshelf import SqliteTable


class SqliteTableTest(DictTableTest):

    def setUp(self):
        self._tempfile = tempfile.mkstemp()

        self._conn = sqlite3.connect(self._tempfile[1])
        self.d = SqliteTable(self._conn)
        

    def tearDown(self):
        self.d.close()
        self._conn.commit()
        self._conn.close()
        os.close(self._tempfile[0])
        os.remove(self._tempfile[1])
        pass



if __name__ == '__main__':
    #unittest.TextTestRunner(verbosity=2).run(SqliteTableTest("test_get_set_del_item"))
    unittest.main()
    #import cProfile
    #cProfile.runctx('unittest.main()', locals=locals(), globals=globals())
