import unittest

from interpreter.structures.frame import DBNFrame


class FrameUnitTest(unittest.TestCase):
    pass

class TestFrameInitDefaults(FrameUnitTest):

    def runTest(self):
        frame = DBNFrame()

        self.assertEqual(frame.base_line_no, -1)
        self.assertIsNone(frame.parent)
        self.assertEqual(frame.return_pointer, -1)
        self.assertEqual(frame.depth, 0)

        self.assertEqual(frame.env, {})
        self.assertEqual(frame.stack, [])


class TestFrameInit(FrameUnitTest):

    def runTest(self):
        frame = DBNFrame(base_line_no=100, parent=98, return_pointer=-2143, depth=986)

        self.assertEqual(frame.base_line_no, 100)
        self.assertEqual(frame.parent, 98)
        self.assertEqual(frame.return_pointer, -2143)
        self.assertEqual(frame.depth, 986)

        self.assertEqual(frame.env, {})
        self.assertEqual(frame.stack, [])


class SimpleBindAndLookupTest(FrameUnitTest):

    def runTest(self):
        frame = DBNFrame()
        frame.bind_variable('HI', 900)
        self.assertEqual(frame.lookup_variable('HI'), 900)


class LookupTestNotFound(FrameUnitTest):

    def runTest(self):
        frame = DBNFrame()
        self.assertIsNone(frame.lookup_variable('DFSFD'))


class LookupTestNotFoundDeafault(FrameUnitTest):

    def runTest(self):
        frame = DBNFrame()
        self.assertEqual(frame.lookup_variable('KJLKJ', 87), 87)


class LookupTestWithBindInParent(FrameUnitTest):

    def runTest(self):
        parent = DBNFrame()
        frame = DBNFrame(parent=parent)

        parent.bind_variable('hi', 65)
        self.assertEqual(frame.lookup_variable('hi'), 65)


class LookupNotFoundWithParent(FrameUnitTest):

    def runTest(self):
        parent = DBNFrame()
        frame = DBNFrame(parent=parent)
        self.assertIsNone(frame.lookup_variable('KK'))


class LookupNotFoundWithParentAndDefault(FrameUnitTest):

    def runTest(self):
        parent = DBNFrame()
        frame = DBNFrame(parent=parent)
        self.assertEqual(frame.lookup_variable('KLKLK', 57), 57)


class LookupWithLotsOfParents(FrameUnitTest):

    def runTest(self):
        root = DBNFrame()
        root.bind_variable('THERE', 9)

        base = root
        for i in range(100):
            base = DBNFrame(parent=base)

        self.assertEqual(base.lookup_variable('THERE'), 9)


class BindVariablesTest(FrameUnitTest):

    def runTest(self):
        frame = DBNFrame()
        frame.bind_variables(h=9, b=28)
        self.assertEqual(frame.lookup_variable('h'), 9)
        self.assertEqual(frame.lookup_variable('b'), 28)


if __name__ == "__main__":
    unittest.main()
