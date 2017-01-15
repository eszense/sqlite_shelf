from collections import Mapping, MutableMapping
from es_commons.suppress2 import suppress
import re
from sqlite_shelf.mutabletable import DictTable
import csv


class CsvTable(DictTable):
    __slots__ = ('_path')
    
    
    def __init__(self, path):
        self._path = path
        DictTable.__init__(self)
        
    def close(self):
        with open(self._path, 'w', encoding='utf-8',newline="\n") as csvfile:
            csvfile.write(u'\ufeff')
            fieldnames = ['_id']
            fieldnames.extend(sorted(self._cols))
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            row_lists = []
            for row in self._rows:
                row_dict = {'_id':row}
                for col in self._cols:
                    row_dict[col] = self._cells.get((row,col), None)
                row_lists.append(row_dict)
            writer.writerows(row_lists)
            
