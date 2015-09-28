from indicoio import fer

from app.settings import INDICO_API_KEY


def get_emotions(face):
    # import numpy as np
    # face = np.zeros((48, 48)).tolist()
    emotions = fer(face, api_key=INDICO_API_KEY)
    return emotions

