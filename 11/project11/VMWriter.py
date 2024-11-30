class VMWriter:
    def __init__(self, file_name):
        self.__file = open(file_name, 'w')

    def write_push(self, segment, index):
        self.__file.writelines([f'push {segment.lower()} {index}\n'])

    def write_pop(self, segment, index):
        self.__file.writelines([f'pop {segment.lower()} {index}\n'])

    def write_arithmetic(self, command):
        self.__file.writelines([f'{command.lower()}\n'])

    def write_label(self, label):
        self.__file.writelines([f'label {label}\n'])

    def write_goto(self, label):
        self.__file.writelines([f'goto {label}\n'])

    def write_if(self, label):
        self.__file.writelines([f'if-goto {label}\n'])

    def write_call(self, name, n_args):
        self.__file.writelines([f'call {name} {n_args}\n'])

    def write_function(self, name, n_vars):
        self.__file.writelines([f'function {name} {n_vars}\n'])

    def write_return(self):
        self.__file.writelines(['return\n'])

    def close(self):
        self.__file.close()
