import unittest
import os
import os.path
import shutil

from adapters.loader import LoadAdapter, PATH_ENV_VAR

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

FIRST_SUB_DIR = 'load_adapter_test_dir'
SECOND_SUB_DIR = 'another_load_adapter_test_dir'

FIRST_DIR_FILENAME = 'first_dir_load.dbn'
SECOND_DIR_FILENAME = 'second_dir_load.dbn'

LOAD_NOT_FILENAME = 'i_dont_exist.dbn'

class LoadAdapterTestCase(unittest.TestCase):

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

    def tearDown(self):
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
        MADE_UP = ['dlfjsdlkfjsdlkfjsdlk']
        with self.assertRaises(ValueError):
            loader = LoadAdapter(search_path=MADE_UP)

        NOT_DIRECTORY = [LOADED_DBN_FILENAME]
        with self.assertRaises(ValueError):
            loader = LoadAdapter(search_path=NOT_DIRECTORY)

## identifier tests
class TestIdentifier(LoadAdapterTestCase):
    """
    identifier should be 'loader'
    """
    def runTest(self):
        self.assertEqual('loader', self.loader.identifier())

## find_file tests
# abs file - existing and non-existing, non-existing but existing relatively!
# relative file - top level, in a directory, in another directory!

## compile
# everything OK
# offset should set
# permission error.. runtime
# value error.. runtime

## load
# everything ok (adds the JUMP!)
# nonexisting file.. runtime
# duplicate load.. runtime


if __name__ == "__main__":
    unittest.main()
