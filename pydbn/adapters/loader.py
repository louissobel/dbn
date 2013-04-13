"""
the loader adapter
"""
import os
import os.path

import base_adapter

from tokenizer import DBNTokenizer
from parser import DBNParser
from compiler import DBNCompiler

class LoadAdapter(base_adapter.BaseAdapter):

    def __init__(self, cwd=None, search_path=None):
        """
        save the search path, blah blah blah
        """
        if cwd is None:
            cwd = os.getcwd()

        if search_path is None:
            search_path = []

        # TODO validate the search path (make sure all directories are real)
        search_path.insert(0, cwd)
        self.search_path = search_path

    def identifier(self):
        return 'loader'

    def find_file(self, filename):
        """
        will return the absolute filename, or None if it can't be found
        """
        if os.path.isabs(filename) and os.path.isfile(filename):
            return filename

        for directory in self.search_path:
            self.interpreter().debug("searching in %s" % directory)

            possible_file = os.path.join(directory, filename)
            if os.path.exists(possible_file) and os.path.isfile(possible_file):
                return possible_file
        return None

    def compile(self, filepath, offset):
        code_h = open(filepath, 'r')
        code = code_h.read()
        code_h.close()

        tokenizer = DBNTokenizer()
        parser = DBNParser()
        compiler = DBNCompiler(module=True)

        try:
            compilation = compiler.compile(parser.parse(tokenizer.tokenize(code)), offset=offset)
        except ValueError:
            raise RuntimeError('Error in loaded code')

        return compilation

    def load(self, filename, offset_pos, return_pos):
        """
        returns the compiled bytecodes of the given file
        """
        self.interpreter().debug("load being called (%s, %d, %d)" % (filename, offset_pos, return_pos))

        filepath = self.find_file(filename)
        if filepath is None:
            raise RuntimeError('Trying to load file %s, but cannot be found in %s' % (filename, str(self.search_path)))

        compilation = self.compile(filepath, offset_pos)
        return compilation.bytecodes + [('JUMP', return_pos)]
