# Device/onvif_ptz_controller.py
from urllib.error import URLError
from urllib.parse import urlsplit, quote_plus, urlunsplit

from onvif import ONVIFCamera
from PyQt5.QtCore import QObject, pyqtSignal


class OnvifPTZController(QObject):  # 必须继承QObject
    """独立的PTZ控制类，不依赖任何界面组件"""
    status_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, ip, port, user, passwd):
        super().__init__()  # 需要调用父类构造函数
        self.is_connected = False
        self._media_service = None
        self.profile_tokens = None
        self._current_profile = None
        self.ptz = None
        self.stream_rtsp = None
        self._init_device(ip, port, user, passwd)
        self.pt_speed = 0.5
        self.zoom_speed = 0.5

    def _init_device(self, ip, port, user, passwd):
        """设备初始化"""
        try:
            self.camera = ONVIFCamera(
                ip,
                port,
                user,
                passwd
            )
            self._media_service = self.camera.create_media_service()
            self.profile_tokens = self._media_service.GetProfiles()
            self._current_profile = self.profile_tokens[0].token
            self.ptz = self.camera.create_ptz_service()
            self.is_connected = True
            self.stream_rtsp = self.get_rtsp_stream(user, passwd)
            print(self.stream_rtsp)
        except Exception as e:
            raise ConnectionError(f"设备连接失败: {str(e)}")

    def get_rtsp_stream(self, user, passwd):
        # stream_uri = media_service.GetStreamUri({
        #     'StreamSetup': {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}},
        #     'ProfileToken': profile.token  # 使用第一个Profile（通常是红外模式） 这里需要修改为红外的profile的token
        # })
        try:
            # 获取第一个 Profile 的 RTSP 地址
            request = self._media_service.create_type('GetStreamUri')
            request.ProfileToken = self._current_profile
            request.StreamSetup = {'Stream': 'RTP-Unicast', 'Transport': {'Protocol': 'RTSP'}}

            stream_uri = self._media_service.GetStreamUri(request)['Uri']
            # return stream_uri[0:7] + user + ':' + passwd + '@' + stream_uri[7:]

            try:
                # 分解原始URL组件
                parts = urlsplit(stream_uri)

                # 编码含特殊字符的密码（如 +/@# 等）
                safe_password = quote_plus(passwd, safe='')

                # 重构网络地址部分（插入认证信息）
                new_netloc = f"{user}:{safe_password}@{parts.netloc}"

                # 替换网络地址并保留其他组件
                new_parts = parts._replace(netloc=new_netloc)

                final_parts = new_parts._replace()

                return urlunsplit(final_parts)
            except (AttributeError, ValueError) as e:
                raise URLError(f"URL解析失败: {str(e)}") from e

        except Exception as e:
            print(f"获取 RTSP 流失败: {str(e)}")


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

    def start_up_left(self):
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
            request.ProfileToken = self._current_profile
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
            request.ProfileToken = self._current_profile
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
                stop_request.ProfileToken = self._current_profile
                stop_request.PanTilt = True
                stop_request.Zoom = True
                self.ptz.Stop(stop_request)
                self.status_signal.emit("已停止所有运动")
            except Exception as e:
                self.error_signal.emit(f"停止失败: {str(e)}")

    def get_snapshot_uri(self):
        """获取快照URL"""
        if not self._current_profile:
            self.error_signal.emit("未选择媒体profile")

        try:
            return self._media_service.GetSnapshotUri({'ProfileToken': self._current_profile.token})
        except Exception as e:
            self.error_signal.emit(f"获取快照URI失败: {str(e)}")
