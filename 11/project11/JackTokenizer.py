import re

KEYWORD = 'keyword'
SYMBOL = 'symbol'
IDENTIFIER = 'identifier'
INT_CONST = 'integerConstant'
STRING_CONST = 'stringConstant'

KEYWORDS = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
SYMBOLS = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']

class JackTokenizer:
    def __init__(self, file_name):
        self.__file = open(file_name, 'r')
        self.__is_parsing_multiline_comment = False

        self.__file.seek(0, 2)
        self.__eof = self.__file.tell()
        self.__file.seek(0, 0)

        self.__tokenizedInput = []
        self.__tokenizerIndex = 0

        self.__tokenizeInput()
    
    
    def __del__(self):
        self.__file.close()
    

    def has_more_tokens(self):
        return self.__tokenizerIndex != (len(self.__tokenizedInput) - 1)


    def advance(self):
        self.__tokenizerIndex += 1
        return


    def __get_token(self):
        return self.__tokenizedInput[self.__tokenizerIndex]


    def token_type(self):
        token = self.__get_token()
        
        if token in KEYWORDS:
            return KEYWORD
        
        if token in SYMBOLS:
            return SYMBOL
        
        if token.isdigit():
            return INT_CONST
        
        if token[0] == '"' and (token.strip())[len(token) - 1] == '"':
            return STRING_CONST

        if bool(re.match(r'^[a-zA-Z0-9_]+$', token)) and bool(re.match(r'^[a-zA-Z_]$', token[0])):
            return IDENTIFIER

        return None
    

    def token(self):
        return self.__get_token()
    

    def key_word(self):
        if (self.token_type() == KEYWORD):
            return self.__get_token()
    

    def symbol(self):
        if (self.token_type() == SYMBOL):
            return self.__get_token()
    

    def identifier(self):
        if (self.token_type() == IDENTIFIER):
            return self.__get_token()
    

    def int_val(self):
        if (self.token_type() == INT_CONST):
            return int(self.__get_token())
    

    def string_val(self):
        if (self.token_type() == STRING_CONST):
            return re.sub(r'"', '', self.__get_token()) 


    def __tokenizeInput(self):
        while self.__has_more_lines():
            lineChars = self.__parse_line(self.__file.readline())

            if lineChars is None:
                continue

            token = ''
            isString = False
            for char in lineChars:
                if char == '"':
                    isString = not isString 
                    token += char
                elif char == ' ' and not isString:
                    self.__push_token(token)
                    token = ''
                elif char in SYMBOLS:
                    if isString:
                        token += char
                    else:
                        self.__push_token(token)
                        self.__push_token(char)
                        token = ''
                else:
                    token += char
    

    def __push_token(self, token):
        if len(token) > 0:
            self.__tokenizedInput.append(token)


    def __has_more_lines(self):
        return self.__file.tell() != self.__eof


    def __parse_line(self, line):
        parsed_line = line
        if self.__is_parsing_multiline_comment and '*/' not in parsed_line:
            return None
        
        if self.__is_parsing_multiline_comment:
            parsed_line = re.sub(r'.*\*/', '', parsed_line).strip()
            self.__is_parsing_multiline_comment = False
        
        parsed_line = re.sub(r'/\*\*.*\*/', '', parsed_line)

        if not self.__is_parsing_multiline_comment and '/**' in parsed_line:
            self.__is_parsing_multiline_comment = True
            parsed_line = re.sub(r'/\*\*.*', '', parsed_line)
        
        parsed_line = re.sub(r'//.*', '', parsed_line).strip()

        return None if len(parsed_line) == 0 else parsed_line


    def __str__(self):
        return f'tokenizedInput: {self.__tokenizedInput}, tokenizerIndex: {self.__tokenizerIndex}'
