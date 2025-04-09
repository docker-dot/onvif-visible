import sys
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt


class BeachAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主容器
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # 主布局（垂直）
        main_layout = QVBoxLayout(main_widget)

        # 图像区域 ----------------------------------------
        img_layout = QHBoxLayout()

        # 原始图像面板
        self.original_img = QLabel()
        self.original_img.setPixmap(QPixmap("beach.jpg").scaled(600, 400))
        self.original_img.setFrameShape(QFrame.Shape.Box)
        img_layout.addWidget(self.original_img)

        # 处理后的图像面板
        self.processed_img = QLabel()
        self.processed_img.setPixmap(QPixmap("beach_processed.jpg").scaled(600, 400))
        self.processed_img.setFrameShape(QFrame.Shape.Box)
        img_layout.addWidget(self.processed_img)

        main_layout.addLayout(img_layout)

        # 控制面板 ----------------------------------------
        control_layout = QHBoxLayout()

        # 参数设置列
        params_group = QGroupBox("检测参数")
        param_layout = QFormLayout()
        self.confidence = QDoubleSpinBox()
        self.confidence.setValue(0.06)
        self.scale_factor = QDoubleSpinBox()
        self.scale_factor.setValue(1.1)
        self.threshold = QDoubleSpinBox()
        self.threshold.setValue(0.9)

        param_layout.addRow("置信度:", self.confidence)
        param_layout.addRow("缩放因子:", self.scale_factor)
        param_layout.addRow("阈值:", self.threshold)
        params_group.setLayout(param_layout)
        control_layout.addWidget(params_group)

        # 功能选择列
        func_group = QGroupBox("工作模式")
        func_layout = QVBoxLayout()

        # 检测模式
        detect_group = QButtonGroup(self)
        self.basic_detect = QRadioButton("基本功能")
        self.smart_detect = QRadioButton("智能导播")
        detect_group.addButton(self.basic_detect)
        detect_group.addButton(self.smart_detect)
        func_layout.addWidget(QLabel("检测模式:"))
        func_layout.addWidget(self.basic_detect)
        func_layout.addWidget(self.smart_detect)

        # 操作模式
        func_layout.addSpacing(15)
        op_group = QButtonGroup(self)
        self.zoom_in = QRadioButton("画面变大")
        self.zoom_out = QRadioButton("画面变小")
        op_group.addButton(self.zoom_in)
        op_group.addButton(self.zoom_out)
        func_layout.addWidget(QLabel("显示控制:"))
        func_layout.addWidget(self.zoom_in)
        func_layout.addWidget(self.zoom_out)

        func_group.setLayout(func_layout)
        control_layout.addWidget(func_group)

        # 方向控制
        nav_group = QGroupBox("导航控制")
        grid = QGridLayout()
        self.up_btn = QPushButton("↑")
        self.down_btn = QPushButton("↓")
        self.left_btn = QPushButton("←")
        self.right_btn = QPushButton("→")
        grid.addWidget(self.up_btn, 0, 1)
        grid.addWidget(self.left_btn, 1, 0)
        grid.addWidget(self.right_btn, 1, 2)
        grid.addWidget(self.down_btn, 2, 1)
        nav_group.setLayout(grid)
        control_layout.addWidget(nav_group)

        main_layout.addLayout(control_layout)

        # 任务提示栏 ----------------------------------------
        task_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入任务提示...")
        self.voice_btn = QPushButton("🎤")
        self.voice_btn.setFixedSize(40, 30)
        task_layout.addWidget(self.task_input)
        task_layout.addWidget(self.voice_btn)
        main_layout.addLayout(task_layout)

        # 窗口设置
        self.setWindowTitle('沙滩场景分析系统')
        self.setMinimumSize(1280, 800)
        self.setStyleSheet("""
            QGroupBox { 
                border: 1px solid gray; 
                margin-top: 10px;
                font: bold 10pt;
            }
            QLabel { 
                font: 10pt; 
            }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BeachAnalysisApp()
    ex.show()
    sys.exit(app.exec())