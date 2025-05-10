import os
import time

import cv2
from PyQt5.QtCore import Qt, QTimer, QMutex, QWaitCondition, QMutexLocker
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QGridLayout, QHBoxLayout, QVBoxLayout,
                             QLabel, QSlider, QGroupBox)
from Device.onvif_ptz_controller import OnvifPTZController

from PyQt5.QtCore import QThread, pyqtSignal


class VideoThread(QThread):
    frame_ready = pyqtSignal(object)
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, rtsp_url):
        super().__init__()
        self.rtsp_url = rtsp_url
        self.running = False
        self.cap = None
        self.lock = QMutex()
        self.last_frame = None
        self.reconnect_interval = 3  # 秒
        self.timeout_ms = 5000  # 新增超时参数
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

    def run(self):
        self.running = True
        # os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

        while self.running and self.reconnect_attempts < self.max_reconnect_attempts:
            try:
                self.cap = cv2.VideoCapture(self.rtsp_url + f"?timeout={self.timeout_ms}", cv2.CAP_FFMPEG)
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 5)
                self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, self.timeout_ms)
                self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, self.timeout_ms)
                if not self.cap.isOpened():
                    raise ConnectionError("无法打开视频流")

                self.status_signal.emit("视频流已连接")

                while self.running and self.cap.isOpened():
                    start_time = time.time()
                    ret, frame = self.cap.read()

                    # 超时检测（关键改进）
                    if (time.time() - start_time) > (self.timeout_ms / 1000):
                        raise TimeoutError("帧读取超时")
                    if ret:
                        with QMutexLocker(self.lock):
                            self.last_frame = frame.copy()
                        self.frame_ready.emit(frame)
                        # time.sleep(0.03)
                    else:
                        self.error_signal.emit("视频流中断，尝试重连...")
                        break
            except TimeoutError as e:
                self.reconnect_attempts += 1
                self.error_signal.emit(f"超时重连({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            except Exception as e:
                self.error_signal.emit(f"连接错误: {str(e)}")
            finally:
                # 改进资源释放逻辑
                if hasattr(self, 'cap') and self.cap.isOpened():
                    self.cap.release()
                del self.cap
                self.cap = None
                # if self.cap:
                #     self.cap.release()
                # if self.running:
                #     time.sleep(self.reconnect_interval)

    def stop(self):
        self.running = False
        self.wait(2000)

    def get_frame(self):
        with QMutexLocker(self.lock):
            return self.last_frame.copy() if self.last_frame is not None else None


class CameraController(QWidget):
    def __init__(self):
        super().__init__()
        self.timer = QTimer(self)  # 新增定时器
        self.timer.setInterval(33)  # 约30fps
        self.cap = None
        self.current_frame = None
        self.frame_mutex = QMutex()
        self.video_thread = None

        self.controller = OnvifPTZController("192.168.1.2", 8000, "admin", "system123")
        self.init_ui()
        self.setup_connections()


    # def init_video(self):
    #     self.timer.timeout.connect(self.update_frame)
    #     self.video_enabled = False

    def toggle_camera(self):
        if not self.video_thread or not self.video_thread.isRunning():
            self.start_video_stream()
            self.btn_camera.setText("停止预览")
        else:
            self.stop_video_stream()
            self.btn_camera.setText("开始预览")

    def start_video_stream(self):
        self.timer.start()  # 启动定时器
        rtsp_url = self.controller.stream_rtsp + '?transport=tcp'
        # rtsp_url = self.controller.stream_rtsp
        self.video_thread = VideoThread(rtsp_url)
        self.video_thread.frame_ready.connect(self.on_new_frame, Qt.QueuedConnection)
        self.timer.timeout.connect(self.update_display)
        self.video_thread.status_signal.connect(self.update_status)
        self.video_thread.error_signal.connect(self.handle_stream_error)
        self.video_thread.start()

    def stop_video_stream(self):
        if self.video_thread:
            self.video_thread.stop()
            self.video_label.clear()
        self.timer.stop()

    def on_new_frame(self, frame):
        # 只做必要的数据存储，显示交给定时器
        with QMutexLocker(self.video_thread.lock):
            self.current_frame = frame

    # def update_display(self):
    #     if self.current_frame is not None:
    #         # 使用硬件加速缩放
    #         rgb_image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
    #         h, w, _ = rgb_image.shape
    #         bytes_per_line = rgb_image.strides[0]
    #
    #         # 创建QImage时使用内存拷贝确保线程安全
    #         qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #
    #         # 保持宽高比缩放
    #         scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
    #             self.video_label.width(),
    #             self.video_label.height(),
    #             Qt.KeepAspectRatio,
    #             Qt.SmoothTransformation
    #         )
    #         self.video_label.setPixmap(scaled_pixmap)

    def update_display(self):
        if self.current_frame is not None:
            # 直接使用 BGR 图像，不进行重复转换
            h, w, _ = self.current_frame.shape
            bytes_per_line = self.current_frame.strides[0]

            # 使用 QImage.Format_BGR888 以避免不必要的颜色空间转换
            qt_image = QImage(self.current_frame.data, w, h, bytes_per_line, QImage.Format_BGR888)

            # 保持宽高比缩放
            scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
                self.video_label.width(),
                self.video_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.video_label.setPixmap(scaled_pixmap)

    def handle_stream_error(self, msg):
        self.status_label.setText(f"错误: {msg}")
        QTimer.singleShot(3000, self.attempt_reconnect)

    def attempt_reconnect(self):
        if not self.video_thread.isRunning():
            self.status_label.setText("尝试重新连接...")
            self.start_video_stream()

    def closeEvent(self, event):
        self.stop_video_stream()
        event.accept()






    def start_video_thread(self, rtsp_url):
        self.video_thread = VideoThread(rtsp_url)
        self.video_thread.frame_ready.connect(self.update_frame)
        self.video_thread.error_signal.connect(self.handle_video_error)
        self.video_thread.start()

    def stop_video_thread(self):
        if self.video_thread:
            self.video_thread.stop()
            self.video_label.clear()

    def update_frame(self, frame):
        self.frame_mutex.lock()
        self.current_frame = frame.copy()
        self.frame_mutex.unlock()

        # 图像处理优化
        rgb_image = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w

        # 使用硬件加速缩放
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled_pixmap = QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.video_label.setPixmap(scaled_pixmap)

    def handle_video_error(self, msg):
        self.status_label.setText(f"错误: {msg}")
        self.stop_video_thread()
        QTimer.singleShot(3000, lambda: self.start_video_thread(self.controller.stream_rtsp))

    def closeEvent(self, event):
        self.stop_video_thread()
        event.accept()

    def update_frame2(self):
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

# class VideoThread(QThread):
#     frame_ready = pyqtSignal(object)
#     status_signal = pyqtSignal(str)
#     error_signal = pyqtSignal(str)
#
#     def __init__(self, rtsp_url):
#         super().__init__()
#         self.rtsp_url = rtsp_url
#         self.running = False
#         self.cap = None
#         self.lock = QMutex()
#         self.last_frame = None
#         self.reconnect_interval = 3  # 秒
#
#     def run(self):
#         self.running = True
#         os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"
#
#         while self.running:
#             try:
#                 self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
#                 self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
#                 if not self.cap.isOpened():
#                     raise ConnectionError("无法打开视频流")
#
#                 self.status_signal.emit("视频流已连接")
#
#                 while self.running and self.cap.isOpened():
#                     ret, frame = self.cap.read()
#                     if ret:
#                         with QMutexLocker(self.lock):
#                             self.last_frame = frame.copy()
#                         self.frame_ready.emit(frame)
#                         time.sleep(0.03)
#                     else:
#                         self.error_signal.emit("视频流中断，尝试重连...")
#                         break
#             except Exception as e:
#                 self.error_signal.emit(f"连接错误: {str(e)}")
#             finally:
#                 if self.cap:
#                     self.cap.release()
#                 if self.running:
#                     time.sleep(self.reconnect_interval)
#
#     def stop(self):
#         self.running = False
#         self.wait(2000)
#
#     def get_frame(self):
#         with QMutexLocker(self.lock):
#             return self.last_frame.copy() if self.last_frame is not None else None

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
        # self.video_label = QLabel(self)
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("background-color: black;")
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
        main_layout.addLayout(left_panel, 4)  # 左侧面板（含视频）占4份空间
        # main_layout.addWidget(direction_group, 3)  # 3:1的比例
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

        self.timer.timeout.connect(self.update_display)  # 连接定时器

    def resize_video(self, event):
        if self.video_thread and self.video_thread.isRunning():
            self.update_display()  # 调用当前线程安全的显示更新方法

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
