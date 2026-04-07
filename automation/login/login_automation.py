"""
登录自动化模块
"""
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import UIDetector
from core.base_automation import BaseAutomation

logger = logging.getLogger(__name__)


class LoginState:
    IDLE = "idle"
    CHECKING = "checking"
    LOGGING_IN = "logging_in"
    COMPLETED = "completed"
    FAILED = "failed"


class LoginAutomation(BaseAutomation):
    """登录自动化控制器"""

    def __init__(self, ui_detector: UIDetector, account: dict, timeout: dict):
        super().__init__(ui_detector)
        self.account = account
        self.timeout = timeout

    def _switch_to_english_input(self):
        """切换到英文输入模式"""
        try:
            import pyautogui
            pyautogui.hotkey('ctrl', 'space')
            time.sleep(0.2)
            logger.info("已发送 Ctrl+Space 切换英文输入")
        except Exception as e:
            logger.warning(f"切换英文输入模式失败: {e}")

    def run(self) -> bool:
        """运行登录自动化流程"""
        try:
            logger.info("=" * 50)
            logger.info("开始登录自动化")
            logger.info("=" * 50)

            if self._failed:
                logger.error("登录已终止")
                return False

            if not self._check_login():
                return False

            logger.info("=" * 50)
            logger.info("登录自动化完成")
            logger.info("=" * 50)
            return True

        except Exception as e:
            logger.error(f"登录流程异常: {e}")
            self.terminate(str(e))
            return False

    def _check_login(self) -> bool:
        """检查登录状态"""
        logger.info("[checking] 检查登录状态...")

        if self._wait_for_template("home_indicator", timeout=5, fail_on_timeout=False, confidence=0.7):
            logger.info("[登录状态] 检测到主页指示器 -> 用户已登录")
            return True

        if self._wait_for_template("xbox_home_page", timeout=5, fail_on_timeout=False, confidence=0.7):
            logger.info("[登录状态] 检测到 Xbox 主页 -> 用户已登录")
            return True

        if self._wait_for_template("login_button", timeout=30, fail_on_timeout=False, confidence=0.7):
            logger.info("[登录状态] 检测到登录按钮 -> 用户未登录，开始自动登录流程")
            return self._do_login()

        if self._wait_for_template("login_user_account", timeout=30, fail_on_timeout=False, confidence=0.7):
            logger.info("[登录状态] 检测到用户账户输入框 -> 用户未登录，开始自动登录流程")
            return self._do_login()

        logger.warning("[登录状态] 未检测到明确的登录状态，尝试继续执行...")
        return True

    def _do_login(self) -> bool:
        """执行登录流程"""
        logger.info("=" * 50)
        logger.info("[登录流程] 开始自动登录")
        logger.info("=" * 50)

        if not self._click_template("login_button", fail_on_not_found=False):
            pass

        time.sleep(2)

        logger.info("等待 Microsoft 登录界面...")
        if not self._wait_for_template("login_user_account", timeout=30, fail_on_timeout=False):
            logger.warning("未找到账户输入框模板，尝试继续...")

        logger.info("点击账户输入框...")
        self._click_template("login_user_account", fail_on_not_found=False)
        time.sleep(0.5)

        self._switch_to_english_input()
        time.sleep(0.3)

        logger.info(f"输入账户: {self.account.get('email', '')}")
        import pyautogui
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.2)
        pyautogui.typewrite(self.account.get('email', ''), interval=0.05)
        time.sleep(1)

        logger.info("点击下一步...")
        if not self._click_template("login_next_button", fail_on_not_found=True):
            logger.error("点击下一步失败，输入框可能被校验卡住，终止自动化")
            return False

        time.sleep(2)

        logger.info("等待密码输入框...")
        if self._wait_for_template("login_password", timeout=30, fail_on_timeout=False):
            logger.info("点击密码输入框...")
            self._click_template("login_password", fail_on_not_found=False)
            time.sleep(0.5)

            self._switch_to_english_input()
            time.sleep(0.3)

            logger.info("输入密码...")
            import pyautogui
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.2)
            pyautogui.typewrite(self.account.get('password', ''), interval=0.05)
            time.sleep(1)

            logger.info("点击登录...")
            if not self._click_template("login_account_button", fail_on_not_found=True):
                logger.error("点击登录按钮失败，终止自动化")
                return False

            time.sleep(2)

            if self._wait_for_template("login_loading", timeout=10, fail_on_timeout=False):
                self._wait_for_template_disappear("login_loading", timeout=60)

        if self._wait_for_template("home_indicator", timeout=self.timeout.get('login', 120), confidence=0.7):
            logger.info("[登录结果] 检测到主页指示器 -> 登录成功")
            return True

        if self._wait_for_template("xbox_home_page", timeout=30, fail_on_timeout=False, confidence=0.7):
            logger.info("[登录结果] 检测到 Xbox 主页 -> 登录成功")
            return True

        logger.warning("[登录结果] 未检测到登录完成标志，继续执行...")
        return True