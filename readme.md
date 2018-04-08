## skill-face-recognition

recognize user by face

## Description

- on face detect - emits "user_detection.face" messages
- on face arrival - emits "user_arrival.face" and "user_departure.face" messages
- listens for face recognition request messages "face_recognition.request"
- listens for face recognition train request messages "face_recognition_train.request"
- auto train new users faces
- automatic greetings - "Hello Joe", "Goodbye Joe"
- fully configurable
- only face encodings are saved, not pictures

## Examples
* "recognize my face"
* "my name is Jon Do"
* "my name is not Jon Do"

## TODO

- settingsmeta.json
- test install scripts
- optimize raspberry pi install

## Credits
JarbasAI