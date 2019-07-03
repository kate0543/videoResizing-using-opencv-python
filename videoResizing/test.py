import unittest
from unittest import TestCase
import main


# tests for the gui file
class TestResizer(TestCase):
    """
    this is the test class for the main.py
    """
    def test_getVideosPath(self):
        main.Resizer.getVideosPath(self)

    def test_startResizing(self):
        main.Resizer.startResizing(self)

    def test_startMultiResizing(self):
        main.Resizer.startResizing(self)

    def test_Results(self):
        main.Resizer.Results(self)

if __name__ == '__main__':
    unittest.main()