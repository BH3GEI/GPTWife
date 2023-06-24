import cv2
import os
import numpy as np
from keras.models import load_model
from tensorflow.keras.utils import img_to_array



def facerecognize_begin():
    # 创建一个人脸检测器对象
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    # 创建一个人脸识别器对象
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()

    # 加载模型
    emotion_classifier = load_model('emotionModel0.hdf5')

    # 表情标签
    emotions = ['happy', 'disgust', 'neutral', 'angry', 'sad', 'surprise', 'fear']

    # 读取人脸照片，建议传入faces
    def read_images_and_labels(path):
        # 获取所有文件夹的名称
        folders = os.listdir(path)
        # 创建一个空列表来存储人脸图像和标签
        images = []
        labels = []
        # 遍历每个文件夹
        for folder in folders:
            # 获取文件夹的路径
            folder_path = os.path.join(path, folder)
            # 获取文件夹中的所有图像文件名
            image_names = os.listdir(folder_path)
            # 遍历每个图像文件
            for image_name in image_names:
                # 获取图像文件的路径
                image_path = os.path.join(folder_path, image_name)
                # 读取图像文件
                image = cv2.imread(image_path)
                # 转换为灰度图像
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                # 检测人脸位置
                faces = face_detector.detectMultiScale(gray, 1.3, 5)
                # 遍历每个人脸
                for (x, y, w, h) in faces:
                    # 裁剪出人脸区域
                    face = gray[y:y + h, x:x + w]
                    # 将人脸图像添加到列表中
                    images.append(face)
                    # 将对应的学号添加到列表中
                    labels.append(int(folder))
        # 返回人脸图像和标签的列表
        return images, labels, x, y

    # 读取已有的人脸照片和学号
    print("正在读取照片~")
    images, labels, x, y = read_images_and_labels("faces")

    # 训练人脸识别器
    print("正在训练模型~")
    face_recognizer.train(images, np.array(labels))

    # 保存以便.load
    print("正在保存模型~")
    face_recognizer.save("model.yml")

    print("训练完成~")
    return face_detector, emotion_classifier, emotions, face_recognizer


def faceReco(face_detector, emotion_classifier, emotions, face_recognizer):
    label = 0
    emotion_number = 2
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    # 转换为灰度图像
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 检测人脸位置
    faces = face_detector.detectMultiScale(gray, 1.3, 5)
    # 遍历每个人脸
    emotion = "neutral"
    for (x, y, w, h) in faces:
        # 裁剪出人脸区域
        face = gray[y:y + h, x:x + w]
        # 调整图像大小以匹配表情模型的输入大小
        resized_image = cv2.resize(face, (48, 48))
        # 将图像转换为表情模型所需的数组格式
        image_array = img_to_array(resized_image)
        image_array = np.expand_dims(image_array, axis=0)
        # 使用模型进行表情预测
        predictions = emotion_classifier.predict(image_array)
        emotion = emotions[np.argmax(predictions)]
        emotion_number = np.argmax(predictions)
        # print("表情：", emotion)
        # 预测人脸的标签
        # 如果检测到人脸,则预测人脸标签
        if w > 0 and h > 0:
            label, confidence = face_recognizer.predict(face)
        # print("身份：", label, confidence, emotion_number)
    return emotion, label, emotion_number
