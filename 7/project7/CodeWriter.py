import os

import Parser

class CodeWriter:
    def __init__(self, file_name):
        self.__file = open(file_name, 'w')
        self.__file_name = os.path.basename(file_name).replace('.asm', '')
        self.__jump_counter = 0

    def write_push_pop(self, command, segment, index):
        lines=[]

        if segment == 'constant':
            lines = self.__handle_constant_segment(index)
        elif segment in ['static', 'temp',  'pointer']:
            lines = self.__handle_direct_address_segment(command, segment, index)
        elif segment in ['local', 'argument', 'this', 'that']:
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
            if command in ['eq', 'gt', 'lt']:
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
    
    def close(self):
        return self.__file.close()
