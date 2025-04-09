import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QRadioButton, QButtonGroup,
                             QGroupBox, QSpacerItem, QSizePolicy, QDoubleSpinBox)


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能图像分析系统")
        self.setGeometry(100, 100, 1024, 768)

        # 主界面布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # 图像显示区域
        img_layout = QHBoxLayout()
        self.left_image = QLabel("原始图像区域")
        self.right_image = QLabel("分析结果区域")
        self.left_image.setStyleSheet("border: 2px solid #666; background: #fff;")
        self.right_image.setStyleSheet("border: 2px solid #666; background: #fff;")
        img_layout.addWidget(self.left_image, 5)
        img_layout.addWidget(self.right_image, 5)
        main_layout.addLayout(img_layout, 7)  # 70%高度

        # 控制面板区域
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)

        # 左侧功能选择
        left_panel = QVBoxLayout()

        # 任务输入区
        task_group = QGroupBox("任务配置")
        task_layout = QVBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入分析指令...")
        task_layout.addWidget(self.task_input)

        # 功能模式选择
        mode_group = QButtonGroup()
        self.mode_basic = QRadioButton("基本导物")
        self.mode_smart = QRadioButton("智能导物")
        self.mode_return = QRadioButton("回视模式")
        self.mode_smart.setChecked(True)
        mode_group.addButton(self.mode_basic)
        mode_group.addButton(self.mode_smart)
        mode_group.addButton(self.mode_return)
        task_layout.addWidget(self.mode_basic)
        task_layout.addWidget(self.mode_smart)
        task_layout.addWidget(self.mode_return)

        task_group.setLayout(task_layout)
        left_panel.addWidget(task_group)
        control_layout.addLayout(left_panel, 3)  # 30%宽度

        # 中间参数配置
        param_group = QGroupBox("参数设置")
        param_layout = QVBoxLayout()

        # 参数输入框
        self.param_sensitivity = QDoubleSpinBox()
        self.param_sensitivity.setValue(0.06)
        self.param_zoom = QDoubleSpinBox()
        self.param_zoom.setValue(1.1)
        self.param_threshold = QDoubleSpinBox()
        self.param_threshold.setValue(0.9)

        param_layout.addWidget(QLabel("灵敏度:"))
        param_layout.addWidget(self.param_sensitivity)
        param_layout.addWidget(QLabel("缩放比例:"))
        param_layout.addWidget(self.param_zoom)
        param_layout.addWidget(QLabel("识别阈值:"))
        param_layout.addWidget(self.param_threshold)
        param_group.setLayout(param_layout)
        control_layout.addWidget(param_group, 2)  # 20%宽度

        # 右侧操作按钮
        right_panel = QVBoxLayout()

        # 方向控制
        nav_group = QGroupBox("画面控制")
        nav_layout = QVBoxLayout()
        btn_layout = QHBoxLayout()

        self.btn_up = QPushButton("↑")
        self.btn_down = QPushButton("↓")
        self.btn_left = QPushButton("←")
        self.btn_right = QPushButton("→")
        btn_layout.addWidget(self.btn_up)
        btn_layout.addWidget(self.btn_down)
        btn_layout.addWidget(self.btn_left)
        btn_layout.addWidget(self.btn_right)

        # 缩放控制
        zoom_layout = QHBoxLayout()
        self.btn_zoom_in = QPushButton("放大+")
        self.btn_zoom_out = QPushButton("缩小-")
        zoom_layout.addWidget(self.btn_zoom_in)
        zoom_layout.addWidget(self.btn_zoom_out)

        nav_layout.addLayout(btn_layout)
        nav_layout.addLayout(zoom_layout)
        nav_group.setLayout(nav_layout)
        right_panel.addWidget(nav_group)

        # 提交按钮
        self.btn_submit = QPushButton("任务提交")
        self.btn_submit.setStyleSheet("background: #4CAF50; color: white;")
        right_panel.addWidget(self.btn_submit)

        control_layout.addLayout(right_panel, 2)  # 20%宽度

        main_layout.addWidget(control_panel, 3)  # 30%高度

        # 连接信号槽
        self._connect_events()

    def _connect_events(self):
        """连接所有UI事件"""
        self.btn_up.clicked.connect(self.on_up)
        self.btn_down.clicked.connect(self.on_down)
        self.btn_left.clicked.connect(self.on_left)
        self.btn_right.clicked.connect(self.on_right)
        self.btn_zoom_in.clicked.connect(self.on_zoom_in)
        self.btn_zoom_out.clicked.connect(self.on_zoom_out)
        self.btn_submit.clicked.connect(self.on_submit)

    # 以下为预留的槽函数接口
    def on_up(self): pass

    def on_down(self): pass

    def on_left(self): pass

    def on_right(self): pass

    def on_zoom_in(self): pass

    def on_zoom_out(self): pass

    def on_submit(self): pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec_())