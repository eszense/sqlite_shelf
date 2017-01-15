from collections import Mapping, MutableMapping, deque
from contextlib import suppress
from abc import abstractmethod
from itertools import count as icount

def count(iterable):
    counter = icount()
    deque(zip(iterable, counter), maxlen=0)  # (consume at C speed)
    return next(counter)

class MutableRowView(MutableMapping):
    """ Proxy for accessing row of Mutable Table

    Behavior:
    - Table is regular, hence del will only fill cell with None
    """
    
    __slots__ = ('_parent','_row')
    
    def __init__(self, parent, row):
        self._parent = parent
        self._row = row
        
    def __delitem__(self, col):
        self[col] = None
       
    def __getitem__(self, col):
        return self._parent._get_cells(self._row)[col]
        
    def __iter__(self):
        yield from self._parent._get_column_names()
        
    def __len__(self):
        return count(self._parent._get_column_names())
        
    def __setitem__(self, col, value):
        self._parent._update_cells(self._row, {col:value})
        
    def __repr__(self):
        return str(self._parent._get_cells(self._row))

    #Reimplemented since None means not exists

    __marker = object()
    def pop(self, key, default=__marker):
        '''D.pop(k[,d]) -> remove D[k] and return existing value.
          If k not exists, return d if given, otherwise raise KeyError / return None
          according original D[k] result.
        '''
        try:
            value = self[key]
            if value is None:
                if default is not self.__marker:
                    return default
            del self[key]
            return value
        except KeyError:
            if default is self.__marker:
                raise
            return default
        #TODO Test it
        
    def popitem(self):
        '''D.popitem() -> (k, v), remove and return a (key, value) 2-tuple;
           Raise KeyError if D has no existent pair.
        '''
        try:
            i = iter(self)
            while True:
                key = next(i)
                value = self[key]
                if value is not None:
                    del self[key]
                    return key, value
        except StopIteration:
            raise KeyError

    def get(self, key, default=None):
        'D.get(k[,d=None]) -> D[k] if D[k] exists(incl not None), else d.'
        with suppress(KeyError):
            value = self[key]
            if value is not None:
                return value
        return default

    def setdefault(self, key, default=None):
        'D.setdefault(k[,d]) -> D.get(k,d) and set D[k]=d if not exists'
        with suppress(KeyError):
            value = self[key]
            if value is not None:
                return value
        self[key] = default
        return default
    

class MutableTable(MutableMapping):
    __slots__ = ()


    def __delitem__(self, row):
        self._del_row(row)
       
    def __getitem__(self, row):
        if row not in self:
            raise KeyError("Row with id %s does not exists" % row)
        return MutableRowView(self, row)
        
    def __setitem__(self, row, values):
        if values is not None:
            new_row = dict(map(lambda col: (col,None),self._get_column_names()))
            new_row.update(values)
            self._update_cells(row, new_row)
        else:
            with suppress(KeyError):
                del self[row]

    def __iter__(self):
        yield from self._get_row_names()
        
    def __len__(self):
        return len(self._get_row_names())

    def __contains__(self, row):
        return row in self._get_row_names()

    def __repr__(self):
        ret = dict()
        for row_key, row in self.items():
            ret[row_key] = dict()
            for col_key, value in row.items():
                ret[row_key][col_key]=value
        return str(ret)

    __marker = object()
    def pop(self, row, default=__marker):
        '''D.pop(k[,d]) -> v, remove specified row and return the corresponding dict.
          If row is not found, d is returned if given, otherwise KeyError is raised.
        '''
        try:
            value = self._get_cells(row)
        except KeyError:
            if default is self.__marker:
                raise
            return default
        else:
            del self[row]
            return value
        
    def popitem(self):
        '''D.popitem() -> (k, v), remove and return some (key, dict) pair
           as a 2-tuple; but raise KeyError if D is empty.
        '''
        try:
            row = next(iter(self))
        except StopIteration:
            raise KeyError
        value = self._get_cells(row)
        del self[row]
        return row, value

    def update(*args, **kwds):
        ''' D.update([E, ]**F) -> None.  Update D from mapping/iterable E and F.
            If E present and has a .keys() method, does:     for k in E: D[k].update(E[k])
            If E present and lacks .keys() method, does:     for (k, v) in E: D[k].update(v)
            In either case, this is followed by: for k, v in F.items(): D[k].update(v)

            N.B. if E[k] / F is None, row is removed
        '''
        def update_row(key, value):
            if value is None:
                self[key] = None
            else:
                try:
                    row = self[key]
                except KeyError:
                    self[key] = value
                else:
                    self[key].update(value)
            
        
        if not args:
            raise TypeError("descriptor 'update' of 'MutableMapping' object "
                            "needs an argument")
        self, *args = args
        if len(args) > 1:
            raise TypeError('update expected at most 1 arguments, got %d' %
                            len(args))
        if args:
            other = args[0]
            if isinstance(other, Mapping):
                for key in other:
                    update_row(key, other[key])
            elif hasattr(other, "keys"):
                for key in other.keys():
                    update_row(key, other[key])
            else:
                for key, value in other:
                    update_row(key, value)
        for key, value in kwds.items():
            update_row(key, other[key])

    def setdefault(self, key, default=None):
        'D.setdefault(k[,d]) -> D.get(k,d), also set D[k]=d if k not in D'
        try:
            return self[key]
        except KeyError:
            self[key] = default
        return self[key]
        
    @abstractmethod
    def _del_row(self, row):
        "Raises: KeyError"
        raise NotImplementedError

    @abstractmethod
    def _update_cells(self, row, values):
        raise NotImplementedError
    
    @abstractmethod
    def _get_cells(self, row):
        "Raises: KeyError"
        raise NotImplementedError
    
    @abstractmethod
    def _get_column_names(self):
        raise NotImplementedError

    @abstractmethod
    def _get_row_names(self):
        raise NotImplementedError
    

class DictTable(MutableTable):
    
    def __init__(self):
        self._rows = set()
        self._cols = set()
        self._cells = dict()
    
    def _del_row(self, row):
        if row not in self._rows:
            raise KeyError("Row with id %s does not exists" % row)
        self._rows.discard(row)
        for key in list(filter(lambda key: key[0] == row, self._cells)):
            del self._cells[key]
    def _update_cells(self, row, values):
        self._rows.add(row)
        for col,value in values.items():
            self._cols.add(col)
            self._cells[(row,col)] = value
    
    def _get_cells(self, row):
        if row not in self._rows:
            raise KeyError("Row with id %s does not exists" % row)
        return dict(map(
            lambda col: (col, self._cells[(row,col)] if (row,col) in self._cells else None),
            self._cols))
               
    def _get_column_names(self):
        return self._cols

    def _get_row_names(self):
        return self._rows
        

