"""
自动化基础模块 - 提供所有自动化类的公共功能
"""
import sys
import time
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core import UIDetector, DetectionStatus

logger = logging.getLogger(__name__)


class BaseAutomation:
    """自动化基类，提供公共方法"""

    def __init__(self, ui_detector: UIDetector):
        self.ui_detector = ui_detector
        self._failed = False

    def terminate(self, reason: str = ""):
        """终止自动化流程"""
        if self._failed:
            return
        self._failed = True
        if reason:
            logger.error(f"自动化终止: {reason}")
        logger.info(f"[failed] {reason}")

    def _wait_for_template(self, template_name: str, timeout: int = 10,
                          fail_on_timeout: bool = True,
                          retry_count: int = 2,
                          retry_interval: float = 0.5,
                          confidence: float = None) -> bool:
        """等待模板出现

        Args:
            template_name: 模板名称
            timeout: 单次检测超时时间
            fail_on_timeout: 超时是否终止自动化
            retry_count: 重试次数（默认2次）
            retry_interval: 重试间隔（秒，默认0.5秒）
            confidence: 指定置信度（默认使用ui_detector的阈值）
        """
        logger.info(f"等待模板: {template_name} (超时={timeout}秒, 重试={retry_count}次)")
        for attempt in range(retry_count):
            if confidence is not None:
                result = self.ui_detector.find_element(template_name, confidence=confidence, timeout=timeout)
            else:
                result = self.ui_detector.wait_for_element(template_name, timeout=timeout)
            if result.status == DetectionStatus.FOUND:
                if attempt > 0:
                    logger.info(f"第 {attempt + 1} 次重试成功检测到模板: {template_name}")
                else:
                    logger.info(f"检测到模板: {template_name}")
                return True

            if attempt < retry_count - 1:
                logger.warning(f"第 {attempt + 1} 次超时等待模板: {template_name}，{retry_interval}秒后重试... ({retry_count - attempt - 1} 次剩余)")
                time.sleep(retry_interval)
            else:
                if fail_on_timeout:
                    logger.error(f"等待模板超时: {template_name}")
                    self.terminate(f"等待模板超时: {template_name}")
                else:
                    logger.warning(f"等待模板超时: {template_name}")

        return False

    def _click_template(self, template_name: str, fail_on_not_found: bool = True) -> bool:
        """点击模板"""
        if self.ui_detector.click_element(template_name):
            logger.info(f"点击模板成功: {template_name}")
            return True

        if fail_on_not_found:
            logger.error(f"点击模板失败: {template_name}")
            self.terminate(f"点击模板失败: {template_name}")
        else:
            logger.warning(f"点击模板失败: {template_name}")
        return False

    def _wait_for_template_disappear(self, template_name: str, timeout: int = 30) -> bool:
        """等待模板消失"""
        result = self.ui_detector.wait_for_element_disappear(template_name, timeout=timeout)
        if result.status == DetectionStatus.FOUND:
            logger.info(f"模板已消失: {template_name}")
            return True
        logger.warning(f"等待模板消失超时: {template_name}")
        return False