import subprocess
import threading
import time

class NotificationManager:
    """
    处理GUI通知功能的类
    """
    
    def __init__(self):
        """初始化通知管理器"""
        self.active_notifications = []
        
    def show_notification(self, title, message, auto_close_seconds=120):
        """
        显示一个通知弹窗
        
        参数:
            title: 弹窗标题
            message: 弹窗内容
            auto_close_seconds: 自动关闭时间(秒)，默认2分钟
        """
        # 创建一个新线程来显示通知，避免阻塞主线程
        notification_thread = threading.Thread(
            target=self._show_notification_window,
            args=(title, message, auto_close_seconds)
        )
        notification_thread.daemon = True  # 设置为守护线程，这样主程序退出时线程也会退出
        notification_thread.start()
        
        # 将线程添加到活动通知列表中
        self.active_notifications.append(notification_thread)
        
    def _show_notification_window(self, title, message, auto_close_seconds):
        """
        内部方法：显示通知窗口并在指定时间后自动关闭
        使用macOS的原生对话框
        """
        # 使用AppleScript显示对话框，设置自动关闭时间
        applescript = f'''
        display dialog "{message}" with title "{title}" buttons {{"确定"}} default button "确定" giving up after {auto_close_seconds}
        '''
        
        try:
            subprocess.run(["osascript", "-e", applescript])
        except Exception as e:
            print(f"显示通知失败: {e}")

# 使用示例
if __name__ == "__main__":
    notifier = NotificationManager()
    notifier.show_notification(
        "512980", 
        "512980 在 15min线 周期当前价格持续在10日均线上方",
        30  # 30秒后自动关闭
    )
    
    # 保持主程序运行，以便看到通知效果
    print("通知已发送，主程序继续运行...")
    time.sleep(60)  # 主程序等待60秒后退出