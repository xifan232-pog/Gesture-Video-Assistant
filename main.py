import sys
from PySide6.QtWidgets import QApplication
from ges_ui import FloatingAssistant
from ges_thread import GestureThread

def main():
    app = QApplication(sys.argv)
    
    # 初始化 UI 与 后台手势识别线程
    assistant = FloatingAssistant()
    thread = GestureThread()

    # 将线程绑定到 assistant 实例上，方便 closeEvent 中进行关闭
    assistant.thread = thread

    # 绑定信号与槽 (Signal -> Slot)
    thread.change_pixmap_signal.connect(assistant.update_camera_preview)
    thread.status_signal.connect(assistant.update_status)
    thread.video_switched_signal.connect(assistant.increment_video_count)

    # 启动界面和线程
    assistant.show()
    thread.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()