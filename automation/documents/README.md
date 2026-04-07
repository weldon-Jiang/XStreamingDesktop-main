# XStreaming 自动化程序说明文档

## 目录结构

```
automation/
├── core/                          # 核心公共模块
│   ├── __init__.py               # core 包导出
│   ├── base_automation.py         # 自动化基类（公共方法）
│   ├── ui_detector.py             # UI 元素检测器（模板匹配）
│   ├── window_controller.py        # 窗口控制器
│   └── config.json                # 配置文件
├── login/                         # 登录自动化模块
│   ├── __init__.py               # login 包导出
│   └── login_automation.py       # 登录流程实现
├── stream/                        # 串流自动化模块
│   ├── __init__.py               # stream 包导出
│   └── stream_automation.py       # 串流流程实现
├── game/                          # 游戏自动化模块
│   ├── __init__.py               # game 包导出
│   └── game_automation.py        # 游戏流程实现
├── templates/                      # 模板图片目录
│   ├── login/                    # 登录相关模板
│   ├── stream/                   # 串流相关模板
│   └── game/                    # 游戏相关模板
├── documents/                     # 文档目录
├── screenshots/                   # 调试截图目录
├── main.py                        # 程序入口
└── requirements.txt               # Python 依赖
```

## 模块说明

### 1. core（核心模块）
公共基础功能，被所有自动化模块共享使用。

| 文件 | 类/函数 | 说明 |
|------|---------|------|
| `base_automation.py` | `BaseAutomation` | 自动化基类，提供模板等待、点击等公共方法 |
| `ui_detector.py` | `UIDetector` | UI 元素检测，使用 OpenCV 模板匹配 |
| `ui_detector.py` | `DetectionStatus` | 检测状态枚举 |
| `ui_detector.py` | `create_detector()` | 创建检测器工厂函数 |
| `window_controller.py` | `WindowController` | 窗口控制（查找、置前、最大化等） |
| `window_controller.py` | `AppLauncher` | 应用启动器 |

### 2. login（登录模块）
处理 Microsoft 账户登录流程。

### 3. stream（串流模块）
处理 Xbox 串流连接流程。

### 4. game（游戏模块）
处理游戏手柄模拟（预留）。

## 工作流程

```
启动应用 (AppLauncher)
    ↓
等待窗口出现 (WindowController)
    ↓
检查登录状态 (LoginAutomation)
    ├─ 已登录 → 跳过登录
    └─ 未登录 → 自动填写账户密码登录
    ↓
等待主页加载 (StreamAutomation)
    ↓
选择控制台 (StreamAutomation)
    ↓
开始串流 (StreamAutomation)
    ↓
等待串流成功 (StreamAutomation)
    ↓
游戏自动化 (GameAutomation) [可选]
```

## 使用方法

### 1. 安装依赖

```bash
cd automation
pip install -r requirements.txt
```

### 2. 配置

编辑 `core/config.json`：

```json
{
  "xstreaming": {
    "path": "D:\\auto-xbox\\XStreamingDesktop-main",
    "dev_command": "npm run dev",
    "window_title": "XStreaming",
    "timeout": {
      "startup": 60,
      "login": 120,
      "stream": 180,
      "page_load": 30
    }
  },
  "account": {
    "email": "your_email@outlook.com",
    "password": "your_password"
  },
  "automation": {
    "enabled": true,
    "retry_count": 2,
    "screenshot_dir": "./screenshots"
  }
}
```

### 3. 运行

```bash
# 基本运行
python main.py

# 调试模式（查看详细日志）
python main.py --debug

# 跳过登录步骤
python main.py --skip-login

# 跳过游戏步骤
python main.py --skip-game

# 指定配置文件
python main.py --config /path/to/config.json
```

## 模板说明

模板图片位于 `templates/` 目录下，按功能模块分类：

### login 模板（7个）
| 模板名 | 文件 | 说明 |
|--------|------|------|
| login_button | 1_login_button.png | 登录按钮 |
| login_user_account | 2_login_user_account.png | 账户输入框 |
| login_next_button | 3_login_next_button.png | 下一步按钮 |
| login_password | 4_login_password.png | 密码输入框 |
| login_account_button | 5_login_account_button.png | 登录按钮 |
| login_loading | 6_login_loading.png | 登录加载中 |
| home_indicator | 7_home_indicator.png | 主页指示器 |

### stream 模板（7个）
| 模板名 | 文件 | 说明 |
|--------|------|------|
| console_card | 8_console_card.png | Xbox 控制台卡片 |
| stream_button | 9_stream_button.png | 开始串流按钮 |
| stream_connecting | 10_stream_connecting.png | 串流连接中 |
| configuration_successfully | 11_configuration_successfully.png | 配置成功 |
| ready_send_to_ICE | 12_ready_send_to_ICE.png | ICE 就绪 |
| stream_connection_successfully | 13_stream_connection_successfully.png | 串流成功 |
| xbox_home_page | 14_xbox_home_page.png | Xbox 主页 |

### game 模板（3个）
| 模板名 | 文件 | 说明 |
|--------|------|------|
| chose_game_FC26_button | 15_chose_game_FC26_button.png | 选择游戏按钮 |
| play_game_button | 15_play_game_button.png | 开始游戏按钮 |
| loading_game | 16_loading_game.png | 游戏加载中 |

## 模板制作

### 截图要求
- 只截取按钮/元素本身，不要包含周围背景
- 模板图片尺寸应与实际 UI 元素一致
- 建议使用 OpenCV 兼容的 PNG 格式

### 制作步骤
1. 使用 pyautogui 截图当前屏幕
2. 使用图像编辑工具裁剪出目标元素
3. 保存为 PNG 格式
4. 放置到对应的 `templates/{模块}/` 目录
5. 在 `main.py` 的 `create_ui_detector()` 中注册模板映射

## 核心类说明

### BaseAutomation
所有自动化模块的基类，提供公共方法：

```python
_wait_for_template(template_name, timeout, fail_on_timeout, retry_count, retry_interval, confidence)
# 等待模板出现，支持重试机制

_click_template(template_name, fail_on_not_found)
# 点击模板元素

_wait_for_template_disappear(template_name, timeout)
# 等待模板消失

terminate(reason)
# 终止自动化流程
```

### UIDetector
UI 元素检测器：

```python
find_element(template_name, confidence, timeout, interval)
# 查找元素，返回 DetectionResult

wait_for_element(template_name, timeout, interval)
# 等待元素出现

click_element(template_name, confidence, timeout, button)
# 点击元素

wait_for_element_disappear(template_name, timeout, interval)
# 等待元素消失
```

## 故障排除

### 1. 端口被占用
```
Error: listen EADDRINUSE: address already in use :::8888
```
程序会自动检测并终止占用端口的进程。

### 2. 模板匹配失败
- 检查模板图片是否与当前界面匹配
- 检查模板分辨率是否一致
- 可调整 `ui_detector.py` 中的 `confidence_threshold`

### 3. 窗口未找到
- 检查 `config.json` 中的 `window_title` 是否正确
- 确保窗口未被其他窗口遮挡

### 4. 截图保存
调试截图保存在 `screenshots/` 目录，文件名为 `not_found_{模板名}_{时间戳}.png`