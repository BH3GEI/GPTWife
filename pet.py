import os
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
import facerecognize
import pprint
import weather
from datetime import datetime


class Detectemotion(QThread):
    change = pyqtSignal(str, int, int)

    def run(self):
        while True:
            try:
                people_emotion, people_label, people_emotion_number = facerecognize.faceReco(face_detector, emotion_classifier, emotions, face_recognizer)
            except:
                people_label = 0
                people_emotion = "neutral"
                people_emotion_number = 2
            # print("aaaa", people_label)
            # print("bbbb", people_emotion_number)
            self.change.emit(people_emotion, people_label, people_emotion_number)
            # 每10秒emit一个值
            self.msleep(10)


class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        # 加入检测人脸进程
        super().__init__()

        self.text = ""
        self.dialog = None
        # 识别到的人物序号
        self.people_label = 1
        # self.walk_permit 0可以走路 1 不再走路
        self.walk_permit = 0
        # self.walk_control 0可以位移 1 不再位移
        self.walk_control = 0
        # self.walk_condition 0可以更换左右走动画 1不更换动画
        self.walk_condition = 0
        # 初始化状态
        self.condition = 0
        self.talk_condition = 0
        self.emotion_condition = 0

        # 开始处理dialog.txt
        self.talkdialog()
        # 开始更新表情参数
        self.changeEmotion
        # 打开检测表情线程
        self.thread = Detectemotion()
        self.thread.start()
        self.thread.change.connect(self.changeEmotion)

        super(DesktopPet, self).__init__(parent)
        # 初始化窗口
        self.movie = None
        self.image = None
        self.screen_width = QDesktopWidget().availableGeometry().width()
        self.screen_height = QDesktopWidget().availableGeometry().height()
        # 初始化表情
        self.people_emotion = "neutral"
        self.people_label = 0
        # 情绪序号 emotions = ['happy', 'disgust', 'neutral', 'angry', 'sad', 'surprise', 'fear']
        self.people_emotion_number = 2
        # 初始化计时器
        self.count = 0
        # 初始化鼠标点击状态、初始位置
        self.mouse_pressed = False
        self.origin_pos = self.pos()
        # 初始化运动方向 1向右 0向左
        self.direction = 1
        # 初始化开启动画
        self.walk_movie = QMovie("emotion/love.gif")
        self.emotion_movie = QMovie("emotion/love.gif")
        # 初始化开始
        self.init()
        # 托盘化初始
        self.initPall()
        # 宠物静态gif图加载
        self.initPetImage()
        # 开启时钟
        self.pettimer()

# 窗体初始化
    def init(self):
        # 初始化
        # 设置窗口属性:窗口无标题栏且固定在最前面
        # FrameWindowHint:无边框窗口
        # WindowStaysOnTopHint: 窗口总显示在最上面
        # SubWindow: 新窗口部件是一个子窗口，而无论窗口部件是否有父窗口部件
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
        self.movie = QMovie("emotion/love.gif")
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

    def pettimer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.handleTimeout)
        self.timer.start(100)  # 每0.1秒执行
        self.count = 0

    def handleTimeout(self):
        self.count += 1
        # print(self.walk_condition)
        if self.count % 8 == 0:  # 每0.8秒执行
            # print("walk")
            self.walk()

        if self.count % 100 == 0:  # 每10秒执行
            if self.emotion_condition == 0:
                # print("emotion")
                self.emotion()
                self.talk()
                self.walk_control = 1
                self.walk_condition = 1

        # 为了让emotion的gif完全播放
        if self.count % 130 == 0:  # 每13秒执行
            if self.walk_permit == 0:
                self.walk_control = 0
            self.walk_condition = 0
            self.talk_clear()
            self.count = 0


    @pyqtSlot(str, int, int)
    def changeEmotion(self, people_emotion, people_label, people_emotion_number):
        self.people_emotion = people_emotion
        self.people_label = people_label
        self.people_emotion_number = people_emotion_number

    # 把dialog.txt存入self.dialog
    def talkdialog(self):
        self.dialog = {}
        with open('dialog.txt', encoding='gb2312') as f:
            for line in f:
                self.dialog_emotion, self.dialog_emotion_number, self.dialog_label, self.dialog_text = line.split()
                self.dialog_label = int(self.dialog_label.strip())
                self.dialog_emotion_number = int(self.dialog_emotion_number.strip())
                self.dialog.setdefault(self.dialog_emotion_number, {}).setdefault(self.dialog_label, []).append(self.dialog_text.strip())
        pprint.pprint(self.dialog)

    # 清空说话
    def talk_clear(self):
        self.text = ""
        print("cccc", self.text)
        self.talkLabel.setText(self.text)
        # 设置样式
        self.talkLabel.setStyleSheet(
            "font: bold;"
            "font:20pt '楷体';"
            "color:black;"
            "background-color: black"
            "url(:/)"
        )
        # 根据内容自适应大小
        self.talkLabel.adjustSize()

    # 宠物对话框行为处理
    def talk(self):
        if not self.talk_condition:
            self.text = self.dialog[self.people_emotion_number][self.people_label][0]
            print("cccc", self.text, self.people_emotion_number, self.people_label)
            self.talkLabel.setText(self.text)
            # 设置样式
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:20pt '楷体';"
                "color:black;"
                "background-color: black"
                "url(:/)"
            )
            # 根据内容自适应大小
            self.talkLabel.adjustSize()
        else:
            # talk_condition为1显示为别点我，这里同样可以通过if-else-if来拓展对应的行为
            self.talkLabel.setText("呜呼呜呼")
            self.talkLabel.setStyleSheet(
                "font: bold;"
                "font:20pt '楷体';"
                "color:black;"
                "background-color: black"
                "url(:/)"
            )
            self.talkLabel.adjustSize()
            # 设置为正常状态
            self.talk_condition = 0

    # 切换情感动画
    def emotion(self):
        # 动画切换表情
        print("展示心情", self.people_emotion, self.people_emotion_number, self.people_label)
        if self.emotion_condition == 0:
            if self.people_emotion == 'happy':
                self.movie = QMovie("./emotion/love.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                # print("happy")
            elif self.people_emotion == 'angry':
                self.movie = QMovie("./emotion/angry.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                # print("angry")
            elif self.people_emotion == 'surprise':
                self.movie = QMovie("./emotion/surprise.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                # print("surprise")
            elif self.people_emotion == 'sad':
                self.movie = QMovie("./emotion/sad.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                # print("sad")
            elif self.people_emotion == 'neutral':
                if self.direction == -1:  # 向左
                    self.movie = QMovie("normal/left walk.gif")
                    self.movie.setScaledSize(QSize(200, 200))
                    self.image.setMovie(self.movie)
                    self.movie.start()
                else:  # 向右
                    self.movie = QMovie("./normal/right walk.gif")
                    self.movie.setScaledSize(QSize(200, 200))
                    self.image.setMovie(self.movie)
                    self.movie.start()

    # 位移和切换方向动画
    def walk(self):
        # 宠物能走的最大范围
        width, _ = QDesktopWidget().availableGeometry().width(), QDesktopWidget().availableGeometry().height()
        # 定义步速和方向
        self.speed = 10
        # 获取当前的坐标
        pos = self.pos()
        x, y = pos.x(), pos.y()
        # 根据方向往左或往右走
        if x <= 0:
            self.direction = 1
        elif x >= width:
            self.direction = -1

        if self.walk_control == 0 and self.walk_permit != 1:
            # 移动宠物
            pos = self.pos()
            self.move(pos.x() + self.direction * self.speed, pos.y())

        if self.walk_condition == 0:
            # 根据方向播放不同的gif
            if self.direction == -1:  # 向左
                self.movie = QMovie("normal/left walk.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
            else:  # 向右
                self.movie = QMovie("./normal/right walk.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()

    # 退出操作，关闭程序
    def quit(self):
        app.quit()

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
        nowalk = menu.addAction("不行走")
        walk = menu.addAction("行走")
        noemotion = menu.addAction("没情感")
        emotion = menu.addAction("情感")
        # 使用exec_()方法显示菜单。从鼠标右键事件对象中获得当前坐标。mapToGlobal()方法把当前组件的相对坐标转换为窗口（window）的绝对坐标。
        action = menu.exec_(self.mapToGlobal(event.pos()))
        # 点击事件为退出
        if action == quitAction:
            qApp.quit()
        # 点击事件为隐藏
        if action == hide:
            # 通过设置透明度方式隐藏宠物
            self.setWindowOpacity(0)
        if action == nowalk:
            self.walk_permit = 1
        if action == walk:
            self.walk_permit = 0
        if action == noemotion:
            self.emotion_condition = 1
        if action == emotion:
            self.emotion_condition = 0


class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.init_ui()

    # 初始化聊天框
    def init_ui(self):
        chat_btn = QPushButton("聊天", self)
        chat_btn.clicked.connect(self.show_chat)
        self.show()
        # ...其他UI元素
        self.chat_box = QDialog(self)
        self.init_chat()

    # 初始化聊天功能
    def init_chat(self):
        weather_btn = QPushButton("天气", self.chat_box)
        weather_btn.move(20, 20)
        weather_btn.clicked.connect(self.get_weather)

        time_btn = QPushButton("时间", self.chat_box)
        time_btn.move(20, 50)
        time_btn.clicked.connect(self.get_time)

        intro_btn = QPushButton("简介", self.chat_box)
        intro_btn.move(20, 80)
        intro_btn.clicked.connect(self.get_intro)

    def show_chat(self):
        self.chat_box.exec_()

    # 查询天气按钮
    def get_weather(self):
        # 请用户输入城市名称
        self.location = QInputDialog.getText(self, '输入城市', '请输入城市名称:')
        print(self.location[0])
        # 网络查询天气
        try:
            weather_result = weather.request_weather(self.location[0])
            if weather_result['status'] == 200:
                text = f"城市:{weather_result['cityInfo']['parent']} {weather_result['cityInfo']['city']}\n"
                text += f"时间:{weather_result['time']} {weather_result['data']['forecast'][0]['week']}\n"
                text += f"温度:{weather_result['data']['forecast'][0]['high']} {weather_result['data']['forecast'][0]['low']}\n"
                text += f"天气:{weather_result['data']['forecast'][0]['type']}"
            QMessageBox.information(self, "OK", text)
        except:
            print("这个城市找不到哦")

    # 查询天气按钮
    def get_time(self):
        # 获取当前时间
        currentDateAndTime = datetime.now()
        text = str(currentDateAndTime)
        QMessageBox.information(self, "时间", text)

    # 简历
    def get_intro(self):
        text = f"这是一个电子宠物。\n"
        text += f"有以下功能\n"
        text += f"1、查询天气：输入地点点击ok。\n"
        text += f"2、查询时间：点击时间\n"
        text += f"3、行走：右键电子宠物点击行走即可切换是否沿屏幕行走。\n"
        text += f"4、检测表情：右键电子宠物点击感情即可切换是否检测您的表情，当您难过或开心时会出现不同的话和大鹅动画。\n"
        text += f"5、检测人物：这部分还没有做ui输入，现在您可以将面部照片放进faces文件夹。\n"
        # 获取简介信息
        QMessageBox.information(self, "简介", text)


if __name__ == '__main__':
    face_detector, emotion_classifier, emotions, face_recognizer = facerecognize.facerecognize_begin()
    # try:
    # 创建了一个QApplication对象，对象名为app，带两个参数argc,argv
    # 所有的PyQt5应用必须创建一个应用（Application）对象。sys.argv参数是一个来自命令行的参数列表。
    app = QApplication(sys.argv)
    # 窗口组件初始化
    pet = DesktopPet()
    # 1. 进入时间循环；
    # 2. wait，直到响应app可能的输入；
    # 3. QT接收和处理用户及系统交代的事件（消息），并传递到各个窗口；
    # 4. 程序遇到exit()退出时，机会返回exec()的值。
    window = Window()
    window.show()
    sys.exit(app.exec_())
    # except Exception as e:
