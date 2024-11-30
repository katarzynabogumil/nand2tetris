import re
import html

import JackTokenizer

class CompilationEngine:
    def __init__(self, input, output_file):
        self.__input = input
        self.__output_file = output_file
        self.__indentation = ''


    def compile_class(self):
        self.__write_start_tag('class')
        self.__write_line(self.__input.key_word())
        self.__write_line(self.__input.identifier())
        self.__write_line(self.__input.symbol())
        
        while self.__input.key_word() in ['static', 'field']:
            self.compile_class_var_dec()

        while self.__input.key_word() in ['method', 'function', 'constructor']:
            self.compile_subroutine()

        self.__write_line(self.__input.symbol())
        self.__write_end_tag('class')
    

    def compile_class_var_dec(self):
        self.__write_start_tag('classVarDec')
        self.__write_line(self.__input.key_word())
        self.__write_line(self.__input.token()) # type
        self.__write_line(self.__input.identifier())

        while self.__input.symbol() == ',':
            self.__write_line(self.__input.symbol())
            self.__write_line(self.__input.identifier())
        
        self.__write_line(self.__input.symbol())
        self.__write_end_tag('classVarDec')
    

    def compile_subroutine(self):
        self.__write_start_tag('subroutineDec')
        self.__write_line(self.__input.key_word())
        self.__write_line(self.__input.token()) # return type
        self.__write_line(self.__input.identifier())
        self.__write_line(self.__input.symbol())
        self.compile_parameter_list()
        self.__write_line(self.__input.symbol())
        self.compile_subroutine_body()
        self.__write_end_tag('subroutineDec')


    def compile_parameter_list(self):
        self.__write_start_tag('parameterList')

        if self.__input.symbol() != ')':
            self.__write_line(self.__input.token()) # type
            self.__write_line(self.__input.identifier())

            while self.__input.symbol() == ',':
                self.__write_line(self.__input.symbol())
                self.__write_line(self.__input.token()) # type
                self.__write_line(self.__input.identifier())
        
        self.__write_end_tag('parameterList')
    

    def compile_subroutine_body(self):
        self.__write_start_tag('subroutineBody')
        self.__write_line(self.__input.symbol())
        
        while self.__input.key_word() == 'var':
            self.compile_var_dec()

        self.compile_statements()

        self.__write_line(self.__input.symbol())
        self.__write_end_tag('subroutineBody')
    

    def compile_var_dec(self):
        self.__write_start_tag('varDec')
        self.__write_line(self.__input.key_word())
        self.__write_line(self.__input.token()) # type
        self.__write_line(self.__input.identifier())

        while self.__input.symbol() == ',':
            self.__write_line(self.__input.symbol())
            self.__write_line(self.__input.identifier())

        self.__write_line(self.__input.symbol())
        self.__write_end_tag('varDec')
    

    def compile_statements(self):  
        self.__write_start_tag('statements')

        while self.__input.key_word() in ['let', 'if', 'while', 'do', 'return']:
            key_word = self.__input.key_word()
            if key_word == 'let':
                self.compile_let()
            elif key_word == 'if':
                self.compile_if()
            elif key_word == 'while':
                self.compile_while()
            elif key_word == 'do':
                self.compile_do()
            elif key_word == 'return':
                self.compile_return()
    
        self.__write_end_tag('statements')


    def compile_let(self):
        self.__write_start_tag('letStatement')
        self.__write_line(self.__input.key_word())
        self.__write_line(self.__input.identifier())

        while self.__input.symbol() == '[':
            self.__write_line(self.__input.symbol())
            self.compile_expression()
            self.__write_line(self.__input.symbol())

        self.__write_line(self.__input.symbol())
        self.compile_expression()
        self.__write_line(self.__input.symbol())

        self.__write_end_tag('letStatement')
    

    def compile_if(self):
        self.__write_start_tag('ifStatement')
        self.__write_line(self.__input.key_word())

        self.__write_line(self.__input.symbol())
        self.compile_expression()
        self.__write_line(self.__input.symbol())

        self.__write_line(self.__input.symbol())
        self.compile_statements()
        self.__write_line(self.__input.symbol())

        if (self.__input.key_word() == 'else'):
            self.__write_line(self.__input.key_word())
            self.__write_line(self.__input.symbol())
            self.compile_statements()
            self.__write_line(self.__input.symbol())

        self.__write_end_tag('ifStatement')
    

    def compile_while(self):
        self.__write_start_tag('whileStatement')
        self.__write_line(self.__input.key_word())

        self.__write_line(self.__input.symbol())
        self.compile_expression()
        self.__write_line(self.__input.symbol())

        self.__write_line(self.__input.symbol())
        self.compile_statements()
        self.__write_line(self.__input.symbol())

        self.__write_end_tag('whileStatement')
    

    def compile_do(self):
        self.__write_start_tag('doStatement')
        self.__write_line(self.__input.key_word())
        self.__write_line(self.__input.identifier())

        if (self.__input.symbol() == '.'):
            self.__write_line(self.__input.symbol())
            self.__write_line(self.__input.identifier())

        self.__write_line(self.__input.symbol())
        self.compile_expression_list()
        self.__write_line(self.__input.symbol())

        self.__write_line(self.__input.symbol())
        self.__write_end_tag('doStatement')
    

    def compile_return(self):
        self.__write_start_tag('returnStatement')
        self.__write_line(self.__input.key_word())
        
        if self.__input.symbol() != ';':
            self.compile_expression()

        self.__write_line(self.__input.symbol())
        self.__write_end_tag('returnStatement')
    

    def compile_expression(self):
        self.__write_start_tag('expression')
        self.compile_term()

        while self.__input.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            self.__write_line(self.__input.symbol())
            self.compile_term()

        self.__write_end_tag('expression')
    

    def compile_term(self):
        self.__write_start_tag('term')

        if self.__input.token_type() == JackTokenizer.INT_CONST:
            self.__write_line(self.__input.int_val())
        elif self.__input.token_type() == JackTokenizer.STRING_CONST:
            self.__write_line(self.__input.string_val())
        elif self.__input.token_type() == JackTokenizer.IDENTIFIER:
            self.__write_line(self.__input.identifier())
        elif self.__input.key_word() in ['true', 'false', 'null', 'this']:
            self.__write_line(self.__input.key_word())
        elif self.__input.symbol() in ['-', '~']:
            self.__write_line(self.__input.symbol())
            self.compile_term()

        # Lookahead for [ ( or . 
        if self.__input.symbol() == '[':
            self.__write_line(self.__input.symbol())
            self.compile_expression()
            self.__write_line(self.__input.symbol())
        elif self.__input.symbol() == '(':
            self.__write_line(self.__input.symbol())
            self.compile_expression_list()
            self.__write_line(self.__input.symbol())
        elif self.__input.symbol() == '.':
            self.__write_line(self.__input.symbol())
            self.__write_line(self.__input.identifier())
            self.__write_line(self.__input.symbol())
            self.compile_expression_list()
            self.__write_line(self.__input.symbol())

        self.__write_end_tag('term')
    

    def compile_expression_list(self):
        self.__write_start_tag('expressionList')

        if self.__input.symbol() != ')':
            self.compile_expression()

            while self.__input.symbol() == ',':
                self.__write_line(self.__input.symbol())
                self.compile_expression()
    
        self.__write_end_tag('expressionList')


    def __write_line(self, input):
        if isinstance(input, str):
            input = html.escape(input)

        self.__output_file.writelines(f'{self.__indentation}<{self.__input.token_type()}> {input} </{self.__input.token_type()}>\n')
        self.__input.advance()


    def __write_start_tag(self, tag):
        self.__output_file.writelines(f'{self.__indentation}<{tag}>\n')
        self.__indentation += '  '


    def __write_end_tag(self, tag):
        self.__indentation = re.sub(r'^  ', '', self.__indentation)
        self.__output_file.writelines(f'{self.__indentation}</{tag}>\n')