## skill-face-recognition
[![Donate with Bitcoin](https://en.cryptobadges.io/badge/micro/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)](https://en.cryptobadges.io/donate/1QJNhKM8tVv62XSUrST2vnaMXh5ADSyYP8)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://paypal.me/jarbasai)
<span class="badge-patreon"><a href="https://www.patreon.com/jarbasAI" title="Donate to this project using Patreon"><img src="https://img.shields.io/badge/patreon-donate-yellow.svg" alt="Patreon donate button" /></a></span>
[![Say Thanks!](https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg)](https://saythanks.io/to/JarbasAl)

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
