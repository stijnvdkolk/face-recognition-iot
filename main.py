import face_recognition
import json
from hiatus import set_timeout, clear_timeout
import cv2
import numpy as np
IMG_W = 1280
IMG_H = 720

video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_W)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_H)

known_face_encodings = []
known_face_names = []

print('Loading all faces, this may take a while...')

with open("data.json") as file:
    for item in json.load(file):
        image = face_recognition.load_image_file(item['image'])
        face_encoding = face_recognition.face_encodings(image)[0]
        known_face_encodings.append(face_encoding)
        known_face_names.append(item['name'])

print(f'Loaded {len(known_face_names)} people!')


face_locations = []
face_encodings = []
face_names = []

sendnotify = True
lastknownperson = None

def disableNotify():
  global sendnotify
  sendnotify = not sendnotify

def noneifyLastKnownPerson():
  global lastknownperson
  lastknownperson = None

timeout_one = None
timeone_two = None

while True:
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        face_names.append(name)

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        if sendnotify:
            sendnotify = False
            timeout_one = set_timeout(disableNotify, 30.0)
            timeout_two = set_timeout(noneifyLastKnownPerson, 60.0)
            if lastknownperson != name:
                lastknownperson = name
                print(name)


    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        clear_timeout(timeout_one)
        clear_timeout(timeout_two)
        break

video_capture.release()
cv2.destroyAllWindows()
