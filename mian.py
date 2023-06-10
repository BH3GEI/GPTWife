import os
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from threading import Thread
import cv2
from keras.models import load_model
from tensorflow.keras.utils import img_to_array
import numpy as np

# 创建一个人脸检测器对象
face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# 创建一个人脸识别器对象
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

# 加载模型
emotion_classifier = load_model('emotionModel0.hdf5')

# 表情标签
emotions = ['happy', 'disgust', 'neutral', 'angry', 'sad', 'surprise', 'fear']


class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        super(DesktopPet, self).__init__(parent)
        # 窗体初始化
        self.init()
        # 托盘化初始
        self.initPall()
        # 宠物静态gif图加载
        self.initPetImage()
        # 宠物正常待机，实现随机切换动作
        self.petNormalAction()


    # 窗体初始化
    def init(self):
        # 初始化
        # 设置窗口属性:窗口无标题栏且固定在最前面
        # FrameWindowHint:无边框窗口
        # WindowStaysOnTopHint: 窗口总显示在最上面
        # SubWindow: 新窗口部件是一个子窗口，而无论窗口部件是否有父窗口部件
        # https://blog.csdn.net/kaida1234/article/details/79863146
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SubWindow)
        # setAutoFillBackground(True)表示的是自动填充背景,False为透明背景
        self.setAutoFillBackground(False)
        # 窗口透明，窗体空间不透明
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 重绘组件、刷新
        self.repaint()

    # 托盘化设置初始化
    def initPall(self):
        # 导入准备在托盘化显示上使用的图标
        icons = os.path.join('tigerIcon.jpg')
        # 设置右键显示最小化的菜单项
        # 菜单项退出，点击后调用quit函数
        quit_action = QAction('退出', self, triggered=self.quit)
        # 设置这个点击选项的图片
        quit_action.setIcon(QIcon(icons))
        # 菜单项显示，点击后调用showing函数
        showing = QAction(u'显示', self, triggered=self.showwin)
        # 新建一个菜单项控件
        self.tray_icon_menu = QMenu(self)
        # 在菜单栏添加一个无子菜单的菜单项‘退出’
        self.tray_icon_menu.addAction(quit_action)
        # 在菜单栏添加一个无子菜单的菜单项‘显示’
        self.tray_icon_menu.addAction(showing)
        # QSystemTrayIcon类为应用程序在系统托盘中提供一个图标
        self.tray_icon = QSystemTrayIcon(self)
        # 设置托盘化图标
        self.tray_icon.setIcon(QIcon(icons))
        # 设置托盘化菜单项
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        # 展示
        self.tray_icon.show()

    # 宠物静态gif图加载
    def initPetImage(self):
        # 对话框定义
        self.talkLabel = QLabel(self)
        # 对话框样式设计
        self.talkLabel.setStyleSheet("font:15pt '楷体';border-width: 1px;color:blue;")
        # 定义显示图片部分
        self.image = QLabel(self)
        # QMovie是一个可以存放动态视频的类，一般是配合QLabel使用的,可以用来存放GIF动态图
        self.movie = QMovie("normal/right walk.gif")
        # 设置标签大小
        self.movie.setScaledSize(QSize(200, 200))
        # 将Qmovie在定义的image中显示
        self.image.setMovie(self.movie)
        self.movie.start()
        self.resize(1024, 1024)
        # 调用自定义的randomPosition，会使得宠物出现位置随机
        self.randomPosition()
        # 展示
        self.show()
        # https://new.qq.com/rain/a/20211014a002rs00
        # 将宠物正常待机状态的动图放入pet1中
        self.pet1 = []
        for i in os.listdir("normal"):
            self.pet1.append("normal/" + i)
        # 将宠物正常待机状态的对话放入pet2中
        self.dialog = []
        # 读取目录下dialog文件
        with open("dialog.txt", "r", encoding="GB2312") as f:
            text = f.read()
            # 以\n 即换行符为分隔符，分割放进dialog中
            self.dialog = text.split("\n")

    # 宠物正常待机动作
    def petNormalAction(self):
        # 每隔一段时间做个动作
        # 定时器设置
        self.timer = QTimer()
        # 时间到了自动执行
        self.timer.timeout.connect(self.randomAct)
        # 动作时间切换设置
        self.timer.start(3000)
        # 宠物状态设置为正常
        self.condition = 0

        # 每隔一段时间切换对话
        self.talkTimer = QTimer()
        self.talkTimer.timeout.connect(self.talk)
        self.talkTimer.start(3000)
        # 对话状态设置为常态
        self.talk_condition = 0
        # 宠物对话框
        self.talk()

        # 左右走
        self.walktimer = QTimer()
        # 时间到了自动执行
        self.walktimer.timeout.connect(self.walk)
        # 动作时间切换设置
        self.walktimer.start(300)
        # 行走状态设置为常态
        self.walk_condition = 1
        # 宠物行走
        self.walk()

    # 随机动作切换
    def randomAct(self):
        # condition记录宠物状态，宠物状态为0时，代表正常待机
        if not self.condition:
            # 随机选择装载在pet1里面的gif图进行展示，实现随机切换
            self.movie = QMovie(random.choice(self.pet1))
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        # condition不为0，转为切换特有的动作，实现宠物的点击反馈
        # 这里可以通过else-if语句往下拓展做更多的交互功能
        else:
            # 读取特殊状态图片路径
            self.movie = QMovie("./click/right walk.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            # 宠物状态设置为正常待机
            self.condition = 0
            self.talk_condition = 0

    def randomAct(self):
        # condition记录宠物状态，宠物状态为0时，代表正常待机
        if not self.condition:
            # 随机选择装载在pet1里面的gif图进行展示，实现随机切换
            self.movie = QMovie(random.choice(self.pet1))
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        # condition不为0，转为切换特有的动作，实现宠物的点击反馈
        # 这里可以通过else-if语句往下拓展做更多的交互功能
        else:
            # 读取特殊状态图片路径
            self.movie = QMovie("./click/right walk.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            # 宠物状态设置为正常待机
            self.condition = 0
            self.talk_condition = 0

    # 宠物对话框行为处理
    def talk(self):
        if not self.talk_condition:
            # talk_condition为0则选取加载在dialog中的语句
            self.talkLabel.setText(random.choice(self.dialog))
            # 设置样式
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            # 根据内容自适应大小
            self.talkLabel.adjustSize()
        else:
            # talk_condition为1显示为别点我，这里同样可以通过if-else-if来拓展对应的行为
            self.talkLabel.setText("别点我")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:25pt '楷体';"
                "color:white;"
                "background-color: white"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

    def emotionAct(self):
        # condition记录宠物状态，宠物状态为0时，代表正常待机
        if not self.emotioncondition:
            # 随机选择装载在pet1里面的gif图进行展示，实现随机切换
            self.movie = QMovie(random.choice("./click/right walk.gif"))
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
        # condition不为0，转为切换特有的动作，实现宠物的点击反馈
        # 这里可以通过else-if语句往下拓展做更多的交互功能
        else:
            # 读取特殊状态图片路径
            self.movie = QMovie("./click/right walk.gif")
            # 宠物大小
            self.movie.setScaledSize(QSize(200, 200))
            # 将动画添加到label中
            self.image.setMovie(self.movie)
            # 开始播放动画
            self.movie.start()
            # 宠物状态设置为正常待机
            self.condition = 0
            self.talk_condition = 0

    def walk(self):
        # 宠物能走的最大范围
        if not self.walk_condition:
            width, _ = QDesktopWidget().availableGeometry().width(), QDesktopWidget().availableGeometry().height()
            # 定义步速和方向
            self.speed = 10
            if not hasattr(self, 'direction'):
                self.direction = 1  # 表示宠物一开始要向右走，也可以赋值为-1让它一开始向左走

            # 获取当前的坐标
            pos = self.pos()
            x, y = pos.x(), pos.y()

            # 根据方向往左或往右走
            if x <= 0:
                self.direction = 1
            elif x >= width:
                self.direction = -1
            self.move(x + self.direction * self.speed, y)
            print(self.direction)

    # 退出操作，关闭程序
    def quit(self):
        self.close()
        sys.exit()

    # 显示宠物
    def showwin(self):
        # setWindowOpacity（）设置窗体的透明度，通过调整窗体透明度实现宠物的展示和隐藏
        self.setWindowOpacity(1)

    # 宠物随机位置
    def randomPosition(self):
        # screenGeometry（）函数提供有关可用屏幕几何的信息
        screen_geo = QDesktopWidget().screenGeometry()
        # 获取窗口坐标系
        pet_geo = self.geometry()
        width = (screen_geo.width() - pet_geo.width()) * random.random()
        height = (screen_geo.height() - pet_geo.height()) * random.random()
        self.move(int(width), int(height))

    # 鼠标左键按下时, 宠物将和鼠标位置绑定
    def mousePressEvent(self, event):
        # 更改宠物状态为点击
        self.condition = 1
        # 更改宠物对话状态
        self.talk_condition = 1
        # 即可调用对话状态改变
        self.talk()
        # 即刻加载宠物点击动画
        self.randomAct()
        if event.button() == Qt.LeftButton:
            self.is_follow_mouse = True
        # globalPos() 事件触发点相对于桌面的位置
        # pos() 程序相对于桌面左上角的位置，实际是窗口的左上角坐标
        self.mouse_drag_pos = event.globalPos() - self.pos()
        event.accept()
        # 拖动时鼠标图形的设置
        self.setCursor(QCursor(Qt.OpenHandCursor))

    # 鼠标移动时调用，实现宠物随鼠标移动
    def mouseMoveEvent(self, event):
        # 如果鼠标左键按下，且处于绑定状态
        if Qt.LeftButton and self.is_follow_mouse:
            # 宠物随鼠标进行移动
            self.move(event.globalPos() - self.mouse_drag_pos)
        event.accept()

    # 鼠标释放调用，取消绑定
    def mouseReleaseEvent(self, event):
        self.is_follow_mouse = False
        # 鼠标图形设置为箭头
        self.setCursor(QCursor(Qt.ArrowCursor))

    # 鼠标移进时调用
    def enterEvent(self, event):
        # 设置鼠标形状 Qt.ClosedHandCursor   非指向手
        self.setCursor(Qt.ClosedHandCursor)

    # 宠物右键点击交互
    def contextMenuEvent(self, event):
        # 定义菜单
        menu = QMenu(self)
        # 定义菜单项
        quitAction = menu.addAction("退出")
        hide = menu.addAction("隐藏")
        walk = menu.addAction("行走")
        # 使用exec_()方法显示菜单。从鼠标右键事件对象中获得当前坐标。mapToGlobal()方法把当前组件的相对坐标转换为窗口（window）的绝对坐标。
        action = menu.exec_(self.mapToGlobal(event.pos()))
        # 点击事件为退出
        if action == quitAction:
            qApp.quit()
        # 点击事件为隐藏
        if action == hide:
            # 通过设置透明度方式隐藏宠物
            self.setWindowOpacity(0)
        if action == walk:
            self.walk_condition = 0

#读取用户脸
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


if __name__ == '__main__':
    # 创建了一个QApplication对象，对象名为app，带两个参数argc,argv
    # 所有的PyQt5应用必须创建一个应用（Application）对象。sys.argv参数是一个来自命令行的参数列表。
    app = QApplication(sys.argv)
    # 窗口组件初始化
    pet = DesktopPet()
    # 1. 进入时间循环；
    # 2. wait，直到响应app可能的输入；
    # 3. QT接收和处理用户及系统交代的事件（消息），并传递到各个窗口；
    # 4. 程序遇到exit()退出时，机会返回exec()的值。
    sys.exit(app.exec_())
