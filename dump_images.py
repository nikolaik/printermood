import os
from config import *
from pymongo import MongoClient

client = MongoClient("mongodb://{host}:{port}".format(host=MONGO_HOST, port=MONGO_PORT))
db = client[MONGO_DBNAME]

IMAGE_COLLECTION = 'images'
IMAGE_DIR = 'imagedump'
images = db[IMAGE_COLLECTION].find()

for i in images:
    mime_type = i['mime_type']
    if type(mime_type) == bytes:
        mime_type = mime_type.decode('ascii')

    file_name = '{}.jpg'.format(i['_id'])
    img = i['file']
    with open(os.path.join(IMAGE_DIR, file_name), 'wb') as f:
        n = f.write(img)

    print("Wrote {} bytes to {}".format(n, file_name))
