import cv2
import face_recognition
import pickle
import os

from make_hash import get_sha256_hash

def Encode(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    faceLocs = face_recognition.face_locations(img)
    if faceLocs:
        faceEncoding = face_recognition.face_encodings(img, faceLocs)[0]
        encoding_bytes = pickle.dumps(faceEncoding)
        return encoding_bytes
    else:
        print("На изображении не обнаружены лица")
        return None