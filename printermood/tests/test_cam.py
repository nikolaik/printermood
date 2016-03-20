from ..cam import ImageLocation
import cv2
import os
import unittest


class ImageLocationTest(unittest.TestCase):
    def setUp(self):
        self.image_path = 'printermood/tests/images/'

    def test_bottle_sharpness(self):
        image_sharp = self._open_image('bottle_sharp.jpg')
        image_blurred = self._open_image('bottle_blurred.jpg')

        face_location_sharp = ImageLocation(
            image_sharp,
            (0, 0, image_sharp.shape[1], image_sharp.shape[0])
        )
        face_location_blurred = ImageLocation(
            image_blurred,
            (0, 0, image_blurred.shape[1], image_blurred.shape[0])
        )

        assert face_location_sharp.sharpness > face_location_blurred.sharpness

    def _open_image(self, filename):
        path = os.path.join(self.image_path, filename)
        image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)

        assert image is not None
        return image
