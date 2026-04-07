"""
UI 检测模块 - 使用 OpenCV 图像识别检测 UI 元素
"""
import cv2
import numpy as np
import os
import time
import logging
from pathlib import Path
from typing import Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class DetectionStatus(Enum):
    FOUND = "found"
    NOT_FOUND = "not_found"
    TIMEOUT = "timeout"


@dataclass
class DetectionResult:
    status: DetectionStatus
    position: Optional[Tuple[int, int]] = None
    confidence: float = 0.0
    message: str = ""


class UIDetector:
    """UI 元素检测器"""

    def __init__(self, template_dir: str, screenshot_dir: str = "./screenshots", template_mapping: dict = None):
        self.template_dir = Path(template_dir)
        self.screenshot_dir = Path(screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)

        self.confidence_threshold = 0.35
        self._template_cache = {}
        self._template_mapping = template_mapping or {}

    def _load_template(self, template_name: str) -> Optional[np.ndarray]:
        """加载模板图片"""
        if template_name in self._template_cache:
            return self._template_cache[template_name]

        actual_filename = self._template_mapping.get(template_name, template_name)
        if Path(actual_filename).is_absolute():
            template_path = Path(actual_filename)
        else:
            template_path = self.template_dir / actual_filename
        if not template_path.exists():
            logger.warning(f"模板不存在: {template_path}")
            return None

        template = cv2.imread(str(template_path))
        if template is None:
            logger.error(f"无法读取模板: {template_path}")
            return None

        self._template_cache[template_name] = template
        logger.debug(f"模板已加载: {template_path}")
        return template

    def _capture_screen(self) -> Optional[np.ndarray]:
        """捕获屏幕截图"""
        try:
            import pyautogui
            screenshot = pyautogui.screenshot()
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            return screen
        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return None

    def _save_debug_screenshot(self, name: str, screen: np.ndarray):
        """保存调试截图"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"{self.screenshot_dir}/{name}_{timestamp}.png"
        cv2.imwrite(filename, screen)
        logger.debug(f"调试截图已保存: {filename}")

    def find_element(
        self,
        template_name: str,
        confidence: float = 0.35,
        timeout: int = 10,
        interval: float = 0.5
    ) -> DetectionResult:
        """
        在屏幕上查找 UI 元素

        Args:
            template_name: 模板图片文件名
            confidence: 匹配置信度 (0-1)
            timeout: 超时时间（秒）
            interval: 检测间隔（秒）

        Returns:
            DetectionResult: 检测结果
        """
        template = self._load_template(template_name)
        if template is None:
            return DetectionResult(
                status=DetectionStatus.NOT_FOUND,
                message=f"模板加载失败: {template_name}"
            )

        start_time = time.time()

        while time.time() - start_time < timeout:
            screen = self._capture_screen()
            if screen is None:
                time.sleep(interval)
                continue

            result = self._match_template(screen, template, confidence)
            if result is not None:
                logger.info(f"找到元素 {template_name}: {result}")
                return DetectionResult(
                    status=DetectionStatus.FOUND,
                    position=result,
                    message=f"找到元素: {template_name}"
                )

            time.sleep(interval)

        self._save_debug_screenshot(f"not_found_{template_name}", screen)
        return DetectionResult(
            status=DetectionStatus.TIMEOUT,
            message=f"查找元素超时: {template_name}"
        )

    def _match_template(
        self,
        screen: np.ndarray,
        template: np.ndarray,
        confidence: float
    ) -> Optional[Tuple[int, int]]:
        """
        执行模板匹配

        Returns:
            匹配中心坐标 (x, y) 或 None
        """
        try:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= confidence:
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2
                logger.debug(f"模板匹配成功: 置信度={max_val:.3f}, 位置=({center_x}, {center_y})")
                return (center_x, center_y)

            logger.debug(f"模板匹配失败: 最高置信度={max_val:.3f}, 要求={confidence}")
            return None
        except Exception as e:
            logger.error(f"模板匹配失败: {e}")
            return None

    def wait_for_element(
        self,
        template_name: str,
        timeout: int = 30,
        interval: float = 0.5
    ) -> DetectionResult:
        """
        等待 UI 元素出现

        Returns:
            DetectionResult: 检测结果
        """
        return self.find_element(template_name, timeout=timeout, interval=interval)

    def wait_for_element_disappear(
        self,
        template_name: str,
        timeout: int = 30,
        interval: float = 0.5
    ) -> DetectionResult:
        """
        等待 UI 元素消失

        Returns:
            DetectionResult: 检测结果
        """
        template = self._load_template(template_name)
        if template is None:
            return DetectionResult(
                status=DetectionStatus.NOT_FOUND,
                message=f"模板加载失败: {template_name}"
            )

        start_time = time.time()

        while time.time() - start_time < timeout:
            screen = self._capture_screen()
            if screen is None:
                time.sleep(interval)
                continue

            result = self._match_template(screen, template, self.confidence_threshold)
            if result is None:
                logger.info(f"元素已消失: {template_name}")
                return DetectionResult(
                    status=DetectionStatus.FOUND,
                    message=f"元素已消失: {template_name}"
                )

            time.sleep(interval)

        return DetectionResult(
            status=DetectionStatus.TIMEOUT,
            message=f"等待元素消失超时: {template_name}"
        )

    def click_element(
        self,
        template_name: str,
        confidence: float = 0.35,
        timeout: int = 10,
        button: str = "left"
    ) -> bool:
        """
        点击 UI 元素

        Returns:
            是否成功点击
        """
        result = self.find_element(template_name, confidence=confidence, timeout=timeout)
        if result.status == DetectionStatus.FOUND and result.position:
            x, y = result.position
            import pyautogui
            pyautogui.click(x, y, button=button)
            logger.info(f"点击坐标: ({x}, {y})")
            return True

        logger.warning(f"无法点击元素: {template_name}")
        return False


def create_detector(config: dict, config_path: str = None) -> UIDetector:
    """根据配置创建检测器"""
    template_dir = config.get("ui_templates", {}).get("template_dir", "./templates")
    screenshot_dir = config.get("automation", {}).get("screenshot_dir", "./screenshots")

    if config_path:
        base_dir = Path(config_path).parent
    else:
        base_dir = Path.cwd()

    template_dir = str((base_dir / template_dir).resolve())
    screenshot_dir = str((base_dir / screenshot_dir).resolve())

    template_mapping = {k: v for k, v in config.get("ui_templates", {}).items() if k != "template_dir"}
    return UIDetector(template_dir, screenshot_dir, template_mapping)