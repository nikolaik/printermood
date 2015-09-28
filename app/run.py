from app.db import get_db_session
from app.models import Light

session = get_db_session()
print("Syncing lights")
Light.sync_lights()

while True:
    try:
        # FIXME: Something else here
        res = input("Are you here?")
        lights = session.query(Light).all()
        print(lights)
    except KeyboardInterrupt:
        print()
        exit(0)
