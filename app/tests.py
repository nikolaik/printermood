import os
import unittest

from app.db import get_db_session
from app.indico_api import get_emotions
from app.lifx_api import get_lights
from app.models import Light
from app.utils import top_emotion


class TestAllTheThings(unittest.TestCase):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        filepath = os.path.join(self.BASE_DIR, 'app/data/not_nice_n.png')
        emotions = get_emotions(filepath)
        self.assertEquals(type(emotions), dict)
        self.assertIn('Neutral', emotions.keys())

    def test_emotion_significant(self):
        emotions = {
            'Surprise': 0.024324588796592172,
            'Happy': 0.3476816111891204,
            'Sad': 0.24464429503898413,
            'Fear': 0.04976541788382526,
            'Neutral': 0.24602374210010866,
            'Angry': 0.08756034499136953
        }
        t = top_emotion(emotions)
        self.assertTrue(t == ('Happy', emotions.get('Happy')))
        self.assertTrue(t[1] > 0.25)


if __name__ == '__main__':
    unittest.main()
