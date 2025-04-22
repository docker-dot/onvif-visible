import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QLabel, QSlider, QGroupBox)
from Device.onvif_ptz_controller import OnvifPTZController


class CameraController(QWidget):
    def __init__(self):
        super().__init__()
        self.video_enabled = None
        self.controller = OnvifPTZController("192.168.1.64", 80, "admin", "123456")
        self.init_ui()
        self.setup_connections()
        self.cap = None
        self.timer = QTimer()
        self.init_video()

    def init_video(self):
        self.timer.timeout.connect(self.update_frame)
        self.video_enabled = False

    def toggle_camera(self):
        if not self.video_enabled:
            try:
                # 使用RTSP流替换本地摄像头
                rtsp_url = "rtsp://admin:123456@192.168.1.64/stream"
                self.cap = cv2.VideoCapture(rtsp_url)

                if not self.cap.isOpened():
                    raise ConnectionError("无法连接网络摄像头")

                self.timer.start(30)
                self.video_enabled = True
                self.btn_camera.setText("关闭视频")
            except Exception as e:
                self.show_error(str(e))
                if self.cap:
                    self.cap.release()
        else:
            self.cap.release()
            self.timer.stop()
            self.video_label.clear()
            self.video_enabled = False
            self.btn_camera.setText("启动视频")

        # if not self.video_enabled:
        #     self.cap = cv2.VideoCapture(0)  # 使用默认摄像头
        #     if not self.cap.isOpened():
        #         self.show_error("摄像头无法打开")
        #         return
        #     self.timer.start(30)  # 30ms刷新间隔
        #     self.video_enabled = True
        # else:
        #     self.cap.release()
        #     self.timer.stop()
        #     self.video_label.clear()
        #     self.video_enabled = False

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            # 转换颜色空间 BGR -> RGB
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 创建QImage并缩放显示
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line,
                              QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image)

            # 保持比例缩放
            scaled_pixmap = pixmap.scaled(self.video_label.size(),
                                          # Qt.KeepAspectRatio,
                                          Qt.KeepAspectRatioByExpanding,
                                          Qt.SmoothTransformation)
            self.video_label.setPixmap(scaled_pixmap)

    def init_ui(self):
        self.setWindowTitle("PTZ摄像头控制器")
        self.setGeometry(100, 100, 600, 400)
        # self.setMinimumSize(800, 600)

        # 主布局
        main_layout = QHBoxLayout()

        # 左侧控制面板（原方向控制+新增视频显示）
        left_panel = QVBoxLayout()

        # 视频显示区域
        self.video_group = QGroupBox("实时画面")
        self.video_label = QLabel(self)
        # self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(800, 600)
        video_layout = QVBoxLayout()
        video_layout.addWidget(self.video_label)
        self.video_group.setLayout(video_layout)

        # 方向控制区域
        direction_group = QGroupBox("云台控制")
        grid = QGridLayout()

        # 创建8方向按钮
        self.btn_up = QPushButton("↑", self)
        self.btn_down = QPushButton("↓", self)
        self.btn_left = QPushButton("←", self)
        self.btn_right = QPushButton("→", self)
        self.btn_upleft = QPushButton("↖", self)
        self.btn_upright = QPushButton("↗", self)
        self.btn_downleft = QPushButton("↙", self)
        self.btn_downright = QPushButton("↘", self)

        # 3x3网格布局
        grid.addWidget(self.btn_upleft, 0, 0)
        grid.addWidget(self.btn_up, 0, 1)
        grid.addWidget(self.btn_upright, 0, 2)
        grid.addWidget(self.btn_left, 1, 0)
        grid.addWidget(QLabel("PTZ", self), 1, 1)  # 中心占位
        grid.addWidget(self.btn_right, 1, 2)
        grid.addWidget(self.btn_downleft, 2, 0)
        grid.addWidget(self.btn_down, 2, 1)
        grid.addWidget(self.btn_downright, 2, 2)
        direction_group.setLayout(grid)

        # 组合左侧面板
        left_panel.addWidget(self.video_group, 4)  # 视频显示区域占比更大
        left_panel.addWidget(direction_group, 3)

        # 右侧控制面板
        control_panel = QVBoxLayout()

        # 变焦控制
        zoom_group = QGroupBox("变焦控制")
        zoom_layout = QVBoxLayout()
        self.btn_zoomin = QPushButton("+", self)
        self.btn_zoomout = QPushButton("-", self)
        # 在变焦控制组中添加
        self.btn_camera = QPushButton("启动摄像头", self)
        zoom_layout.addWidget(self.btn_camera)
        zoom_layout.addWidget(self.btn_zoomin)
        zoom_layout.addWidget(self.btn_zoomout)
        zoom_group.setLayout(zoom_layout)

        # 速度调节
        speed_group = QGroupBox("速度设置")
        speed_layout = QVBoxLayout()
        self.pt_speed_slider = QSlider(Qt.Horizontal)
        self.pt_speed_slider.setRange(0, 100)
        self.zoom_speed_slider = QSlider(Qt.Horizontal)
        self.zoom_speed_slider.setRange(0, 100)
        speed_layout.addWidget(QLabel("云台速度:"))
        speed_layout.addWidget(self.pt_speed_slider)
        speed_layout.addWidget(QLabel("变焦速度:"))
        speed_layout.addWidget(self.zoom_speed_slider)
        speed_group.setLayout(speed_layout)

        # 状态显示
        self.status_label = QLabel("就绪", self)

        # 组合右侧面板
        control_panel.addWidget(zoom_group)
        control_panel.addWidget(speed_group)
        control_panel.addWidget(self.status_label)
        control_panel.addStretch()

        # 组合主布局
        main_layout.addWidget(direction_group, 3)  # 3:1的比例
        main_layout.addLayout(control_panel, 1)
        self.setLayout(main_layout)

    def setup_connections(self):
        # 方向按钮绑定
        self.btn_up.pressed.connect(self.controller.start_up)
        self.btn_up.released.connect(self.controller.stop_move)

        self.btn_down.pressed.connect(self.controller.start_down)
        self.btn_down.released.connect(self.controller.stop_move)

        self.btn_left.pressed.connect(self.controller.start_left)
        self.btn_left.released.connect(self.controller.stop_move)

        self.btn_right.pressed.connect(self.controller.start_right)
        self.btn_right.released.connect(self.controller.stop_move)

        self.btn_upleft.pressed.connect(self.controller.start_up_left)
        self.btn_upleft.released.connect(self.controller.stop_move)

        self.btn_upright.pressed.connect(self.controller.start_up_right)
        self.btn_upright.released.connect(self.controller.stop_move)

        self.btn_downleft.pressed.connect(self.controller.start_down_left)
        self.btn_downleft.released.connect(self.controller.stop_move)

        self.btn_downright.pressed.connect(self.controller.start_down_right)
        self.btn_downright.released.connect(self.controller.stop_move)

        # 其他方向按钮同理...

        # 变焦控制
        self.btn_zoomin.pressed.connect(self.controller.start_zoomin)
        self.btn_zoomin.released.connect(self.controller.stop_move)

        self.btn_zoomout.pressed.connect(self.controller.start_zoomout)
        self.btn_zoomout.released.connect(self.controller.stop_move)

        # 速度调节
        self.pt_speed_slider.valueChanged.connect(self.update_pt_speed)
        self.zoom_speed_slider.valueChanged.connect(self.update_zoom_speed)

        # 状态信号连接
        self.controller.status_signal.connect(self.update_status)
        self.controller.error_signal.connect(self.show_error)

        self.btn_camera.clicked.connect(self.toggle_camera)
        # 窗口尺寸变化事件
        self.video_label.resizeEvent = self.resize_video

    def resize_video(self, event):
        if self.video_enabled:
            self.update_frame()  # 窗口尺寸变化时更新画面

    def update_pt_speed(self, value):
        self.controller.pt_speed = value / 100.0  # 转换为0.0-1.0范围
        self.status_label.setText(f"云台速度: {value}%")

    def update_zoom_speed(self, value):
        self.controller.zoom_speed = value / 100.0
        self.status_label.setText(f"变焦速度: {value}%")

    def update_status(self, msg):
        self.status_label.setText(f"状态: {msg}")

    def show_error(self, msg):
        self.status_label.setText(f"错误: {msg}")
        # 可以添加QMessageBox弹窗提示