from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QLabel,
    QFrame, QApplication
)
from PySide6.QtGui import QPixmap
from controller import SystemController


class FloatingAssistant(QWidget):
    def __init__(self):
        super().__init__()

        self.video_count = 0
        self.is_collapsed = False
        self.drag_position = QPoint()
        self.thread = None

        self.init_ui()

    def init_ui(self):
        # 无边框 + 置顶 + 工具窗口
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )

        self.setAttribute(Qt.WA_TranslucentBackground)

        self.main_frame = QFrame(self)
        self.main_frame.setStyleSheet("""
            QFrame{
                background-color:rgba(30,30,30,220);
                border-radius:12px;
                color:white;
            }

            QLineEdit{
                background-color:rgba(255,255,255,30);
                border:1px solid #555;
                border-radius:4px;
                color:white;
                padding:4px;
            }

            QPushButton{
                background-color:#007ACC;
                color:white;
                border:none;
                border-radius:4px;
                padding:4px 8px;
            }

            QPushButton:hover{
                background:#0098FF;
            }
        """)

        self.layout = QVBoxLayout(self.main_frame)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # ===================== 顶部 =====================
        top_bar = QHBoxLayout()

        self.title_label = QLabel("🎬 刷视频手势助手")
        self.title_label.setStyleSheet(
            "font-weight:bold;font-size:13px;"
        )

        self.toggle_btn = QPushButton("➖ 隐藏摄像头")
        self.toggle_btn.setFocusPolicy(Qt.NoFocus)
        self.toggle_btn.clicked.connect(self.toggle_collapse)

        self.close_btn = QPushButton("❌")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setFocusPolicy(Qt.NoFocus)

        self.close_btn.setStyleSheet("""
            QPushButton{
                background:#FF4D4D;
                color:white;
                border:none;
                border-radius:4px;
                font-weight:bold;
            }

            QPushButton:hover{
                background:#FF1A1A;
            }
        """)

        self.close_btn.clicked.connect(self.close)

        top_bar.addWidget(self.title_label)
        top_bar.addStretch()
        top_bar.addWidget(self.toggle_btn)
        top_bar.addWidget(self.close_btn)

        self.layout.addLayout(top_bar)

        # ===================== 输入框 =====================
        self.url_container = QWidget()

        url_layout = QHBoxLayout(self.url_container)
        url_layout.setContentsMargins(0, 0, 0, 0)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("粘贴抖音/B站网址...")
        self.url_input.returnPressed.connect(self.on_open_url)

        self.go_btn = QPushButton("跳转")
        self.go_btn.setFocusPolicy(Qt.NoFocus)
        self.go_btn.clicked.connect(self.on_open_url)

        url_layout.addWidget(self.url_input)
        url_layout.addWidget(self.go_btn)

        self.layout.addWidget(self.url_container)

        # ===================== 摄像头 =====================
        self.cam_label = QLabel("启动摄像头中...")
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setFixedHeight(120)

        self.cam_label.setStyleSheet("""
            background:black;
            border-radius:6px;
        """)

        self.layout.addWidget(self.cam_label)

        # ===================== 信息 =====================
        self.count_label = QLabel("已看视频：0 个")
        self.count_label.setStyleSheet(
            "color:#00FFCC;font-weight:bold;"
        )

        self.status_label = QLabel("状态：等待手势指令...")
        self.status_label.setStyleSheet(
            "color:#AAA;font-size:11px;"
        )

        self.layout.addWidget(self.count_label)
        self.layout.addWidget(self.status_label)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.main_frame)

        self.resize(250, 280)

    # ======================================================
    # 打开网址
    # ======================================================

    def on_open_url(self):
        url = self.url_input.text().strip()

        if url:
            SystemController.open_url(url)

            self.url_input.clearFocus()
            self.clearFocus()

            # 等网页加载
            QTimer.singleShot(
                3500,
                self.auto_play_video
            )

    def auto_play_video(self):
        """网页打开后自动播放"""

        self.clearFocus()

        SystemController.play_video()

    # ======================================================
    # 更新画面
    # ======================================================

    def update_camera_preview(self, q_img):

        if not self.is_collapsed:
            self.cam_label.setPixmap(
                QPixmap.fromImage(q_img)
            )

    def update_status(self, text):
        self.status_label.setText(f"状态：{text}")

    def increment_video_count(self):
        self.video_count += 1
        self.count_label.setText(
            f"已看视频：{self.video_count} 个"
        )

    # ======================================================
    # 折叠
    # ======================================================

    def toggle_collapse(self):

        if self.is_collapsed:

            self.cam_label.show()

            self.toggle_btn.setText(
                "➖ 隐藏摄像头"
            )

            self.resize(250, 280)

            self.is_collapsed = False

        else:

            self.cam_label.hide()

            self.toggle_btn.setText(
                "📷 显示摄像头"
            )

            self.adjustSize()

            self.resize(250, 140)

            self.is_collapsed = True

        self.clearFocus()

        # 100ms 后把焦点交还给浏览器
        QTimer.singleShot(
            100,
            SystemController.activate_browser
        )

    # ======================================================
    # 拖动窗口
    # ======================================================

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )

            event.accept()

    def mouseMoveEvent(self, event):

        if event.buttons() == Qt.LeftButton:

            self.move(
                event.globalPosition().toPoint()
                - self.drag_position
            )

            event.accept()

    # ======================================================
    # 关闭
    # ======================================================

    def closeEvent(self, event):

        if self.thread and self.thread.isRunning():
            self.thread.stop()

        event.accept()
        QApplication.quit()