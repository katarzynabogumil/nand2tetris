class SymbolTable:
    def __init__(self):
        self.reset()


    def reset(self):
        self.__table = {}
        self.__indexes = {
            'static': 0,
            'field': 0,
            'argument': 0,
            'var': 0,
        }


    def define(self, name, type, kind):
        segment = ''
        if kind == 'var':
            segment = 'local'
        elif kind == 'argument':
            segment = 'argument'
        elif kind == 'static':
            segment = 'static'
        elif kind == 'field':
            segment = 'this'
        
        self.__table[name] = {
            'type': type,
            'kind': segment,
            'index': self.__indexes[kind],
        }
        self.__indexes[kind] += 1


    def var_count(self):
        return self.__indexes['field'] + self.__indexes['var']


    def kind_of(self, name):
        record = self.__table.get(name)
        return None if not record else record['kind']


    def type_of(self, name):
        record = self.__table.get(name)
        return None if not record else record['type']


    def index_of(self, name):
        record = self.__table.get(name)
        return None if not record else record['index']


    def check_name(self, name):
        return bool(name in self.__table.keys())
