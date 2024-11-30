import JackTokenizer
from VMWriter import VMWriter
from SymbolTable import SymbolTable

CONSTANT = 'constant'
ARGUMENT = 'argument'
POINTER = 'pointer'
STATIC = 'static'
THIS = 'this'
THAT = 'that'
TEMP = 'temp'

NOT = 'not'
NEG = 'neg'
ADD = 'add'
SUB = 'sub'
EQ = 'eq'
GT = 'gt'
LT = 'lt'
AND = 'and'
OR = 'or'

GOTO = 'goto'
IF_GOTO = 'if-goto'

class CompilationEngine:
    def __init__(self, input, output_file):
        self.__input = input
        self.__class_name = ''
        self.__if_index = 0
        self.__while_index = 0

        self.__output = VMWriter(output_file)
        self.__class_table = SymbolTable()
        self.__subroutine_table = SymbolTable()


    def compile_class(self):
        self.__input.advance()
        self.__class_name = self.__input.identifier()
        self.__input.advance()
        self.__input.advance()
        
        while self.__input.key_word() in [STATIC, 'field']:
            self.compile_class_var_dec()

        while self.__input.key_word() in ['method', 'function', 'constructor']:
            self.compile_subroutine()


    def compile_class_var_dec(self):
        kind = 'field'
        if self.__input.key_word() == STATIC:
            kind = STATIC

        self.__input.advance()
        type = self.__input.token()
        self.__input.advance()
        name = self.__input.identifier()
        self.__input.advance()

        self.__class_table.define(name, type, kind)

        while self.__input.symbol() == ',':
            self.__input.advance()
            name = self.__input.identifier()
            self.__input.advance()
            self.__class_table.define(name, type, kind)
        
        self.__input.advance()


    def compile_subroutine(self):
        self.__subroutine_table.reset()
        self.__if_index = 0
        self.__while_index = 0

        key_word = self.__input.key_word()
        self.__input.advance()
        return_type = self.__input.token()
        self.__input.advance()
        function_name = f'{self.__class_name}.{self.__input.identifier()}'
        self.__input.advance()

        if key_word == 'method':
            self.__subroutine_table.define(THIS, self.__class_name, ARGUMENT) # before parameter list

        self.__input.advance()
        self.compile_parameter_list()
        self.__input.advance()
        self.__input.advance()
        
        while self.__input.key_word() == 'var':
            self.compile_var_dec()

        if key_word == 'constructor':
            count = self.__class_table.var_count()
            self.__output.write_function(function_name, 0)
            self.__output.write_push(CONSTANT, count)
            self.__output.write_call('Memory.alloc', 1)
            self.__output.write_pop(POINTER, 0) 
            
        elif key_word == 'method':
            self.__output.write_function(function_name, self.__subroutine_table.var_count())
            self.__output.write_push(ARGUMENT, 0) 
            self.__output.write_pop(POINTER, 0) 
            
        elif key_word == 'function':
            self.__output.write_function(function_name, self.__subroutine_table.var_count())

        self.compile_subroutine_body()
        self.__input.advance()


    def compile_parameter_list(self):
        if self.__input.symbol() != ')':
            type = self.__input.token()
            self.__input.advance()
            name = self.__input.identifier()
            self.__input.advance()
            self.__subroutine_table.define(name, type, ARGUMENT)

            while self.__input.symbol() == ',':
                self.__input.advance()
                type = self.__input.token()
                self.__input.advance()
                name = self.__input.identifier()
                self.__input.advance()
                self.__subroutine_table.define(name, type, ARGUMENT)


    def compile_subroutine_body(self):
        self.compile_statements()
    

    def compile_var_dec(self):
        kind = self.__input.key_word()
        self.__input.advance()
        type = self.__input.token()
        self.__input.advance()
        name = self.__input.identifier()
        self.__input.advance()

        self.__subroutine_table.define(name, type, kind)

        while self.__input.symbol() == ',':
            self.__input.advance()
            name = self.__input.identifier()
            self.__input.advance()
            self.__subroutine_table.define(name, type, kind)

        self.__input.advance()
    

    def compile_statements(self):
        while self.__input.key_word() in ['let', 'if', 'while', 'do', 'return']:
            key_word = self.__input.key_word()
            if key_word == 'let':
                self.compileLet()
            elif key_word == 'if':
                self.compile_if()
            elif key_word == 'while':
                self.compile_while()
            elif key_word == 'do':
                self.compile_do()
            elif key_word == 'return':
                self.compile_return()


    def compileLet(self):
        self.__input.advance()
        name = self.__input.identifier()
        segment = self.__get_segment(name)
        index = self.__get_index(name)
        self.__input.advance()

        is_array = False
        if self.__input.symbol() == '[':
            is_array = True
            self.__input.advance()
            self.compile_expression()
            self.__input.advance()
            self.__output.write_push(segment, index)
            self.__output.write_arithmetic(ADD)

        self.__input.advance()
        self.compile_expression()

        if is_array:
            self.__output.write_pop(TEMP, 0)
            self.__output.write_pop(POINTER, 1)
            self.__output.write_push(TEMP, 0)
            segment = THAT
            index = 0
        
        self.__output.write_pop(segment, index)
        self.__input.advance()
    

    def compile_if(self):
        self.__input.advance()
        self.__input.advance()
        self.compile_expression()
        self.__input.advance()

        label_true = f'IF_TRUE{self.__if_index}'
        label_false = f'IF_FALSE{self.__if_index}'
        label_end = f'IF_END{self.__if_index}'
        self.__if_index += 1

        self.__output.write_if(label_true)
        self.__output.write_goto(label_false)
        self.__output.write_label(label_true)

        self.__input.advance()
        self.compile_statements()
        self.__input.advance()


        if (self.__input.key_word() == 'else'):
            self.__output.write_goto(label_end)
            self.__output.write_label(label_false)
            self.__input.advance()
            self.__input.advance()
            self.compile_statements()
            self.__input.advance()
            self.__output.write_label(label_end)
        else:
            self.__output.write_label(label_false)


    def compile_while(self):
        self.__input.advance()

        label_exp = f'WHILE_EXP{self.__while_index}'
        self.__output.write_label(label_exp)

        self.__input.advance()
        self.compile_expression()
        self.__output.write_arithmetic(NOT)
        self.__input.advance()

        label_end = f'WHILE_END{self.__while_index}'
        self.__output.write_if(label_end)

        self.__while_index += 1

        self.__input.advance()
        self.compile_statements()
        self.__input.advance()

        self.__output.write_goto(label_exp)
        self.__output.write_label(label_end)


    def compile_do(self):
        self.__input.advance()
        self.compile_expression()
        self.__input.advance()

        self.__output.write_pop(TEMP, 0)


    def compile_return(self):
        self.__input.advance()
        
        if self.__input.symbol() != ';':
            self.compile_expression()
        else:
            self.__output.write_push(CONSTANT, 0)

        self.__output.write_return()
        self.__input.advance()


    def compile_expression(self):
        self.compile_term()

        if self.__input.symbol() in ['+', '-', '*', '/', '&', '|', '<', '>', '=']:
            symbol = self.__input.symbol()
            self.__input.advance()
            self.compile_term()

            if symbol == '+':
                self.__output.write_arithmetic(ADD)
            elif symbol == '-':
                self.__output.write_arithmetic(SUB)
            elif symbol == '*':
                self.__output.write_call('Math.multiply', 2)
            elif symbol == '/':
                self.__output.write_call('Math.divide', 2)
            elif symbol == '&':
                self.__output.write_arithmetic(AND)
            elif symbol == '|':
                self.__output.write_arithmetic(OR)
            elif symbol == '>':
                self.__output.write_arithmetic(GT)
            elif symbol == '<':
                self.__output.write_arithmetic(LT)
            elif symbol == '=':
                self.__output.write_arithmetic(EQ)


    def compile_term(self):
        name = ''
        if self.__input.token_type() == JackTokenizer.INT_CONST:
            self.__output.write_push(CONSTANT, self.__input.int_val())
            self.__input.advance()

        elif self.__input.token_type() == JackTokenizer.STRING_CONST:
            self.__handle_string(self.__input.string_val())
            self.__input.advance()

        elif self.__input.key_word() in ['false', 'null']:
            self.__output.write_push(CONSTANT, 0)
            self.__input.advance()

        elif self.__input.key_word() == 'true':
            self.__output.write_push(CONSTANT, 0)
            self.__output.write_arithmetic(NOT)
            self.__input.advance()

        elif self.__input.key_word() == THIS:
            self.__output.write_push(POINTER, 0)
            self.__input.advance()

        elif self.__input.symbol() in ['-', '~']:
            symbol = self.__input.symbol()
            self.__input.advance()
            self.compile_term()
            if symbol == '-':
                self.__output.write_arithmetic(NEG)
            if symbol == '~':
                self.__output.write_arithmetic(NOT)

        elif self.__input.symbol() == '(':
            self.__input.advance()
            self.compile_expression()
            self.__input.advance()

        elif self.__input.token_type() == JackTokenizer.IDENTIFIER:
            name = self.__input.identifier()
            self.__input.advance()

            # Lookahead for [ ( or . 
            if self.__input.symbol() == '.':
                self.__input.advance()
                type = self.__get_type(name)
                method_name = self.__input.identifier()
                
                call_name = f'{type}.{self.__input.identifier()}'
                if type is None:
                    call_name = f'{name}.{self.__input.identifier()}'
                    
                self.__input.advance()
                self.__input.advance()
                
                if self.__subroutine_table.check_name(name) or self.__class_table.check_name(name):
                    segment = self.__get_segment(name)
                    index = self.__get_index(name)
                    self.__output.write_push(segment, index) # is method call

                    n_args = self.compile_expression_list()
                    self.__input.advance()
                    self.__output.write_call(call_name, n_args + 1)

                else:
                    n_args = self.compile_expression_list()
                    self.__input.advance()
                    self.__output.write_call(call_name, n_args)

            elif self.__input.symbol() == '(':
                self.__output.write_push(POINTER, 0)
                self.__input.advance()
                n_args = self.compile_expression_list()
                self.__input.advance()
                self.__output.write_call(f'{self.__class_name}.{name}', n_args + 1)

            elif self.__input.symbol() == '[':
                segment = self.__get_segment(name)
                index = self.__get_index(name)
                self.__input.advance()
                self.compile_expression()
                self.__input.advance()

                self.__output.write_push(segment, index)
                self.__output.write_arithmetic(ADD)
                self.__output.write_pop(POINTER, 1)
                self.__output.write_push(THAT, 0)

            else:
                segment = self.__get_segment(name)
                index = self.__get_index(name)
                self.__output.write_push(segment, index)


    def __get_type(self, name):
        return self.__subroutine_table.type_of(name) or self.__class_table.type_of(name)


    def __get_segment(self, name):
        return self.__subroutine_table.kind_of(name) or self.__class_table.kind_of(name)


    def __get_index(self, name):
        subroutine_segment = self.__subroutine_table.index_of(name)
        class_segment = self.__class_table.index_of(name)
        return subroutine_segment if subroutine_segment is not None else class_segment


    def __handle_string(self, string):
        self.__output.write_push(CONSTANT, len(string))
        self.__output.write_call('String.new', 1)

        for char in string:
            self.__output.write_push(CONSTANT, ord(char))
            self.__output.write_call('String.appendChar', 2)


    def compile_expression_list(self):
        count = 0
        if self.__input.symbol() != ')':
            count += 1
            self.compile_expression()

            while self.__input.symbol() == ',':
                count += 1
                self.__input.advance()
                self.compile_expression()

        return count
