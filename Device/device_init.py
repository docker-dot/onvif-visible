from onvif import ONVIFCamera, ONVIFError
from typing import List, Optional, Dict, Any

IP = '192.168.1.68'
PORT = 80
USER = 'admin'
PASSWORD = 'system123'


class Device:
    """ONVIF相机控制类，封装常用操作"""

    def __init__(self, ip: str, port: int, user: str, password: str):
        """
        初始化相机连接
        Args:
            ip: 相机IP地址
            port: ONVIF服务端口，默认80
            user: 用户名
            password: 密码
            wsdl_dir: WSDL文件存放目录
        """
        try:
            self._camera = ONVIFCamera(ip, port, user, password)
            self._services_available = {}  # 缓存服务支持情况
            self._profiles = []  # 媒体profile列表
            self._current_profile = None  # 当前使用的profile
            self._ptz_service = self._camera.create_ptz_service() if self.check_service_supported('ptz') else None
            self._media_service = self._camera.create_media_service() if self.check_service_supported('media') else None
            self._device_service = self._camera.create_devicemgmt_service() if self.check_service_supported(
                'device') else None
            self._event_service = self._camera.create_events_service() if self.check_service_supported(
                'event') else None

        except ONVIFError as e:
            raise ConnectionError(f"连接相机失败: {str(e)}") from e

    def check_service_supported(self, service_name: str) -> bool:
        """检查设备是否支持某个服务"""
        if not self._services_available:
            try:
                device_info = self._camera.devicemgmt.GetServices({'IncludeCapability': True})
                self._services_available = {s.Namespace: True for s in device_info}
            except ONVIFError as e:
                raise RuntimeError("获取设备服务能力失败") from e
        return f'http://www.onvif.org/ver20/{service_name}/wsdl' in self._services_available or f'http://www.onvif.org/ver10/{service_name}/wsdl' in self._services_available

    def _check_space_supported(self, space_type: str) -> bool:
        """检查PTZ节点是否支持特定坐标空间"""
        try:
            configs = self._ptz_service.GetConfigurationOptions({
                'ConfigurationToken': self._current_profile.PTZConfiguration.token
            })

            # 空间类型与配置项的映射
            space_mapping = {
                'AbsolutePanTiltPositionSpace': configs.Spaces.AbsolutePanTiltPositionSpace,
                'ContinuousPanTiltVelocitySpace': configs.Spaces.ContinuousPanTiltVelocitySpace,
                # 其他空间类型类似处理
            }
            return bool(space_mapping.get(space_type, []))
        except ONVIFError as e:
            raise RuntimeError(f"空间支持检查失败: {str(e)}") from e

    def load_profiles(self) -> None:
        """加载所有媒体profile"""
        if not self.check_service_supported('media'):
            raise RuntimeError("设备不支持媒体服务")

        try:
            self._profiles = self._media_service.GetProfiles()
            if self._profiles:
                self._current_profile = self._profiles[0]
        except ONVIFError as e:
            raise RuntimeError(f"获取profiles失败: {str(e)}") from e

    @property
    def profiles(self) -> List:
        """获取所有可用的媒体profile"""
        return self._profiles

    def set_current_profile(self, profile_token: str) -> None:
        """设置当前使用的profile"""
        for profile in self._profiles:
            if profile.token == profile_token:
                self._current_profile = profile
                return
        raise ValueError("无效的profile token")

    def get_ptz_status(self) -> Dict[str, Any]:
        """获取PTZ当前状态"""
        if not self.check_service_supported('ptz'):
            raise RuntimeError("设备不支持PTZ服务")

        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            return self._ptz_service.GetStatus({'ProfileToken': self._current_profile.token})
        except ONVIFError as e:
            raise RuntimeError(f"获取PTZ状态失败: {str(e)}") from e

    def get_ptz_configurations(self) -> List:
        """获取所有PTZ配置"""
        if not self.check_service_supported('ptz'):
            raise RuntimeError("设备不支持PTZ服务")

        try:
            return self._ptz_service.GetConfigurations()
        except ONVIFError as e:
            raise RuntimeError(f"获取PTZ配置失败: {str(e)}") from e

    def create_preset(self, preset_name: str) -> str:
        """创建新预置位
        Args:
            preset_name: 支持中文（自动UTF-8编码）
        Returns:
            新预置位的token
        """
        try:
            req = self._ptz_service.create_type('SetPreset')
            req.ProfileToken = self._current_profile.token
            req.PresetName = preset_name.encode('utf-8')  # 强制UTF-8编码
            resp = self._ptz_service.SetPreset(req)
            return resp.PresetToken
        except ONVIFError as e:
            raise RuntimeError(f"创建预置位失败: {str(e)}") from e

    def remove_preset(self, preset_token: str) -> None:
        """删除指定预置位"""
        try:
            req = self._ptz_service.create_type('RemovePreset')
            req.ProfileToken = self._current_profile.token
            req.PresetToken = preset_token
            self._ptz_service.RemovePreset(req)
        except ONVIFError as e:
            raise RuntimeError(f"删除预置位失败: {str(e)}") from e

    def absolute_move(self, pan: float, tilt: float, zoom: float) -> None:
        """绝对位置移动（需要设备支持）"""
        if not all([
            self._check_space_supported('AbsolutePanTiltPositionSpace'),
            self._check_space_supported('AbsoluteZoomPositionSpace')
        ]):
            raise RuntimeError("设备不支持绝对坐标空间操作")
        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            req = self._ptz_service.create_type('AbsoluteMove')
            req.ProfileToken = self._current_profile.token
            req.Position = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }
            self._ptz_service.AbsoluteMove(req)
        except ONVIFError as e:
            raise RuntimeError(f"PTZ移动失败: {str(e)}") from e

    def relative_move(self, pan: float, tilt: float, zoom: float) -> None:
        """相对移动（增量位移控制）

        参数：
            pan: 水平方向相对位移（范围由设备决定，典型值-1.0到1.0）
            tilt: 垂直方向相对位移
            zoom: 变焦相对增量
        """
        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            req = self._ptz_service.create_type('RelativeMove')
            req.ProfileToken = self._current_profile.token

            # 设置相对位移向量（关键参数）
            req.Translation = {
                'PanTilt': {'x': pan, 'y': tilt},  # 水平/俯仰增量
                'Zoom': {'x': zoom}  # 变焦增量
            }

            # 可选速度控制（根据设备支持情况）
            # req.Speed = {
            #     'PanTilt': {'x': 0.5, 'y': 0.5},  # 水平/俯仰速度
            #     'Zoom': {'x': 0.3}                # 变焦速度
            # }

            self._ptz_service.RelativeMove(req)
        except ONVIFError as e:
            raise RuntimeError(f"PTZ相对移动失败: {str(e)}") from e

    def continuous_move(self, pan: float, tilt: float, zoom: float, timeout: int) -> None:
        """连续移动（速度控制）"""
        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            req = self._ptz_service.create_type('ContinuousMove')
            req.ProfileToken = self._current_profile.token
            req.Velocity = {
                'PanTilt': {'x': pan, 'y': tilt},
                'Zoom': {'x': zoom}
            }
            req.Timeout = f"PT{timeout}S"  # ISO 8601格式超时时间
            self._ptz_service.ContinuousMove(req)
        except ONVIFError as e:
            raise RuntimeError(f"PTZ移动失败: {str(e)}") from e

    def stop_move(self):
        """停止所有移动"""
        try:
            req = self._ptz_service.create_type('Stop')
            req.ProfileToken = self._current_profile.token
            req.PanTilt = True
            req.Zoom = True
            self._ptz_service.Stop(req)
        except Exception as e:
            raise RuntimeError(f"停止失败: {str(e)}") from e

    def get_presets(self) -> List[Dict]:
        """获取所有预置位"""
        req = self._ptz_service.create_type('GetPresets')
        req.ProfileToken = self._current_profile.token
        presets = self._ptz_service.GetPresets(req)
        return [{'token': p.token, 'name': p.Name} for p in presets]

    def goto_preset(self, preset_token: str):
        """跳转到指定预置位"""
        req = self._ptz_service.create_type('GotoPreset')
        req.ProfileToken = self._current_profile.token
        req.PresetToken = preset_token
        self._ptz_service.GotoPreset(req)

    def get_snapshot_uri(self) -> Optional[str]:
        """获取快照URL"""
        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            return self._media_service.GetSnapshotUri({'ProfileToken': self._current_profile.token})
        except ONVIFError as e:
            raise RuntimeError(f"获取快照URI失败: {str(e)}") from e


# # 使用示例
# if __name__ == '__main__':
#     IP = '192.168.1.68'
#     PORT = 80
#     USER = 'admin'
#     PASSWORD = 'system123'
#     try:
#         # 初始化连接
#         camera = ONVIFCameraController(
#             ip=IP,
#             port=PORT,
#             user=USER,
#             password=PASSWORD
#             # wsdl_dir='../wsdl/'
#         )
#
#         # 加载profiles
#         camera.load_profiles()
#
#         # 获取PTZ状态
#         status = camera.get_ptz_status()
#         print(f"当前PTZ状态: {status}")
#
#         # 打印所有profile
#         print("可用profiles:")
#         for profile in camera.profiles:
#             print(f" - {profile.Name} (Token: {profile.token})")
#
#         # 获取快照地址
#         snapshot_uri = camera.get_snapshot_uri()
#         print(f"快照URL: {snapshot_uri}")
#
#     except Exception as e:
#         print(f"发生错误: {str(e)}")
