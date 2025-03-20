from onvif import ONVIFCamera, ONVIFError
from typing import List, Optional, Dict, Any


class ONVIFCameraController:
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

    def load_profiles(self) -> None:
        """加载所有媒体profile"""
        if not self.check_service_supported('media'):
            raise RuntimeError("设备不支持媒体服务")

        try:
            media_service = self._camera.create_media_service()
            self._profiles = media_service.GetProfiles()
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
            ptz_service = self._camera.create_ptz_service()
            return ptz_service.GetStatus({'ProfileToken': self._current_profile.token})
        except ONVIFError as e:
            raise RuntimeError(f"获取PTZ状态失败: {str(e)}") from e

    def get_ptz_configurations(self) -> List:
        """获取所有PTZ配置"""
        if not self.check_service_supported('ptz'):
            raise RuntimeError("设备不支持PTZ服务")

        try:
            ptz_service = self._camera.create_ptz_service()
            return ptz_service.GetConfigurations()
        except ONVIFError as e:
            raise RuntimeError(f"获取PTZ配置失败: {str(e)}") from e

    def absolute_move(self, pan: float, tilt: float, zoom: float) -> None:
        """绝对位置移动（需要设备支持）"""
        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            ptz_service = self._camera.create_ptz_service()
            req = ptz_service.create_type('AbsoluteMove')
            req.ProfileToken = self._current_profile.token
            req.Position = {'PanTilt': {'x': pan, 'y': tilt}, 'Zoom': zoom}
            ptz_service.AbsoluteMove(req)
        except ONVIFError as e:
            raise RuntimeError(f"PTZ移动失败: {str(e)}") from e

    def get_snapshot_uri(self) -> Optional[str]:
        """获取快照URL"""
        if not self._current_profile:
            raise RuntimeError("未选择媒体profile")

        try:
            media_service = self._camera.create_media_service()
            return media_service.GetSnapshotUri({'ProfileToken': self._current_profile.token})
        except ONVIFError as e:
            raise RuntimeError(f"获取快照URI失败: {str(e)}") from e


# 使用示例
if __name__ == '__main__':
    try:
        # 初始化连接
        camera = ONVIFCameraController(
            ip='192.168.1.68',
            port=80,
            user='admin',
            password='system123'
            # wsdl_dir='../wsdl/'
        )

        # 加载profiles
        camera.load_profiles()

        # 获取PTZ状态
        status = camera.get_ptz_status()
        print(f"当前PTZ状态: {status}")

        # 打印所有profile
        print("可用profiles:")
        for profile in camera.profiles:
            print(f" - {profile.Name} (Token: {profile.token})")

        # 获取快照地址
        snapshot_uri = camera.get_snapshot_uri()
        print(f"快照URL: {snapshot_uri}")

    except Exception as e:
        print(f"发生错误: {str(e)}")
