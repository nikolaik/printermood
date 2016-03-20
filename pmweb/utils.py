import base64

import magic


def top_emotion(emotions):
    if type(emotions) != dict or len(emotions) == 0:
        return None

    return sorted(emotions.items(), key=lambda x: x[1], reverse=True)[0]


def get_mime_type(image_data):
    return magic.from_buffer(image_data, mime=True).decode('ascii')


def get_data_url(image):
    return 'data:{};base64,{}'.format(
        image['mime_type'],
        base64.b64encode(image['file']).decode('ascii'))
