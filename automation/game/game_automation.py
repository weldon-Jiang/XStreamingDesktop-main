"""
游戏自动化模块
"""
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import UIDetector
from core.base_automation import BaseAutomation

logger = logging.getLogger(__name__)


class GameState:
    IDLE = "idle"
    WAITING_FOR_GAMEPAD = "waiting_for_gamepad"
    PLAYING = "playing"
    COMPLETED = "completed"
    FAILED = "failed"


class GameAutomation(BaseAutomation):
    """游戏自动化控制器"""

    def __init__(self, ui_detector: UIDetector):
        """
        初始化游戏自动化

        Args:
            ui_detector: UI 检测器实例
        """
        super().__init__(ui_detector)

    def _simulate_gamepad_input(self):
        """模拟游戏手柄输入"""
        try:
            import pyautogui
            pyautogui.press('a')
            time.sleep(0.5)
        except Exception as e:
            logger.warning(f"模拟手柄输入失败: {e}")

    def run(self) -> bool:
        """运行游戏自动化流程"""
        try:
            logger.info("=" * 50)
            logger.info("开始游戏自动化")
            logger.info("=" * 50)

            if self._failed:
                logger.error("游戏自动化已终止")
                return False

            if not self._wait_for_gamepad():
                return False

            self._play_game()

            logger.info("=" * 50)
            logger.info("游戏自动化完成")
            logger.info("=" * 50)
            return True

        except Exception as e:
            logger.error(f"游戏流程异常: {e}")
            self.terminate(str(e))
            return False

    def _wait_for_gamepad(self) -> bool:
        """等待手柄连接"""
        logger.info("[waiting_for_gamepad] 等待游戏手柄连接...")

        if not self._wait_for_template("gamepad_connected", timeout=30):
            logger.error("未检测到游戏手柄连接，终止自动化")
            self.terminate("未检测到游戏手柄连接")
            return False

        logger.info("游戏手柄已连接")
        return True

    def _play_game(self):
        """循环模拟游戏手柄操作"""
        logger.info("[playing] 模拟游戏手柄操作...")

        while not self._failed:
            self._simulate_gamepad_input()
            time.sleep(1)