# /onvif-visible/main
import sys
from PyQt5.QtWidgets import QApplication

from UI.qt_main import CameraController


def main():
    # 创建Qt应用
    app = QApplication(sys.argv)

    try:
        # 创建控制器窗口
        window = CameraController()
        window.show()

        # 异常处理（示例）
        if not window.controller.is_connected():
            raise ConnectionError("无法连接摄像头")

    except Exception as e:
        print(f"初始化失败: {str(e)}")
        return 1

    # 启动事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
