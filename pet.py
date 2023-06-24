import os
import sys
import random
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
import facerecognize


class Detectemotion(QThread):
    change = pyqtSignal(str)

    def run(self):
        i = 0
        while True:
            people_emotion = facerecognize.faceReco(face_detector, emotion_classifier, emotions, face_recognizer)
            self.change.emit(people_emotion)
            print("心情也是", people_emotion)
            # 每10秒emit一个值
            self.msleep(10000)


class DesktopPet(QWidget):
    def __init__(self, parent=None, **kwargs):
        # 加入检测人脸进程
        super().__init__()
        self.thread = Detectemotion()
        self.thread.start()
        self.thread.change.connect(self.changeEmotion)

        super(DesktopPet, self).__init__(parent)
        # 窗体初始化
        self.people_emotion = None
        self.movie = None
        self.image = None
        self.screen_width = QDesktopWidget().availableGeometry().width()
        self.screen_height = QDesktopWidget().availableGeometry().height()
        self.count = 0
        self.mouse_pressed = False
        self.origin_pos = self.pos()
        self.condition = 0
        self.walk_condition = 0
        self.talk_condition = 0
        self.emotion_condition = 0
        self.direction = 1
        self.init()
        # 托盘化初始
        self.initPall()
        # 宠物静态gif图加载
        self.initPetImage()
        self.pettimer()
        self.walk_movie = QMovie("emotion/love.gif")
        self.emotion_movie = QMovie("emotion/love.gif")

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
        # 将宠物正常待机状态的对话放入pet2中
        self.dialog = []
        # 读取目录下dialog文件
        with open("dialog.txt", "r", encoding="GB2312") as f:
            text = f.read()
            # 以\n 即换行符为分隔符，分割放进dialog中
            self.dialog = text.split("\n")

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

        if self.count % 8 == 0:  # 每0.8秒执行
            # print("talk")
            self.talk()

        if self.count % 100 == 0:  # 每10秒执行
            # print("emotion")
            self.emotion()
            self.walk_condition = 1

        # 为了让emotion的gif完全播放
        if self.count % 120 == 0:  # 每12秒执行
            self.walk_condition = 0
            self.count = 0

    @pyqtSlot(str)
    def changeEmotion(self, people_emotion):
        self.people_emotion = people_emotion

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

    def emotion(self):
        # 同时走路
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

        if self.walk_condition == 0:
            # 移动宠物
            pos = self.pos()
            self.move(pos.x() + self.direction * self.speed, pos.y())

        # 动画切换表情
        if self.emotion_condition == 0:
            if self.emotion_condition == 0 and self.people_emotion == 'happy':
                self.movie = QMovie("./emotion/love.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                print("happy")
            elif self.emotion_condition == 0 and self.people_emotion == 'angry':
                self.movie = QMovie("./emotion/angry.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                print("angry")
            elif self.emotion_condition == 0 and self.people_emotion == 'surprise':
                self.movie = QMovie("./emotion/surprise.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                print("surprise")
            elif self.emotion_condition == 0 and self.people_emotion == 'sad':
                self.movie = QMovie("./emotion/sad.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()
                print("sad")
            elif self.emotion_condition == 0 and self.people_emotion == 'neutral':
                self.movie = QMovie("./emotion/sad.gif")
                self.movie.setScaledSize(QSize(200, 200))
                self.image.setMovie(self.movie)
                self.movie.start()

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

        if self.walk_condition == 0:
            # 移动宠物
            pos = self.pos()
            self.move(pos.x() + self.direction * self.speed, pos.y())
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
            self.walk_condition = 1
        if action == walk:
            self.walk_condition = 0
        if action == noemotion:
            self.emotion_condition = 1
        if action == emotion:
            self.emotion_condition = 0


if __name__ == '__main__':
    face_detector, emotion_classifier, emotions, face_recognizer = facerecognize.facerecognize_begin()
    try:
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
    except Exception as e:
        print(e)
