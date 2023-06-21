import facerecognize
from pet import DesktopPet

import sys

from PyQt5.QtWidgets import *



if __name__ == '__main__':
    face_detector, emotion_classifier, emotions, face_recognizer = facerecognize.facerecognize_begin()
    emotioncondition = facerecognize.faceReco(face_detector, emotion_classifier, emotions, face_recognizer)
    print("正在下蛋")
    goose = DesktopPet(emotioncondition)
    print("小鹅出生")
    app = QApplication(sys.argv)
    # 启动事件循环
    app.exec_()
    while True:
        print("我换心情")
        emotioncondition = facerecognize.faceReco(face_detector, emotion_classifier, emotions, face_recognizer)
        print("鹅换心情")
        goose.update(emotioncondition)

