import sys

import Parser
from CodeWriter import CodeWriter

def main():
  parser = Parser.Parser(sys.argv[1])
  code_writer = CodeWriter(sys.argv[1].replace('vm', 'asm'))

  while parser.has_more_lines():
    parser.advance()

    type = parser.command_type()
    if type == Parser.C_ARITHMETIC:
      code_writer.write_arithmetic(parser.arg1())
    elif type == Parser.C_POP or type == Parser.C_PUSH:
      code_writer.write_push_pop(type, parser.arg1(), parser.arg2())
    
  code_writer.close()


if __name__ == '__main__':
    main()
