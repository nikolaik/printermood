import unittest

from app.db import get_db_session
from app.indico_api import get_emotions
from app.lifx_api import get_lights
from app.models import Light


class TestAllTheThings(unittest.TestCase):
    def test_get_lights(self):
        s = get_db_session()
        light = s.query(Light).all()[:1]
        self.assertIsNotNone(light)

    @unittest.skip('invalid token, fix tomorrow')
    def test_lifx_get_lights(self):
        lights = get_lights()
        self.assertIsNotNone(lights)

    @unittest.skip('api')
    def test_indico_api(self):
        filepath = 'data/not_nice_n.png'
        get_emotions(filepath)


if __name__ == '__main__':
    unittest.main()
