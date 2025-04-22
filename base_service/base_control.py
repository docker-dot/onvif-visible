# 云台方向控制方法
def start_up(self):
    """向上移动"""
    self._move_ptz(0, self.pt_speed)


def start_down(self):
    """向下移动"""
    self._move_ptz(0, -self.pt_speed)


def start_right(self):
    """向右移动"""
    self._move_ptz(self.pt_speed, 0)


def start_left(self):
    """向左移动"""
    self._move_ptz(-self.pt_speed, 0)


def start_left_up(self):
    """左上移动"""
    self._move_ptz(-self.pt_speed, self.pt_speed)


def start_down_left(self):
    """左下移动"""
    self._move_ptz(-self.pt_speed, -self.pt_speed)


def start_up_right(self):
    """右上移动"""
    self._move_ptz(self.pt_speed, self.pt_speed)


def start_down_right(self):
    """右下移动"""
    self._move_ptz(self.pt_speed, -self.pt_speed)


# 变焦控制方法
def start_zoomin(self):
    """变焦放大"""
    self._move_zoom(self.zoom_speed)


def start_zoomout(self):
    """变焦缩小"""
    self._move_zoom(-self.zoom_speed)


# 通用控制方法
def _move_ptz(self, pan_speed, tilt_speed):
    """通用云台移动方法
    :param pan_speed: 水平速度 [-1,1]（右正左负）
    :param tilt_speed: 垂直速度 [-1,1]（上正下负）
    """
    if not self.ptz:
        self.error_signal.emit("PTZ服务未初始化")
        return

    try:
        request = self.ptz.create_type('ContinuousMove')
        request.ProfileToken = self.profile_token
        request.Velocity = {
            "PanTilt": {"x": pan_speed, "y": tilt_speed},
            "Zoom": 0
        }
        self.ptz.ContinuousMove(request)
        self.status_signal.emit(f"开始移动：Pan={pan_speed}, Tilt={tilt_speed}")
    except Exception as e:
        self.error_signal.emit(f"移动失败: {str(e)}")


def _move_zoom(self, zoom_speed):
    """通用变焦控制方法
    :param zoom_speed: 变焦速度 [-1,1]（正值放大，负值缩小）
    """
    if not self.ptz:
        self.error_signal.emit("PTZ服务未初始化")
        return

    try:
        request = self.ptz.create_type('ContinuousMove')
        request.ProfileToken = self.profile_token
        request.Velocity = {
            "PanTilt": {"x": 0, "y": 0},
            "Zoom": zoom_speed
        }
        self.ptz.ContinuousMove(request)
        self.status_signal.emit(f"开始变焦：Zoom={zoom_speed}")
    except Exception as e:
        self.error_signal.emit(f"变焦失败: {str(e)}")


def stop_move(self):
    """停止所有运动"""
    if self.ptz:
        try:
            stop_request = self.ptz.create_type('Stop')
            stop_request.ProfileToken = self.profile_token
            stop_request.PanTilt = True
            stop_request.Zoom = True
            self.ptz.Stop(stop_request)
            self.status_signal.emit("已停止所有运动")
        except Exception as e:
            self.error_signal.emit(f"停止失败: {str(e)}")


def start_zoomin(self):
    """ONVIF协议实现变焦放大的槽函数"""
    if not self.ptz:
        self.error_signal.emit("PTZ服务未初始化")
        return

    try:
        # 创建连续移动请求
        request = self.ptz.create_type('ContinuousMove')
        request.ProfileToken = self.profile_token

        # 设置缩放速度（正值放大）
        request.Velocity = {
            "Zoom": self.zoom_speed,
            "PanTilt": {"x": 0, "y": 0}  # 保持云台静止
        }

        # 发送控制命令
        self.ptz.ContinuousMove(request)
        self.status_signal.emit("开始变焦放大")  #

    except Exception as e:
        self.error_signal.emit(f"控制失败: {str(e)}")


