from collections import Mapping, MutableMapping
from es_commons.suppress2 import suppress
import sqlite3
import re
from sqlite_shelf.mutabletable import MutableTable


class SqliteTable(MutableTable):
    __slots__ = ('_c', '_table')
    _type_mapping = {str:"TEXT", int:"INT", float:"REAL", None.__class__:"TEXT"}
    
    def __init__(self, conn, table="DefaultTable"):
        self._c = conn.cursor()
        self._table = table
        with suppress(sqlite3.Error, regex=r"table %s already exists" % table):
            self._c.execute('CREATE TABLE %s (_id TEXT PRIMARY KEY NOT NULL)' % self._table)
        
    def close(self):
        self._c.close()
    
    def _del_row(self, row):
        "Raises: KeyError"
        self._c.execute('DELETE FROM %s WHERE _id = ?' % self._table, (row,))
        assert self._c.rowcount < 2
        if self._c.rowcount == 0:
            raise KeyError("Row with id %s does not exists in %s" % (row,self._table))
        
        
    
    def _update_cells(self, row, values):
        values = {str(k): v for k, v in values.items()}
        values["_id"] = row
        while True:
            try:
                self._c.execute('UPDATE %s SET "%s WHERE _id = :_id' % 
                                    (self._table, ', "'.join(map(lambda x: x+'" = :'+x, filter(lambda x: x!="_id", values.keys())))),
                                    values)
                assert self._c.rowcount < 2
                if self._c.rowcount == 0:
                    self._c.execute('INSERT INTO "%s" ("%s") VALUES (:%s)' % (self._table, '", "'.join(values.keys()), ", :".join(values.keys())), values)
                return
            except sqlite3.OperationalError as e:
                match = re.match(r"no such column: (\w+)", e.args[0])
                if match:
                    self._c.execute('ALTER TABLE %s ADD COLUMN "%s" %s' % (self._table, match.group(1), self._type_mapping[values[match.group(1)].__class__]))
                    continue
                raise
    
    def _get_cells(self, row):
        "Raises: KeyError"
        self._c.execute('SELECT * FROM %s WHERE _id = ?' % self._table, (row,))
        r = self._c.fetchone()
        if r is None:
            raise KeyError("Row with id %s does not exists in %s" % (row,self._table))
        r = sqlite3.Row(self._c, r)
        assert r["_id"] == row
        r = dict(r)
        del r["_id"]
        return r
    
    
    def _get_column_names(self):
        self._c.execute('PRAGMA table_info(%s)' % self._table)
        assert self._c.fetchone()[1] == "_id"
        return map(lambda row: row[1], self._c.fetchall())
    
    def _get_row_names(self):
        self._c.execute('SELECT _id FROM %s' % self._table)
        r = list(map(lambda row: row[0], self._c.fetchall()))
        return r
    

