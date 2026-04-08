"""
core 包 - 自动化核心模块

提供所有自动化模块共享的基础功能：
- UI 元素检测（模板匹配）
- 窗口控制
- 自动化基类
"""

from .ui_detector import UIDetector, DetectionStatus, create_detector
from .window_controller import WindowController, AppLauncher
from .base_automation import BaseAutomation

__all__ = ['UIDetector', 'DetectionStatus', 'create_detector', 'WindowController', 'AppLauncher', 'BaseAutomation']