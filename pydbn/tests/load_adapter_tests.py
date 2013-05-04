import unittest
import os
import os.path
import shutil

from interpreter.adapters.loader import LoadAdapter, PATH_ENV_VAR

LOADED_DBN = """
Set A 0
"""

LOADED_DBN_FILENAME = "test_load.dbn"
PERMERROR_DBN_FILENAME = "test_permerror.dbn"

ERROR_DBN = """
. 38 ? +
"""

ERROR_DBN_FILENAME = "test_error.dbn"

EXPECTED_BYTECODE = [
    ('LOAD_INTEGER', '0'),
    ('STORE', 'A'),
]

FIRST_SUB_DIR = os.path.abspath('load_adapter_test_dir')
SECOND_SUB_DIR = os.path.abspath('another_load_adapter_test_dir')

FIRST_DIR_FILENAME = 'first_dir_load.dbn'
SECOND_DIR_FILENAME = 'second_dir_load.dbn'

LOAD_NOT_FILENAME = 'i_dont_exist.dbn'

class LoadAdapterTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        self.addCleanup(self.cleanUp)

    def setUp(self):
        """
        Do set up
        """
        self.actual_cwd = os.getcwd()
        os.mkdir(FIRST_SUB_DIR)
        os.mkdir(SECOND_SUB_DIR)

        # write the test loadable file in each dir
        for subdir, filename in zip((FIRST_SUB_DIR, SECOND_SUB_DIR), (FIRST_DIR_FILENAME, SECOND_DIR_FILENAME)):
            path = os.path.join(self.actual_cwd, subdir, filename)
            file_h = open(path, 'w')
            file_h.write(LOADED_DBN)
            file_h.close()

        # write some test files in this directory
        for filename, content in zip((LOADED_DBN_FILENAME, PERMERROR_DBN_FILENAME, ERROR_DBN_FILENAME), (LOADED_DBN, LOADED_DBN, ERROR_DBN)):
            file_h = open(filename, 'w')
            file_h.write(content)
            file_h.close()

        # fuck with the permissions on PERMERROR
        os.chmod(PERMERROR_DBN_FILENAME, 0)

        # set the environment variable
        os.environ[PATH_ENV_VAR] = os.pathsep.join((FIRST_SUB_DIR, SECOND_SUB_DIR))

        # and of course, initialize the loader (to a default one)
        self.loader = LoadAdapter()

    def cleanUp(self):
        """
        delete the directories
        """
        for subdir in (FIRST_SUB_DIR, SECOND_SUB_DIR):
            shutil.rmtree(os.path.join(self.actual_cwd, subdir))

        for filename in (LOADED_DBN_FILENAME, PERMERROR_DBN_FILENAME, ERROR_DBN_FILENAME):
            os.unlink(filename)

## test tests
class TestSetupTearDown(LoadAdapterTestCase):
    def runTest(self):
        pass

## __init__ tests
class TestInitDefaultCwdHandling(LoadAdapterTestCase):
    """
    If cwd is not provided, it should act like it is None, and insert it at start
    """
    def runTest(self):
        self.assertEqual(self.actual_cwd, self.loader.search_path[0])

class TestInitCwdNoneHandling(LoadAdapterTestCase):
    """
    if arg cwd is set to None, then it should get it and insert it
    """
    def runTest(self):
        loader = LoadAdapter(cwd=None)
        self.assertEqual(self.actual_cwd, loader.search_path[0])

class TestInitCwdFalseHandling(LoadAdapterTestCase):
    """
    if arg cwd is False, it should __not__ be inserted into search path
    """
    def runTest(self):
        loader = LoadAdapter(cwd=False)
        self.assertNotEqual(self.actual_cwd, loader.search_path[0])

class TestInitCwdCustomHandling(LoadAdapterTestCase):
    """
    if a cwd is provided, it should be inserted into search path
    """
    def runTest(self):
        CUSTOM_DIR = '/'
        loader = LoadAdapter(cwd=CUSTOM_DIR)
        self.assertEqual(CUSTOM_DIR, loader.search_path[0])

class TestInitEnvVarHandling(LoadAdapterTestCase):
    """
    should use the environment variable to fill out the path
    """
    def runTest(self):
        loader = LoadAdapter(cwd=False)
        self.assertEqual([FIRST_SUB_DIR, SECOND_SUB_DIR], loader.search_path)

class TestInitCheckEnvFalseHandling(LoadAdapterTestCase):
    """
    if check env is false, should not grab from the environment variables
    """
    def runTest(self):
        loader = LoadAdapter(cwd=False, check_env=False)
        self.assertEqual([], loader.search_path)

class TestInitEmptyEnvVar(LoadAdapterTestCase):
    """
    if envar is empty, we should be OK
    """
    def runTest(self):
        os.environ[PATH_ENV_VAR] = ""
        loader = LoadAdapter(cwd=False)
        self.assertEqual([], loader.search_path)

class TestInitNoEnvVar(LoadAdapterTestCase):
    """
    if the envvar is not set, we shouldbe OK
    """
    def runTest(self):
        del os.environ[PATH_ENV_VAR]
        loader = LoadAdapter(cwd=False)
        self.assertEqual([], loader.search_path)

class TestCustomSearchPath(LoadAdapterTestCase):
    """
    should be able to set custom search path
    """
    def runTest(self):
        CUSTOM_PATH = ['/']
        loader = LoadAdapter(cwd=False, check_env=False, search_path=CUSTOM_PATH)
        self.assertEqual(CUSTOM_PATH, loader.search_path)

        # it should copy it so it is mutate safe
        old_custom_path = CUSTOM_PATH[:]
        CUSTOM_PATH.append('bloop')
        self.assertEqual(old_custom_path, loader.search_path)

class TestCustomSearchPathPosition(LoadAdapterTestCase):
    """
    custom search path should be between CWD and env vars
    """
    def runTest(self):
        CUSTOM_PATH = ['/']
        loader = LoadAdapter(search_path=CUSTOM_PATH)
        self.assertEqual([self.actual_cwd] + CUSTOM_PATH + [FIRST_SUB_DIR, SECOND_SUB_DIR], loader.search_path)

class TestBadDirThrowsValueError(LoadAdapterTestCase):
    """
    if we provide something that does not exist or is not direcotry, should throw value error
    """
    def runTest(self):
        MADE_UP = ['/dlfjsdlkfjsdlkfjsdlk']
        with self.assertRaises(ValueError):
            loader = LoadAdapter(search_path=MADE_UP)

        NOT_DIRECTORY = [os.path.join(self.actual_cwd, LOADED_DBN_FILENAME)]
        with self.assertRaises(ValueError):
            loader = LoadAdapter(search_path=NOT_DIRECTORY)

class TestNonAbsPathThrowsValueError(LoadAdapterTestCase):
    """
    non abs path should throw error
    """
    def runTest(self):
        NON_ABS = [os.path.basename(FIRST_SUB_DIR)]
        with self.assertRaises(ValueError):
            loader = LoadAdapter(search_path=NON_ABS)

## identifier tests
class TestIdentifier(LoadAdapterTestCase):
    """
    identifier should be 'loader'
    """
    def runTest(self):
        self.assertEqual('loader', self.loader.identifier())

## find_file tests
class TestFindAbsoluteFile(LoadAdapterTestCase):
    """
    should find an absolute filename, returning the filename
    """
    def runTest(self):
        PATH = os.path.join(self.actual_cwd, LOADED_DBN_FILENAME)
        self.assertEqual(PATH, self.loader.find_file(PATH))

class TestFindNonExistingAbsoluteFile(LoadAdapterTestCase):
    """
    should return None if the absolute file does not exist
    """
    def runTest(self):
        PATH = os.path.join(self.actual_cwd, LOAD_NOT_FILENAME)
        self.assertIsNone(self.loader.find_file(PATH))

class TestFindNonExistingAbsoluteFileThatExistsRelatively(LoadAdapterTestCase):
    """
    if an absolute path does not exist but it would exist relatively,
    should still return None
    (regression)
    """
    def runTest(self):
        PATH = os.path.join('/', LOADED_DBN_FILENAME)
        self.assertIsNone(self.loader.find_file(PATH))

class TestFindExistingRelativeFile(LoadAdapterTestCase):
    """
    should find and return absolute path of relative filename
    """
    def runTest(self):
        ABS_PATH = os.path.join(self.actual_cwd, SECOND_SUB_DIR, SECOND_DIR_FILENAME)
        self.assertEqual(ABS_PATH, self.loader.find_file(SECOND_DIR_FILENAME))

class TestFindExistingRelativePath(LoadAdapterTestCase):
    """
    should find a relative path
    Load a/b
    """
    def runTest(self):
        FILE_PATH = os.path.join(os.path.basename(SECOND_SUB_DIR), SECOND_DIR_FILENAME)
        ABS_PATH = os.path.join(self.actual_cwd, SECOND_SUB_DIR, SECOND_DIR_FILENAME)
        self.assertEqual(ABS_PATH, self.loader.find_file(FILE_PATH))

class TestFindNonExistingPath(LoadAdapterTestCase):
    """
    return should return for a file that does not exist
    """
    def runTest(self):
        self.assertIsNone(self.loader.find_file(LOAD_NOT_FILENAME))

## compile tests
class TestCompileExistingFile(LoadAdapterTestCase):
    """
    we should compile a filepath - not here to test the compiler though
    """
    def runTest(self):
        FILE_PATH = os.path.join(self.actual_cwd, LOADED_DBN_FILENAME)
        OFFSET = 7
        compilation = self.loader.compile(FILE_PATH, OFFSET)
        self.assertEquals(OFFSET + 2, compilation.counter)
        self.assertEquals(EXPECTED_BYTECODE, compilation.bytecodes)

class TestCompileReadError(LoadAdapterTestCase):
    """
    when there is a error opening the file, it should throw runtime error
    """
    def runTest(self):
        FILE_PATH = os.path.join(self.actual_cwd, PERMERROR_DBN_FILENAME)
        with self.assertRaises(RuntimeError):
            self.loader.compile(FILE_PATH, 0)

class TestCompileCodeError(LoadAdapterTestCase):
    """
    when there is an error in the loaded code, should raise runtime error
    """
    def runTest(self):
        FILE_PATH = os.path.join(self.actual_cwd, ERROR_DBN_FILENAME)
        with self.assertRaises(RuntimeError):
            self.loader.compile(FILE_PATH, 0)

## load tests
class TestLoad(LoadAdapterTestCase):
    """
    should load and return bytecode
    """
    def runTest(self):
        RETURN_POS = 8
        OFFSET = 10
        THIS_EXPECTED_BYTECODE = EXPECTED_BYTECODE + [('JUMP', '8')]

        result = self.loader.load(LOADED_DBN_FILENAME, OFFSET, RETURN_POS)
        self.assertEquals(THIS_EXPECTED_BYTECODE, result)

class TestLoadFileNotFound(LoadAdapterTestCase):
    """
    should raise runtime error if a file does not exist
    """
    def runTest(self):
        with self.assertRaises(RuntimeError):
            self.loader.load(LOAD_NOT_FILENAME, 0, 0)

class TestDuplicateLoad(LoadAdapterTestCase):
    """
    should raise runtime error if you try to load the same file twice
    """
    def runTest(self):
        self.loader.load(LOADED_DBN_FILENAME, 0, 0)
        with self.assertRaises(RuntimeError):
            self.loader.load(LOADED_DBN_FILENAME, 0, 0)

if __name__ == "__main__":
    unittest.main()
