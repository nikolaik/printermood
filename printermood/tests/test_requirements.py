import unittest


class RequirementsTestCase(unittest.TestCase):
    def test_opencv(self):
        try:
            import cv2
            assert cv2.__version__ is not None
        except ImportError:
            self.fail('OpenCV not installed!')

    def test_dlib(self):
        try:
            import dlib
            assert dlib.__version__ is not None
        except ImportError:
            self.fail('Dlib not installed!')


if __name__ == "__main__":
    unittest.main()

