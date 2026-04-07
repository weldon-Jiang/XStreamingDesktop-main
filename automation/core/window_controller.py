"""
窗口控制模块 - 控制 XStreaming 窗口
"""
import subprocess
import time
import logging
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class WindowState(Enum):
    NOT_FOUND = "not_found"
    MINIMIZED = "minimized"
    NORMAL = "normal"
    MAXIMIZED = "maximized"
    FULLSCREEN = "fullscreen"


@dataclass
class WindowInfo:
    hwnd: int
    title: str
    state: WindowState
    rect: tuple


class WindowController:
    """窗口控制器"""

    def __init__(self, window_title: str = "XStreaming"):
        self.window_title = window_title
        self._hwnd = None

    def find_window(self) -> Optional[WindowInfo]:
        """查找窗口"""
        try:
            import win32gui
            import win32con

            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title and self.window_title.lower() == title.lower():
                        rect = win32gui.GetWindowRect(hwnd)
                        state = self._get_window_state(hwnd)
                        windows.append(WindowInfo(
                            hwnd=hwnd,
                            title=title,
                            state=state,
                            rect=rect
                        ))
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)

            if windows:
                self._hwnd = windows[0].hwnd
                return windows[0]

            return None

        except ImportError:
            logger.warning("pywin32 未安装，窗口控制功能受限")
            return None
        except Exception as e:
            logger.error(f"查找窗口失败: {e}")
            return None

    def _get_window_state(self, hwnd: int) -> WindowState:
        """获取窗口状态"""
        try:
            import win32gui
            if win32gui.IsIconic(hwnd):
                return WindowState.MINIMIZED
            elif win32gui.IsZoomed(hwnd):
                return WindowState.MAXIMIZED
            return WindowState.NORMAL
        except:
            return WindowState.NORMAL

    def bring_to_front(self) -> bool:
        """将窗口置前"""
        window = self.find_window()
        if window:
            try:
                import win32gui
                import win32con
                win32gui.ShowWindow(window.hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(window.hwnd)
                time.sleep(0.5)
                logger.info(f"窗口已置前: {window.title}")
                return True
            except Exception as e:
                logger.error(f"置前窗口失败: {e}")
        return False

    def maximize(self) -> bool:
        """最大化窗口"""
        window = self.find_window()
        if window:
            try:
                import win32gui
                import win32con
                win32gui.ShowWindow(window.hwnd, win32con.SW_MAXIMIZE)
                logger.info("窗口已最大化")
                return True
            except Exception as e:
                logger.error(f"最大化窗口失败: {e}")
        return False

    def minimize(self) -> bool:
        """最小化窗口"""
        window = self.find_window()
        if window:
            try:
                import win32gui
                import win32con
                win32gui.ShowWindow(window.hwnd, win32con.SW_MINIMIZE)
                logger.info("窗口已最小化")
                return True
            except Exception as e:
                logger.error(f"最小化窗口失败: {e}")
        return False

    def restore(self) -> bool:
        """恢复窗口"""
        window = self.find_window()
        if window:
            try:
                import win32gui
                import win32con
                win32gui.ShowWindow(window.hwnd, win32con.SW_RESTORE)
                logger.info("窗口已恢复")
                return True
            except Exception as e:
                logger.error(f"恢复窗口失败: {e}")
        return False

    def is_window_exists(self) -> bool:
        """检查窗口是否存在"""
        return self.find_window() is not None

    def wait_for_window(self, timeout: int = 60, interval: float = 1.0) -> bool:
        """等待窗口出现"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_window_exists():
                logger.info("窗口已出现")
                return True
            time.sleep(interval)

        logger.warning(f"等待窗口超时: {timeout}秒")
        return False

    def get_window_position(self) -> Optional[tuple]:
        """获取窗口位置"""
        window = self.find_window()
        if window:
            return window.rect
        return None

    def click_at_position(self, x: int, y: int, button: str = "left") -> bool:
        """在窗口指定位置点击"""
        try:
            import win32gui
            import win32api
            import win32con

            window = self.find_window()
            if not window:
                return False

            rect = window.rect
            rel_x = x + rect[0]
            rel_y = y + rect[1]

            win32api.SetCursorPos((rel_x, rel_y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            time.sleep(0.05)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

            logger.info(f"点击坐标: ({rel_x}, {rel_y})")
            return True

        except Exception as e:
            logger.error(f"点击坐标失败: {e}")
            return False


class AppLauncher:
    """应用程序启动器"""

    def __init__(self, app_path: str, app_command: str = None):
        self.app_path = Path(app_path)
        self.app_command = app_command or 'npm run dev'

        if not self.app_path.exists():
            raise FileNotFoundError(f"应用路径不存在: {app_path}")

    def launch(self) -> subprocess.Popen:
        """启动应用"""
        try:
            logger.info(f"启动应用: {self.app_path}")
            logger.info(f"执行命令: {self.app_command}")

            process = subprocess.Popen(
                self.app_command,
                shell=True,
                cwd=str(self.app_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            logger.info(f"应用已启动, PID: {process.pid}")

            import threading
            def read_output(pipe, name):
                import codecs
                reader = codecs.getreader('utf-8')(pipe, errors='replace')
                for line in iter(reader.readline, ''):
                    if line:
                        logger.info(f"[{name}] {line.strip()}")

            stdout_thread = threading.Thread(target=read_output, args=(process.stdout, "stdout"))
            stderr_thread = threading.Thread(target=read_output, args=(process.stderr, "stderr"))
            stdout_thread.daemon = True
            stderr_thread.daemon = True
            stdout_thread.start()
            stderr_thread.start()

            return process

        except Exception as e:
            logger.error(f"启动应用失败: {e}")
            raise

    def is_running(self) -> bool:
        """检查应用是否在运行"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline)
                if 'nextron' in cmdline_str.lower() or 'electron' in cmdline_str.lower():
                    return True
            return False
        except ImportError:
            logger.warning("psutil 未安装，无法检测进程")
            return True

    def terminate(self) -> bool:
        """终止应用"""
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                cmdline = proc.info.get('cmdline') or []
                cmdline_str = ' '.join(cmdline)
                if 'nextron' in cmdline_str.lower() or 'electron' in cmdline_str.lower():
                    proc.terminate()
                    proc.wait(timeout=10)
                    logger.info(f"已终止进程: {proc.pid}")
            return True
        except ImportError:
            logger.warning("psutil 未安装，无法终止进程")
            return False
        except Exception as e:
            logger.error(f"终止应用失败: {e}")
            return False