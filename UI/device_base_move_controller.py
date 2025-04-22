from Device.device_init import Device
from base_service.base_control import *

device = Device()


def visible_zoomin_controller(visible_up):
    visible_up.pressed.connect(lambda: start_zoomin(device))
    visible_up.released.connect(lambda: stop_move(device))


# 可见光视频流变焦缩小
def visible_zoomout_controller(visible_down):
    visible_down.pressed.connect(lambda: start_zoomout(device))
    visible_down.released.connect(lambda: stop_move(device))


# 摄像头向上转动
def up_rotation_controller(up_rotation):
    up_rotation.pressed.connect(lambda: start_up(device))
    up_rotation.released.connect(lambda: stop_move(device))


# 摄像头向下转动
def down_rotation_controller(down_rotation):
    down_rotation.pressed.connect(lambda: start_down(device))
    down_rotation.released.connect(lambda: stop_move(device))


# 摄像头向左转动
def left_rotation_controller(left_rotation):
    left_rotation.pressed.connect(lambda: start_left(device))
    left_rotation.released.connect(lambda: stop_move(device))


# 摄像头向右转动
def right_rotation_controller(right_rotation):
    right_rotation.pressed.connect(lambda: start_right(device))
    right_rotation.released.connect(lambda: stop_move(device))


# 摄像头向左上转动
def up_left_rotation_controller(up_rotation):
    up_rotation.pressed.connect(lambda: start_left_up(device))
    up_rotation.released.connect(lambda: stop_move(device))


# 摄像头向下转动
def down_rotation_controller(down_rotation):
    down_rotation.pressed.connect(lambda: start_down(device))
    down_rotation.released.connect(lambda: stop_move(device))


# 摄像头向左转动
def left_rotation_controller(left_rotation):
    left_rotation.pressed.connect(lambda: start_left(device))
    left_rotation.released.connect(lambda: stop_move(device))


# 摄像头向右转动
def right_rotation_controller(right_rotation):
    right_rotation.pressed.connect(lambda: start_right(device))
    right_rotation.released.connect(lambda: stop_move(device))
