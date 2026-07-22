import time
import math
import cv2
import numpy as np
import mediapipe as mp
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
from controller import SystemController

class GestureThread(QThread):
    change_pixmap_signal = Signal(QImage)
    status_signal = Signal(str)
    video_switched_signal = Signal()

    def __init__(self):
        super().__init__()
        self.running = True
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        self.last_action_time = 0
        self.cooldown = 1.2

    def run(self):
        cap = cv2.VideoCapture(0)
        self.running = True

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret or not self.running:
                break

            frame = cv2.flip(frame, 1)
            h, w, c = frame.shape
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(rgb_frame)

            current_time = time.time()

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # ----------------------------------------------------
                    # 🎨 仅新增部分：淡线条手势骨骼绘制（半透明叠加）
                    # ----------------------------------------------------
                    overlay = rgb_frame.copy()
                    
                    # 定义淡灰色、细线条样式
                    landmark_style = self.mp_draw.DrawingSpec(color=(200, 200, 200), thickness=1, circle_radius=2)
                    connection_style = self.mp_draw.DrawingSpec(color=(180, 180, 180), thickness=1)

                    # 在图层 overlay 上画出关节连线
                    self.mp_draw.draw_landmarks(
                        overlay, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        landmark_drawing_spec=landmark_style,
                        connection_drawing_spec=connection_style
                    )

                    # 35% 骨骼图层 + 65% 摄像画面融合，实现“淡线条”效果
                    rgb_frame = cv2.addWeighted(rgb_frame, 0.65, overlay, 0.35, 0)
                    # ----------------------------------------------------

                    # 提取关键点
                    landmarks = hand_landmarks.landmark
                    thumb_tip = landmarks[4]
                    thumb_mcp = landmarks[2]
                    index_tip = landmarks[8]
                    index_mcp = landmarks[5]
                    middle_tip = landmarks[12]
                    ring_tip = landmarks[16]
                    pinky_tip = landmarks[20]

                    pinch_dist = math.hypot(index_tip.x - thumb_tip.x, index_tip.y - thumb_tip.y)

                    others_folded = (
                        middle_tip.y > landmarks[9].y and 
                        ring_tip.y > landmarks[13].y and 
                        pinky_tip.y > landmarks[17].y
                    )

                    four_fingers_folded = (
                        index_tip.y > index_mcp.y and
                        middle_tip.y > landmarks[9].y and
                        ring_tip.y > landmarks[13].y and
                        pinky_tip.y > landmarks[17].y
                    )

                    if current_time - self.last_action_time > self.cooldown:
                        # 👌 点赞
                        if pinch_dist < 0.05:
                            SystemController.like_video()          
                            self.status_signal.emit("❤️ 视频点赞！") 
                            self.last_action_time = current_time

                        # 👆 上一个视频
                        elif index_tip.y < index_mcp.y - 0.15 and others_folded:
                            SystemController.prev_video()
                            self.status_signal.emit("⏫ 切上一个视频")
                            self.last_action_time = current_time

                        # 👇 下一个视频
                        elif index_tip.y > index_mcp.y + 0.15 and others_folded:
                            SystemController.next_video()
                            self.status_signal.emit("⏬ 切下一个视频")
                            self.video_switched_signal.emit()
                            self.last_action_time = current_time

                        # 👍 音量 +
                        elif thumb_tip.y < thumb_mcp.y - 0.1 and four_fingers_folded:
                            SystemController.volume_up()
                            self.status_signal.emit("🔊 音量 +")
                            self.last_action_time = current_time

                        # 👎 音量 -
                        elif thumb_tip.y > thumb_mcp.y + 0.1 and four_fingers_folded:
                            SystemController.volume_down()
                            self.status_signal.emit("🔉 音量 -")
                            self.last_action_time = current_time

            bytes_per_line = c * w
            qt_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            scaled_img = qt_img.scaled(200, 150)
            self.change_pixmap_signal.emit(scaled_img)

            time.sleep(0.03)

        cap.release()

    def stop(self):
        self.running = False
        self.wait(1000)