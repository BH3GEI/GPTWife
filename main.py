import facerecognize

face_detector, emotion_classifier, emotions, face_recognizer = facerecognize.facerecognize_begin()
emotioncondition = facerecognize.faceReco(face_detector, emotion_classifier, emotions, face_recognizer)

