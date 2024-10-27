__copyright__ = "Copyright (c) 2024 Jeff Sawatzky"
__license__ = "MIT"

from amazonorders.util import to_type
from tests.unittestcase import UnitTestCase


class TestSession(UnitTestCase):
    def test_to_type(self):
        self.assertEqual(to_type(None), None)

        self.assertEqual(to_type("0.0"), 0.0)
        self.assertEqual(to_type("0.1"), 0.1)
        self.assertEqual(to_type("0"), 0)
        self.assertEqual(to_type("1.0"), 1.0)
        self.assertEqual(to_type("1.1"), 1.1)
        self.assertEqual(to_type("1"), 1)

        self.assertEqual(to_type("True"), True)
        self.assertEqual(to_type("False"), False)

        self.assertEqual(to_type(""), None)
        self.assertEqual(to_type(" "), " ")
        self.assertEqual(to_type("None"), "None")