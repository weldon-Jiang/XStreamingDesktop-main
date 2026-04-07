"""
XStreaming 自动化主入口
"""
import json
import logging
import sys
import time
import argparse
import subprocess
from pathlib import Path
from dataclasses import dataclass

from core import UIDetector, WindowController, AppLauncher
from login import LoginAutomation
from stream import StreamAutomation
from game import GameAutomation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('automation.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


def kill_process_on_port(port: int):
    """杀死占用指定端口的进程"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True,
            capture_output=True,
            text=True
        )
        lines = result.stdout.strip().split('\n')
        for line in lines:
            if 'LISTENING' in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'LISTENING' and i > 0:
                        pid = parts[i + 1].strip()
                        logger.warning(f"发现占用端口 {port} 的进程 PID: {pid}")
                        try:
                            subprocess.run(f'taskkill /F /PID {pid}', shell=True)
                            logger.info(f"已终止进程 {pid}")
                        except Exception as e:
                            logger.error(f"终止进程失败: {e}")
                        break
    except Exception as e:
        logger.warning(f"检查端口占用失败: {e}")


@dataclass
class AutomationConfig:
    xstreaming_path: str
    dev_command: str
    window_title: str
    timeout: dict
    account: dict
    enabled: bool
    retry_count: int


def load_config(config_path: str = None) -> dict:
    """加载配置文件"""
    if config_path is None:
        config_path = Path(__file__).parent / "config.json"

    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_ui_detector(config: dict, config_path: str = None) -> UIDetector:
    """创建 UI 检测器"""
    base_dir = Path(config_path).parent if config_path else Path.cwd()

    login_templates = {
        'login_button': '1_login_button.png',
        'login_user_account': '2_login_user_account.png',
        'login_next_button': '3_login_next_button.png',
        'login_password': '4_login_password.png',
        'login_account_button': '5_login_account_button.png',
        'login_loading': '6_login_loading.png',
        'home_indicator': '7_home_indicator.png',
    }

    stream_templates = {
        'console_card': '8_console_card.png',
        'stream_button': '9_stream_button.png',
        'stream_connecting': '10_stream_connecting.png',
        'configuration_successfully': '11_configuration_successfully.png',
        'ready_send_to_ICE': '12_ready_send_to_ICE.png',
        'stream_connection_successfully': '13_stream_connection_successfully.png',
        'xbox_home_page': '14_xbox_home_page.png',
    }

    game_templates = {
        'chose_game_FC26_button': '15_chose_game_FC26_button.png',
        'play_game_button': '15_play_game_button.png',
        'loading_game': '16_loading_game.png',
    }

    login_template_dir = base_dir / "templates" / "login"
    stream_template_dir = base_dir / "templates" / "stream"
    game_template_dir = base_dir / "templates" / "game"

    all_template_mapping = {}
    for k, v in login_templates.items():
        all_template_mapping[k] = str(login_template_dir / v)
    for k, v in stream_templates.items():
        all_template_mapping[k] = str(stream_template_dir / v)
    for k, v in game_templates.items():
        all_template_mapping[k] = str(game_template_dir / v)

    return UIDetector(
        template_dir=str(base_dir / "templates"),
        screenshot_dir=str(base_dir / "screenshots"),
        template_mapping=all_template_mapping
    )


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='XStreaming 自动化')
    parser.add_argument('--config', '-c', default=None, help='配置文件路径')
    parser.add_argument('--debug', '-d', action='store_true', help='开启调试模式')
    parser.add_argument('--skip-login', action='store_true', help='跳过登录步骤')
    parser.add_argument('--skip-game', action='store_true', help='跳过游戏步骤')
    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    try:
        config_path = args.config or str(Path(__file__).parent / "config.json")
        config = load_config(config_path)

        automation_config = AutomationConfig(
            xstreaming_path=config['xstreaming']['path'],
            dev_command=config['xstreaming']['dev_command'],
            window_title=config['xstreaming']['window_title'],
            timeout=config['xstreaming']['timeout'],
            account=config['account'],
            enabled=config['automation']['enabled'],
            retry_count=config['automation']['retry_count']
        )

        if not automation_config.enabled:
            logger.warning("自动化功能已禁用")
            return

        logger.info("=" * 50)
        logger.info("开始 XStreaming 自动化")
        logger.info("=" * 50)

        app_launcher = AppLauncher(
            automation_config.xstreaming_path,
            automation_config.dev_command
        )
        window_controller = WindowController(automation_config.window_title)
        ui_detector = create_ui_detector(config, config_path)

        logger.info("检查端口 8888 是否被占用...")
        kill_process_on_port(8888)
        time.sleep(1)

        app_launcher.launch()
        logger.info("应用已启动，等待初始化...")
        time.sleep(5)

        if not window_controller.wait_for_window(timeout=automation_config.timeout.get('startup', 60)):
            logger.error("等待窗口超时")
            app_launcher.terminate()
            return

        window_controller.bring_to_front()
        logger.info("窗口已置前")

        if not args.skip_login:
            login_automation = LoginAutomation(
                ui_detector,
                automation_config.account,
                automation_config.timeout
            )
            if not login_automation.run():
                logger.error("登录流程失败")
                app_launcher.terminate()
                return
        else:
            logger.info("跳过登录步骤")

        stream_automation = StreamAutomation(
            ui_detector,
            window_controller,
            app_launcher,
            automation_config.timeout
        )
        if not stream_automation.run():
            logger.error("串流流程失败")
            app_launcher.terminate()
            return

        if not args.skip_game:
            game_automation = GameAutomation(ui_detector)
            game_automation.run()
        else:
            logger.info("跳过游戏步骤")

        logger.info("=" * 50)
        logger.info("所有自动化流程完成！")
        logger.info("=" * 50)

    except KeyboardInterrupt:
        logger.info("用户中断")
        try:
            app_launcher.terminate()
        except:
            pass
    except Exception as e:
        logger.error(f"自动化异常: {e}")
        try:
            app_launcher.terminate()
        except:
            pass


if __name__ == "__main__":
    main()
