import face_recognition
from os import remove
from os.path import join, dirname
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
import pickle
from shared_camera import Camera

__author__ = 'jarbas'


class FaceRecognition(MycroftSkill):

    def __init__(self):
        super(FaceRecognition, self).__init__(name="FaceRecogSkill")
        self.reload_skill = False
        # TODO use other dir and allow reload
        self.known_faces = {}
        # TODO use skill settings
        self.model = join(dirname(dirname(__file__)), "encodings.fr")
        self.sensitivity = 0.5
        self.load_encodings()
        LOG.info("Local Face recognition engine started")
        self.camera = Camera()

    def initialize(self):
        self.add_event("face_recognition_request", self.handle_recognition_request)

    def get_encodings(self, picture_path):
        # Load the image file
        img = face_recognition.load_image_file(picture_path)
        # Get face encodings for any faces in the uploaded image
        encodings = face_recognition.face_encodings(img)
        if len(encodings):
            return encodings[0]
        else:
            return None

    def recognize_encodings(self, picture_path, known_encodings=None):
        known_encodings = known_encodings or self.known_faces
        # Load the uploaded image file
        img = face_recognition.load_image_file(picture_path)
        # Get face encodings for any faces in the uploaded image
        unknown_face_encodings = face_recognition.face_encodings(img)

        face_found = False
        recognized = False
        person = "None"
        predictions = {}
        top_score = 0
        if len(unknown_face_encodings) > 0:
            face_found = True
            if len(known_encodings.keys()):
                known_enc = [known_encodings[enc] for enc in known_encodings]
                # See if the first face in the image matches the known face
                face_distances = face_recognition.face_distance(
                    known_enc, unknown_face_encodings[0])
                person = "unknown"
                for i, face_distance in enumerate(face_distances):
                    name = known_encodings.keys()[i]
                    score = 1 - face_distance
                    if top_score < score:
                        top_score = score
                        if score > self.sensitivity:
                            person = name
                            recognized = True
                    predictions[name] = score

        # Return the result as json
        result = {
            "face_found_in_image": face_found,
            "recognized": recognized,
            "person": person,
            "score": top_score,
            "predictions": predictions
        }
        if not len(known_encodings.keys()):
            result["error"] = "no known users available"
        return result

    def load_encodings(self):
        try:
            with open(self.model, "r") as f:
                self.known_faces = pickle.load(f)
        except Exception as e:
            LOG.warning(e)

    def train_user(self, user, picture_path):
        if user in self.known_faces.keys():
            res = {"success": True,
                   "warning": "user already registered",
                   "user": user}
        else:
            res = {"success": True,
                   "user": user}
            try:
                self.known_faces[user] = self.get_encodings(picture_path)
                with open(self.model, "w") as f:
                    pickle.dump(self.known_faces, f)
            except Exception as e:
                res = {"success": False,
                       "error": "could not save face encodings",
                       "exception": str(e)}
        remove(picture_path)
        return res

    def handle_recognition_request(self, message):
        face = message.data.get("file")
        result = self.recognize_encodings(face)
        # emit result to internal bus
        self.emitter.emit(Message("face_recognition_result",
                                  {"result": result}))

    @intent_handler(IntentBuilder("recognize_face")
                    .require("recognize_my_face.voc"))
    def handle_recognize_my_face(self, message):
        frame = self.camera.get()
        if frame is None:
            self.speak_dialog("camera.error")
        else:
            # TODO use filesystem access instead
            pic = join(dirname(__file__), "tmp.jpg")
            with open(pic, "wb") as f:
                f.write(frame)
            result = self.recognize_encodings(pic)
            if not result["face_found_in_image"]:
                self.speak_dialog("face.error")
            elif not result["recognized"]:
                person = self.get_response("who_are_you")
                if person:
                    self.train_user(person, pic)
            else:
                self.speak(result["person"])


def create_skill():
    return FaceRecognition()
