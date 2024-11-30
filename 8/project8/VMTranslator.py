import os
import sys

import Parser
from CodeWriter import CodeWriter

def main():
    input = sys.argv[1]
    output = input.replace('vm', 'asm') if input.endswith('.vm') else f"{os.path.join(input, os.path.basename(input))}.asm"
    code_writer = CodeWriter(output)

    if input.endswith('.vm'): 
        translate_file(input, code_writer)
    else:
        for file_name in os.listdir(input):
            if file_name.endswith('.vm'): 
                code_writer.bootstrap()
                translate_file(os.path.join(input, file_name), code_writer)
        
    code_writer.close()


def translate_file(file_name, code_writer):
    parser = Parser.Parser(file_name)
    code_writer.set_file_name(file_name.replace('.vm', ''))

    while parser.has_more_lines():
        parser.advance()

        type = parser.command_type()
        if type == Parser.C_ARITHMETIC:
            code_writer.write_arithmetic(parser.arg1())
        elif type == Parser.C_POP or type == Parser.C_PUSH:
            code_writer.write_push_pop(type, parser.arg1(), parser.arg2())
        elif type == Parser.C_LABEL:
            code_writer.write_label(parser.arg1())
        elif type == Parser.C_GOTO:
            code_writer.write_go_to(parser.arg1())
        elif type == Parser.C_IF:
            code_writer.write_if(parser.arg1())
        elif type == Parser.C_FUNCTION:
            code_writer.write_function(parser.arg1(), parser.arg2())
        elif type == Parser.C_CALL:
            code_writer.write_call(parser.arg1(), parser.arg2())
        elif type == Parser.C_RETURN:
            code_writer.write_return()


if __name__ == '__main__':
    main()
