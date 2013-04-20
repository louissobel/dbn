import os
import unittest

from dbn import run_dbn, compile_dbn
import output

directory = os.path.dirname(__file__)

test_cases = [os.path.join(directory, d) for d in os.listdir(directory) if not (d.startswith('.') or d.startswith('_'))]

PATH_ENV_VAR = 'DBN_LOAD_PATH'

# assume each subdir has code.dbn and expected.bmp

class ImageMatchTestCase():
  
  def get_actual(self):

    terp = run_dbn(compile_dbn(self.directory + '/code.dbn'))
    
    outFile = self.directory + '/actual.bmp'
    output.output_png(terp, outFile)
    return open(outFile, 'rb').read()
    

  def runTest(self):
    os.environ[PATH_ENV_VAR] = self.directory

    actual = self.get_actual()
    expected = open(self.directory + '/expected.bmp', 'rb').read()
    
    self.assertEqual(actual, expected)

    # this happens if it passes
    os.remove(self.directory + '/actual.bmp')
    

for test_case in test_cases:
  class_name = 'ImageMatchTestCase_%s' % test_case
  locals()[class_name] = type(class_name, (unittest.TestCase, ImageMatchTestCase), {'directory': test_case})

if __name__ == "__main__":
  unittest.main()
  