# controller.py
import time
import pyautogui
import webbrowser

class SystemController:
    @staticmethod
    def open_url(url: str):
        """调用默认浏览器打开链接"""
        if url:
            if not url.startswith("http"):
                url = "https://" + url
            webbrowser.open(url)

    @staticmethod
    def next_video():
        """切换下一个视频 (抖音/B站网页版通用 '↓' 键)"""
        pyautogui.press('down')

    @staticmethod
    def prev_video():
        """切换上一个视频 ('↑' 键)"""
        pyautogui.press('up') 

    @staticmethod
    def like_video():
        """点赞视频 (双击空格键模式)"""
        # 1. 第 1 次按下空格
        pyautogui.press('space')
        # 2. 极短间隔（模拟快速双击）
        time.sleep(0.08)
        # 3. 第 2 次按下空格
        pyautogui.press('space')

    @staticmethod
    def volume_up():
        """增大系统音量 (直接触发系统多媒体键)"""
        # 连按两次可以每次调大明显一些
        pyautogui.press('volumeup')
        pyautogui.press('volumeup')

    @staticmethod
    def volume_down():
        """减小系统音量 (直接触发系统多媒体键)"""
        pyautogui.press('volumedown')
        pyautogui.press('volumedown')

    @staticmethod
    def activate_browser():
        """
        点击视频区域，把焦点切回浏览器
        不会播放/暂停视频
        """
        screen_w, screen_h = pyautogui.size()

        target_x = int(screen_w * 0.40)
        target_y = int(screen_h * 0.40)

        pyautogui.click(target_x, target_y)

    @staticmethod
    def play_video():
        """
        激活浏览器后开始播放视频
        """
        SystemController.activate_browser()
        time.sleep(0.1)
        pyautogui.press("space")
