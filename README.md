Match the light in your printer room with how the user feels

![Image of printermood dashboard](screenshot.png)
 
## Install
    apt install mongo-server python3-venv python3-dev
    # pillow deps
    pyenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    python run.py
    
    # Frontend
    cd printermood/static
    npm install
    npm install -g webpack
    npm start  # to build/package frontend stuff

    # Testing
    python -m printermood.tests

## TODO

- [ ] Capture image if motion and face is detected, per 3s
- [ ] Send image to Indico and save result
- [ ] On 5 faces with same emotion (confidence above ~0.4) set lightbulb state to specified color


# Models

- User: name
- LIFXLight: name, power_state, id, ...
- Faces: image data, timestamp, metadata, url
- Mood: user_id, name, face_id


## Colors
Confidence maps to light intensity

- sad = blue
- angry = red
- happy = green
- neutral = white
- surprise = pink
