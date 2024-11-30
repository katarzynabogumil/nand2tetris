import os

import Parser

class CodeWriter:
    def __init__(self, file_name):
        self.__file = open(file_name, 'w')
        self.__file_name = os.path.basename(file_name).replace('.asm', '')
        self.__function_name = [f'{self.__file_name}.main']
        self.__jump_counter = 0
        self.__return_counter = 0
        self.__is_defining_function = False

    def bootstrap(self):
        lines = ['@256', 'D=A', '@SP', 'M=D']
        self.__file.writelines([line + '\n' for line in lines])
        self.write_call('Sys.init', 0)
        
    def close(self):
        self.__file.close()

    def set_file_name(self, base_file_name):
        self.__file_name = os.path.basename(base_file_name)

    def get_function_name(self):
        return self.__function_name[-1]
    
    def write_push_pop(self, command, segment, index):
        lines=[]

        if segment == 'constant':
            lines = self.__handle_constant_segment(index)
        if segment in ['static', 'temp', 'pointer']:
            lines = self.__handle_direct_address_segment(command, segment, index)
        if segment in ['local',  'argument',  'this',  'that']:
            lines = self.__handle_base_address_segment(command, segment, index)

        self.__file.writelines([line + '\n' for line in lines])

    def __handle_constant_segment(self, index):
        return [f'@{index}', 'D=A', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1']

    def __handle_direct_address_segment(self, command, segment, index):
        lines = []
        
        if command == Parser.C_POP:
            lines.extend(['@SP', 'M=M-1', 'A=M', 'D=M'])
        
        if segment == 'temp':
            lines.append(f'@{int(index) + 5}')
        if segment == 'static':
            lines.append(f'@{self.__file_name}.{index}')
        if segment == 'pointer':
            if index == '0':
                lines.append('@THIS')
            elif index == '1':
                lines.append('@THAT')

        if command == Parser.C_POP:
            lines.extend(['M=D'])
        elif command == Parser.C_PUSH:
            lines.extend(['D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])

        return lines
    
    def __handle_base_address_segment(self, command, segment, index):
        lines = []
        
        if command == Parser.C_POP:
            lines.extend(['@SP', 'M=M-1', 'A=M', 'D=M'])
        
        segment_address = ''
        if segment == 'local':
            segment_address = 'LCL'
        if segment == 'argument':
            segment_address = 'ARG'
        if segment == 'this':
            segment_address = 'THIS'
        if segment == 'that':
            segment_address = 'THAT'

        if command == Parser.C_POP:
            lines.extend([ f'@{segment_address}', 'D=D+M', f'@{index}', 'D=D+A', '@SP', 'A=M', 'A=D-M', 'M=D-A'])
        elif command == Parser.C_PUSH:
            lines.extend([ f'@{segment_address}', 'D=M', f'@{index}', 'A=D+A', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'])

        return lines

    def write_arithmetic(self, command):
        lines=['@SP', 'M=M-1', 'A=M']
        
        if command == 'neg':
            lines.append('M=-M')
        elif command == 'not':
            lines.append('M=!M')
        else:
            lines.extend(['D=M', '@SP', 'M=M-1', 'A=M'])
            if command == 'add':
                lines.append('M=D+M')
            if command == 'sub':
                lines.append('M=M-D')
            if command == 'and':
                lines.append('M=D&M')
            if command == 'or':
                lines.append('M=D|M')
            if command in ['eq',  'gt', 'lt']:
                lines.extend(self.__handle_jumps(command))

        lines.extend(['@SP', 'M=M+1'])

        self.__file.writelines([line + '\n' for line in lines])

    def __handle_jumps(self, command):
        lines = []

        # get value to compare, overwrite top of the stack with -1 (as true)
        lines.extend(['D=M-D', '@SP',  'A=M', 'M=-1'])

        label = f'JUMP.{self.__jump_counter}'
        self.__jump_counter += 1

        lines.append(f'@{label}')

        if command == 'eq':
            lines.append('D;JEQ')
        if command == 'gt':
            lines.append('D;JGT')
        if command == 'lt':
            lines.append('D;JLT')

        # if true, skip overwriting with 0
        lines.extend(['@SP', 'A=M', 'M=0', f'({label})']) 

        return lines

    def write_label(self, label):
        line = f'({self.get_function_name()}${label})\n'
        self.__file.write(line)

    def write_go_to(self, label):
        lines = [f'@{self.get_function_name()}${label}', '0;JMP']
        self.__file.writelines([line + '\n' for line in lines])

    def write_if(self, label):
        lines = ['@SP', 'M=M-1', 'A=M', 'D=M', f'@{self.get_function_name()}${label}', 'D;JNE']
        self.__file.writelines([line + '\n' for line in lines])

    def write_function(self, function_name, n_vars):
        self.__is_defining_function = True
        lines = [f'({function_name})']
        self.__file.writelines([line + '\n' for line in lines])
        for _ in range(int(n_vars)):
            self.write_push_pop(Parser.C_PUSH, 'constant', '0')

    def write_call(self, function_name, n_args):
        return_label = f'{self.get_function_name()}$ret.{self.__return_counter}'
        self.__function_name.append(function_name)
        self.__return_counter += 1
        self.write_push_pop(Parser.C_PUSH, 'constant', return_label)

        lines = []
        for el in ['LCL', 'ARG', 'THIS', 'THAT']:
            lines.extend([ f'@{el}', 'D=M', '@SP', 'A=M', 'M=D', '@SP', 'M=M+1'] )

        lines.extend([f'@{int(n_args)+5}', 'D=A', '@SP', 'D=M-D', '@ARG', 'M=D'])
        lines.extend(['@SP', 'D=M', '@LCL', 'M=D'])
        lines.extend([f'@{function_name}', '0;JMP', f'({return_label})'])
        self.__file.writelines([line + '\n' for line in lines])

    def write_return(self):
        if not self.__is_defining_function:
            self.__function_name.pop()
        else:
            self.__is_defining_function = False
        
        lines = ['@LCL', 'D=M', '@R13', 'M=D'] # end_frame
        lines.extend(['@5', 'D=A', '@R13', 'A=M-D', 'D=M', '@R14', 'M=D']) # ret_address
        self.__file.writelines([line + '\n' for line in lines])

        self.write_push_pop(Parser.C_POP, "argument", 0)

        lines = ['@ARG', 'D=M', '@SP', 'M=D+1']
        lines.extend(['@R13', 'A=M-1', 'D=M', '@THAT', 'M=D'])
        lines.extend(['@2', 'D=A', '@R13', 'A=M-D', 'D=M', '@THIS', 'M=D'])
        lines.extend(['@3', 'D=A', '@R13', 'A=M-D', 'D=M', '@ARG', 'M=D'])
        lines.extend(['@4', 'D=A', '@R13', 'A=M-D', 'D=M', '@LCL', 'M=D'])
        lines.extend([f'@R14', 'A=M', '0;JMP'])

        self.__file.writelines([line + '\n' for line in lines])
