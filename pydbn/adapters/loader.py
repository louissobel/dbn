"""
the loader adapter
"""
import os
import os.path

from tokenizer import DBNTokenizer
from parser import DBNParser
from compiler import DBNCompiler
import base_adapter

# TODO prevent circular imports

PATH_ENV_VAR = 'DBN_LOAD_PATH'

class LoadAdapter(base_adapter.BaseAdapter):
    """
    The adapter responsible for searching for and compiling and `Load`ed files
    """

    def __init__(self, cwd=None, search_path=None, check_env=True):
        """
        save the search path

        cwd can be prevented from being added to search path by passing False

        will check env var
        """
        if cwd is None:
            cwd = os.getcwd()

        if search_path is None:
            search_path = []

        # TODO validate the search path (make sure all directories are real)
        if not cwd is False:
            search_path.insert(0, cwd)

        # check the set env var for more paths
        env_var = os.environ.get(PATH_ENV_VAR)
        if env_var:
            search_path.extend(env_var.split(os.path.pathsep))
        
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
            if os.path.isfile(possible_file):
                return possible_file

        return None

    def compile(self, filepath, offset):
        """
        Reads and compiles the given file at the given offset (the offset is for the compiler)
        """
        try:
            code_h = open(filepath, 'r')
        except OSError as e:
            raise RuntimeError('Problem loading file %s: %s' % (filepath, str(e)))

        code = code_h.read()
        code_h.close()

        tokenizer = DBNTokenizer()
        parser = DBNParser()
        compiler = DBNCompiler(module=True)

        try:
            compilation = compiler.compile(parser.parse(tokenizer.tokenize(code)), offset=offset)
        except ValueError:
            # This is a little hairy. Correct, but be wary.
            raise RuntimeError('Error in loaded code')

        return compilation

    def load(self, filename, offset_pos, return_pos):
        """
        returns the compiled bytecodes of the given file

        adds a `JUMP` byte code with a target to the given return_pos
        this allows the interpreter to jump to the start of this code,
        then get sent back to the correct place
        """
        self.interpreter().debug("load being called (%s, %d, %d)" % (filename, offset_pos, return_pos))

        filepath = self.find_file(filename)
        if filepath is None:
            raise RuntimeError('Trying to load file %s, but cannot be found in %s' % (filename, str(self.search_path)))

        compilation = self.compile(filepath, offset_pos)

        # add the jump for the interpreter
        return compilation.bytecodes + [('JUMP', return_pos)]
