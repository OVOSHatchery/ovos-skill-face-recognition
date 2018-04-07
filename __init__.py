import face_recognition
import cv2
from os import remove, makedirs
from os.path import join, dirname, expanduser, exists
from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft.messagebus.message import Message
from mycroft.util.log import LOG
import pickle
from shared_camera import Camera
import time
from threading import Thread

__author__ = 'jarbas'


class FaceRecognition(MycroftSkill):
    def __init__(self):
        super(FaceRecognition, self).__init__()
        if "model_path" not in self.settings:
            self.settings["model_path"] = expanduser(
                "~/.face_recognition/face_encodings.fr")

        if "sensitivity" not in self.settings:
            self.settings["sensitivity"] = 0.5

        if "detect_interval" not in self.settings:
            self.settings["detect_interval"] = 1

        if "detect_timeout" not in self.settings:
            self.settings["detect_timeout"] = 10

        if "scan_faces" not in self.settings:
            self.settings["scan_faces"] = True

        if "cascade" not in self.settings:
            self.settings["cascade"] = join(dirname(__file__),
                                            'haarcascade_frontalface_alt2.xml')

        if dirname(__file__) in self.settings["model_path"]:
            self.reload_skill = False
        if not exists(self.settings["model_path"].replace(
                "face_encodings.fr", "")):
            makedirs(self.settings["model_path"].replace(
                "face_encodings.fr", ""))

        self.cascade = cv2.CascadeClassifier(self.settings["cascade"])
        self.known_faces = {}

        self.load_encodings()

        self.vision = None
        self.last_detection = 0
        self.recognize = False
        self.detect_thread = Thread(target=self.face_detect_loop)
        self.detect_thread.setDaemon(True)
        self.detect_thread.start()

        self.detect_timer_thread = Thread(target=self.face_timer)
        self.detect_timer_thread.setDaemon(True)
        self.detect_timer_thread.start()

        self.camera = Camera()
        LOG.info("Local Face recognition engine started")

    def get_feed(self):
        return self.camera.get().copy()

    def initialize(self):
        self.add_event("face_recognition_request",
                       self.handle_recognition_request)

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
                        if score > self.settings["sensitivity"]:
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
            with open(self.settings["model_path"], "r") as f:
                self.known_faces = pickle.load(f)
        except Exception as e:
            LOG.warning(str(e))

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
                with open(self.settings["model_path"], "w") as f:
                    pickle.dump(self.known_faces, f)
            except Exception as e:
                res = {"success": False,
                       "error": "could not save face encodings",
                       "exception": str(e)}

        return res

    def handle_recognition_request(self, message):
        face = message.data.get("file")
        result = self.recognize_encodings(face)
        # emit result to internal bus
        self.emitter.emit(Message("face_recognition_result",
                                  {"result": result}))

    @intent_handler(IntentBuilder("recognize_face")
                    .require("recognize_my_face"))
    def handle_recognize_my_face(self, message):
        frame = self.get_feed()
        if frame is None:
            self.speak_dialog("camera.error")
        else:
            pic = expanduser("~/tmp_face.jpeg")
            cv2.imwrite(pic, frame)
            result = self.recognize_encodings(pic)
            if not result["face_found_in_image"]:
                self.speak_dialog("face.error")
            elif not result["recognized"]:
                person = self.get_response("who_are_you")
                if person:
                    self.train_user(person, pic)
            else:
                self.speak(result["person"])
            remove(pic)

    def detect_faces(self):
        """ searches webcam for faces, returns bounding boxes """
        self.vision = self.get_feed()
        gray = cv2.cvtColor(self.vision, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray, 1.3, 5)
        return faces

    def recognize_faces(self, faces):
        """ recognizes detected faces, notify of user arrival """
        if self.recognize:
            for (x, y, w, h) in faces:
                roi_color = self.vision[y:y + h, x:x + w]
                pic = expanduser("~/tmp.jpg")
                cv2.imwrite(pic, roi_color)
                result = self.recognize_encodings(pic)
                if not result["face_found_in_image"]:
                    LOG.error("face recognition requested in non face picture")
                    continue
                self.emitter.emit(Message("user_arrival.face", result))

                if result["recognized"]:
                    LOG.info("stopping face recognition")
                    self.recognize = False

    def face_timer(self):
        while True:
            if not self.recognize and time.time() - self.last_detection > \
                    self.settings["detect_timeout"]:
                self.recognize = True
                LOG.info("face detect timeout, enabling face recognition")
            time.sleep(1)

    def face_detect_loop(self):
        while True:
            time.sleep(self.settings["detect_interval"])
            if self.settings["scan_faces"]:
                faces = self.detect_faces()
                if len(faces):
                    LOG.info("detected faces: " + str(len(faces)))
                    self.last_detection = time.time()
                    self.recognize_faces(faces)

    def shutdown(self):
        super(FaceRecognition, self).shutdown()
        self.detect_timer_thread.join(0)
        self.detect_thread.join(0)


def create_skill():
    return FaceRecognition()
