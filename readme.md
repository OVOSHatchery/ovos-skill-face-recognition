## skill-face-recognition

recognize user by face

## Description

- on face detect

        "user.detected", {"method": "face"}

- on face arrival

        "user.arrived", {"method": "face"}
        "user_departed", {"method": "face"}

- listens for face recognition request

        "face.recognize", {"file": "path/to/face.jpg"}

- listens for face recognition train

        "face.train", {"file": "path/to/face.jpg", "user": "jon do"}

- auto train new users faces
- automatic greetings - "Hello Joe", "Goodbye Joe"
- fully configurable
- only face encodings are saved, not pictures

## Examples
* "recognize my face"
* "my name is Jon Do"
* "my name is not Jon Do"

## TODO

- test install scripts
- optimize raspberry pi install

## Credits
JarbasAI