import os
import sys

from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine

def main():
    input = sys.argv[1]

    if input.endswith('.jack'): 
        analyze_file(input, input.replace('jack', 'xml'))
    else:
        for file_name in os.listdir(input):
            if file_name.endswith('.jack'): 
                analyze_file(os.path.join(input, file_name), f"{os.path.join(input, file_name.replace('jack', 'xml'))}")


def analyze_file(input_file_name, output_file_name):
    tokenizer = JackTokenizer(input_file_name)

    with open(output_file_name, 'w') as output_file:
        compilation_engine = CompilationEngine(tokenizer, output_file)
        compilation_engine.compile_class()


if __name__ == '__main__':
    main()
