"""
串流自动化模块
"""
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import UIDetector, WindowController, AppLauncher
from core.base_automation import BaseAutomation

logger = logging.getLogger(__name__)


class StreamState:
    IDLE = "idle"
    STARTING_APP = "starting_app"
    WAITING_FOR_WINDOW = "waiting_for_window"
    WAITING_FOR_HOME = "waiting_for_home"
    SELECTING_CONSOLE = "selecting_console"
    STARTING_STREAM = "starting_stream"
    WAITING_FOR_STREAM = "waiting_for_stream"
    STREAM_CONNECTED = "stream_connected"
    FAILED = "failed"


class StreamAutomation(BaseAutomation):
    """串流自动化控制器"""

    def __init__(self, ui_detector: UIDetector, window_controller: WindowController,
                 app_launcher: AppLauncher, timeout: dict):
        """
        初始化串流自动化

        Args:
            ui_detector: UI 检测器实例
            window_controller: 窗口控制器
            app_launcher: 应用启动器
            timeout: 超时配置 dict
        """
        super().__init__(ui_detector)
        self.window_controller = window_controller  # 窗口控制器
        self.app_launcher = app_launcher           # 应用启动器
        self.timeout = timeout                    # 超时配置

    def terminate(self, reason: str = ""):
        """终止串流流程"""
        super().terminate(reason)
        try:
            self.app_launcher.terminate()
        except:
            pass

    def run(self) -> bool:
        """运行串流自动化流程"""
        try:
            logger.info("=" * 50)
            logger.info("开始串流自动化")
            logger.info("=" * 50)

            if self._failed:
                logger.error("串流已终止")
                return False

            if not self._wait_for_home():
                return False

            if not self._select_console():
                return False

            if not self._start_stream():
                return False

            if not self._wait_for_stream():
                return False

            logger.info("=" * 50)
            logger.info("串流自动化完成")
            logger.info("=" * 50)
            return True

        except Exception as e:
            logger.error(f"串流流程异常: {e}")
            self.terminate(str(e))
            return False

    def _wait_for_home(self) -> bool:
        """等待主页加载"""
        logger.info("[waiting_for_home] 等待主页加载...")

        if self._wait_for_template("home_indicator", timeout=self.timeout.get('page_load', 30)):
            logger.info("主页指示器已出现")
            return True

        if self._wait_for_template("xbox_home_page", timeout=10, fail_on_timeout=False):
            logger.info("Xbox主页已加载")
            return True

        logger.error("主页加载失败")
        self.terminate("主页加载失败")
        return False

    def _select_console(self) -> bool:
        """选择控制台"""
        logger.info("[selecting_console] 选择 Xbox 控制台...")

        if not self._wait_for_template("console_card", timeout=30):
            return False

        if not self._click_template("console_card"):
            return False

        time.sleep(1)
        return True

    def _start_stream(self) -> bool:
        """开始串流"""
        logger.info("[starting_stream] 开始串流...")

        if not self._wait_for_template("stream_button", timeout=30):
            return False

        if not self._click_template("stream_button"):
            return False

        time.sleep(2)
        return True

    def _wait_for_stream(self) -> bool:
        """等待串流成功"""
        logger.info("[waiting_for_stream] 等待串流连接...")

        timeout = self.timeout.get('stream', 180)
        start_time = time.time()
        check_interval = 5

        while time.time() - start_time < timeout:
            if self._failed:
                return False

            elapsed = int(time.time() - start_time)
            logger.info(f"等待串流中... ({elapsed}s)")

            if self._wait_for_template("stream_connection_successfully", timeout=2, fail_on_timeout=False):
                logger.info("串流已成功连接！")
                logger.info("[stream_connected] 串流连接成功")
                return True

            if self._wait_for_template("configuration_successfully", timeout=1, fail_on_timeout=False):
                logger.info("检测到配置成功状态，串流成功！")
                logger.info("[stream_connected] 串流连接成功")
                return True

            if self._wait_for_template("stream_connecting", timeout=1, fail_on_timeout=False):
                logger.info("检测到串流连接中...")
            elif self._wait_for_template("loading_game", timeout=1, fail_on_timeout=False):
                logger.info("检测到游戏加载中...")
            elif self._wait_for_template("ready_send_to_ICE", timeout=1, fail_on_timeout=False):
                logger.info("检测到ICE就绪状态...")

            time.sleep(check_interval)

        logger.error("串流等待超时")
        self.terminate("串流等待超时")
        return False