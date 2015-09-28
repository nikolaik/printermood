## Install
    pyenv venv
    . venv/bin/activate
    pip install -r requirements.txt
    python -m app.db  # creates db
    python -m app.run
    
    # Testing
    python -m app.tests

## TODO

- [ ] Capture image if motion and face is detected, per 3s
- [ ] Send image to Indico and save result
- [ ] On 5 faces with same emotion (confidence above ~0.4) set lightbulb state to specified color


## Colors
Confidence maps to light intensity

- sad = blue
- angry = red
- happy = green
- neutral = white
- surprise = pink
