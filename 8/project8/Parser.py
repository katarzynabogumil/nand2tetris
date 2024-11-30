import re

C_ARITHMETIC= 'C_ARITHMETIC'
C_PUSH= 'C_PUSH'
C_POP = 'C_POP'
C_LABEL = 'C_LABEL'
C_GOTO = 'C_GOTO'
C_IF = 'C_IF'
C_FUNCTION = 'C_FUNCTION'
C_RETURN = 'C_RETURN'
C_CALL = 'C_CALL'

COMMAND_TYPES = {      
    'push': C_PUSH,
    'pop': C_POP,
    'label': C_LABEL,
    'if-goto': C_IF,
    'goto': C_GOTO,
    'function': C_FUNCTION,
    'return': C_RETURN,
    'call': C_CALL,
}

class Parser:
    def __init__(self, file_name):
        self.__file = open(file_name, 'r')

        self.__file.seek(0, 2)
        self.__eof = self.__file.tell()
        self.__file.seek(0, 0)

        self.__current_line = ''

    def has_more_lines(self):
        return self.__file.tell() != self.__eof

    def advance(self):
        self.__current_line = self.__parse_line(self.__file.readline())

    def command_type(self):
        if self.__current_line is None:
            return None
        
        type_indicator = self.__current_line[0]
        return COMMAND_TYPES.get(type_indicator, C_ARITHMETIC)
    
    def arg1(self):
        return self.__current_line[0] if self.command_type() == C_ARITHMETIC else self.__current_line[1]
    
    def arg2(self):
        return self.__current_line[2]
    
    def __del__(self):
        self.__file.close()
    
    def __parse_line(self, line):
        parsed_pine = re.sub('//.*', '', line).strip()
        return None if len(parsed_pine) == 0 else parsed_pine.split(' ')
    
    def __str__(self):
        return f'current_line: {self.__current_line}, tell: {self.__file.tell()}, eof: {self.__eof}'
