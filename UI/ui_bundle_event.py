from UIconnect.device_driver_controller import *
from UIconnect.show_video_controller import *
from UIconnect.middle_controller import *

"""
这是接口代码，定义了不同任务和控制
摄像头有两个
"""


class MainWindowBundleEvent:
    def __init__(self, ui_main_window):
        # SDK视频流
        show_widget_number = int(ui_main_window.show_widget.winId())
        show_visible_controller(show_widget_number)
        # 截图按钮功能
        show_screenshot(ui_main_window.pushButton_screenshot, ui_main_window.graph_view)
        # 视频流变焦放大
        visible_zoomin_controller(ui_main_window.pushButton_ZoomIn)
        # 视频流变焦缩小
        visible_zoomout_controller(ui_main_window.pushButton_ZoomOut)
        # 摄像头向上转动
        up_rotation_controller(ui_main_window.pushButton_Up)
        # 摄像头向下转动
        down_rotation_controller(ui_main_window.pushButton_Down)
        # 摄像头向左转动
        left_rotation_controller(ui_main_window.pushButton_Left)
        # 摄像头向右转动
        right_rotation_controller(ui_main_window.pushButton_Right)
        # 基本寻物
        base_find_connect(ui_main_window.basefind_radioButton, ui_main_window.textEdit, ui_main_window.graph_view,ui_main_window.additional_widget,
                          ui_main_window.submit_llm)
        base_allfind_connect(ui_main_window.baseallfind_radioButton, ui_main_window.textEdit, ui_main_window.graph_view,
                             ui_main_window.submit_llm)
        base_find_one_class_connect(ui_main_window.agentfind_radioButton, ui_main_window.textEdit,
                                    ui_main_window.graph_view,ui_main_window.additional_widget,
                                    ui_main_window.submit_llm)
