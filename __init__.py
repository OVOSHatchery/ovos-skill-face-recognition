import face_recognition
import os
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message


__author__ = 'jarbas'


class FaceRecService(MycroftSkill):

    def __init__(self):
        super(FaceRecService, self).__init__(name="FaceRecogSkill")
        self.reload_skill = False
        self.known_faces = {}
        # load known faces
        faces = os.listdir(os.path.dirname(__file__) + "/known faces")
        # Load the jpg files into numpy arrays
        for face in faces:
            # Get the face encodings for each face in each image file
            # Since there could be more than one face in each image, it returns a list of encordings.
            # But since i assume each image only has one face, I only care about the first encoding in each image, so I grab index 0.
            self.log.info("loading face encodings for " + face)
            self.known_faces[face] = face_recognition.face_encodings(face_recognition.load_image_file(os.path.dirname(__file__) + "/known faces/" + face))[0]

    def initialize(self):
        self.emitter.on("face_recognition_request", self.handle_recog)

    def handle_recog(self, message):
        face = message.data.get("file")
        user_id = message.data.get("source")
        self.log.info(user_id + " request facerecog for " + face)
        if user_id is not None:
            if user_id == "unknown":
                user_id = "all"
            self.target = user_id
        else:
            self.log.warning("no user/target specified")
            user_id = "all"

        result = None
        # read unknown image
        self.log.info("loading unknown image")
        unknown_image = face_recognition.load_image_file(face)
        self.log.info("getting face encodings of unknown image")
        encoding = face_recognition.face_encodings(unknown_image)[0]
        # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
        for person in self.known_faces.keys():
            self.log.info("comparing to person " + person)
            # check if unknown person is this face, by comparing face encodings
            match = face_recognition.compare_faces([self.known_faces[person]], encoding)
            print match
            if match:
                result = person.replace(".jpg", "")
                self.log.info("match found, unknown image is " + result)
                break

        self.speak(result)

        self.emitter.emit(Message("message_request",
                                  {"user_id": user_id, "data": {"result": result}, "type": "face_recognition_result"}))

    def stop(self):
        pass


def create_skill():
    return FaceRecService()
