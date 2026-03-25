<p align="center">
  <a href="https://github.com/Geocld/XStreaming">
    <img src="https://raw.githubusercontent.com/Geocld/XStreaming/main/images/logo.png" width="546">
  </a>
</p>

<p align="center">
  开源 Xbox/云游戏串流应用.
</p>

## 简介

XStreaming 是一款开源的 Xbox/云游戏串流移动端客户端，借鉴了 [Greenlight](https://github.com/unknownskl/greenlight) 提供的 API 接口和相关实现。

> 声明：XStreaming 与 Microsoft、Xbox 没有关联。所有权和商标属于其各自所有者。

## Android

在 Android 平台你可以使用 [XStreaming](https://github.com/Geocld/XStreaming)。

## 功能

- 跨平台，支持 Windows、macOS、Linux
- 串流 Xbox One、Xbox Series X|S 的音视频
- 支持 1080P 分辨率
- 支持外接、蓝牙手柄，支持手柄振动
- 支持手柄按键映射
- 免代理云游戏
- IPv6 优先连接支持
- 扳机振动

## 应用程序流程

### 1. 启动流程
1. **应用程序初始化**
   - 加载应用设置和配置
   - 使用GPU加速设置初始化Electron应用
   - 设置IPC通信通道
   - 初始化认证模块（XAL和MSAL）
   
   **代码入口：**
   - `main/application.ts:45-83` - 应用程序构造函数
   - `main/application.ts:74-78` - IPC和认证初始化
   - `onenote:游戏自动化->xbox串流开源代码分析->main/application.ts代码分析` - 应用程序构造函数代码分析文档
   
2. **主窗口创建**
   - 创建并配置主应用窗口
   - 加载Web界面
   - 设置全屏控制的键盘快捷键
   
   **代码入口：**
   - `main/application.ts:163-172` - Electron就绪事件处理
   - `main/application.ts:289-373` - openMainWindow方法
   - `main/helpers/create-window.ts` - 窗口创建辅助函数

### 2. 认证流程
1. **登录流程**
   - 用户点击"登录"按钮
   - 打开Microsoft账户登录窗口
   - 用户输入Microsoft账户凭据
   - Microsoft认证服务器返回令牌
   
   **代码入口：**
   - `main/authentication.ts` - 认证类
   - `main/MsalAuthentication.ts` - MSAL认证实现

2. **令牌管理**
   - 使用electron-store安全存储认证令牌
   - 在需要时刷新令牌
   - 检索用户个人资料信息（玩家标签、玩家头像、游戏分数）
   
   **代码入口：**
   - `main/helpers/tokenstore.ts` - AuthTokenStore实现
   - `main/helpers/streamTokenStore.ts` - 串流令牌存储
   - `main/helpers/webTokenStore.ts` - Web令牌存储
   - `main/application.ts:213-287` - authenticationCompleted方法

3. **认证验证**
   - 在启动时检查令牌是否有效
   - 如果令牌过期，尝试静默刷新令牌
   - 如果刷新失败，回退到完整登录流程
   
   **代码入口：**
   - `main/authentication.ts:41-75` - checkAuthentication方法
   - `main/authentication.ts:77-284` - startSilentFlow方法

### 3. 控制台发现流程
1. **Xbox控制台检测**
   - 使用Xbox Web API发现可用的Xbox控制台
   - 获取控制台信息，包括名称、IP地址和状态
   - 在"控制台"选项卡中显示控制台
   
   **代码入口：**
   - `main/helpers/streammanager.ts:280-288` - getConsoles方法
   - `main/helpers/xcloudapi.ts` - Xbox API实现

2. **控制台状态监控**
   - 检查控制台是否在线且可用于串流
   - 显示每个控制台的实时状态
   
   **代码入口：**
   - `renderer/pages/[locale]/home.tsx` - 控制台列表组件
   - `main/ipc/consoles.ts` - 控制台IPC处理程序

### 4. 串流连接流程
1. **串流启动**
   - 用户从列表中选择一个控制台
   - 应用程序从Xbox API请求串流令牌
   - 与选定的控制台创建串流会话
   
   **代码入口：**
   - `main/helpers/streammanager.ts:53-76` - startStream方法
   - `main/helpers/xcloudapi.ts` - startStream API调用

2. **会话设置**
   - 监控会话状态直到准备就绪
   - 处理会话的MSAL认证
   - 设置WebRTC连接用于视频/音频串流
   
   **代码入口：**
   - `main/helpers/streammanager.ts:165-254` - monitorSession方法
   - `main/ipc/streaming.ts` - 串流IPC处理程序

3. **连接建立**
   - 交换SDP（会话描述协议）信息
   - 处理ICE（交互式连接建立）候选
   - 建立点对点连接
   
   **代码入口：**
   - `main/helpers/streammanager.ts:98-146` - sendSdp和sendIce方法
   - `renderer/pages/[locale]/stream.tsx` - WebRTC连接设置

### 5. 串流控制流程
1. **视频/音频串流**
   - 接收来自Xbox控制台的视频流
   - 接收来自Xbox控制台的音频流
   - 实时显示视频并播放音频
   
   **代码入口：**
   - `renderer/pages/[locale]/stream.tsx` - 视频/音频渲染
   - `main/helpers/xboxWorker.ts` - 串流处理

2. **输入处理**
   - 捕获游戏手柄输入
   - 捕获键盘/鼠标输入
   - 向Xbox控制台发送输入命令
   - 支持游戏手柄振动/rumble
   
   **代码入口：**
   - `main/ipc/streaming.ts` - 输入处理
   - `renderer/components/KeyboardMap.tsx` - 键盘映射
   - `renderer/components/GamepadMapModal.tsx` - 游戏手柄映射

3. **串流设置**
   - 调整分辨率和比特率
   - 配置音频设置
   - 启用/禁用HDR等功能
   
   **代码入口：**
   - `renderer/pages/[locale]/settings.tsx` - 串流设置
   - `main/ipc/settings.ts` - 设置IPC处理程序

### 6. 串流终止流程
1. **用户主动停止**
   - 用户点击"停止串流"按钮
   - 应用程序向Xbox API发送停止串流请求
   - 清理串流会话
   
   **代码入口：**
   - `main/helpers/streammanager.ts:78-96` - stopStream方法
   - `renderer/pages/[locale]/stream.tsx` - 停止串流按钮处理

2. **自动终止**
   - 处理网络断开连接
   - 处理控制台关闭
   - 当串流结束时清理资源
   
   **代码入口：**
   - `main/helpers/streammanager.ts:165-254` - monitorSession方法（错误处理）
   - `renderer/pages/[locale]/stream.tsx` - 网络错误处理

3. **会话清理**
   - 从活动会话列表中移除会话
   - 释放分配的资源
   - 返回控制台选择屏幕
   
   **代码入口：**
   - `main/helpers/streammanager.ts:86-89` - stopStream中的会话清理
   - `renderer/pages/[locale]/stream.tsx` - 串流结束清理

<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/console.jpg" /> 
<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/xcloud.jpg" />
<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/xcloud2.jpg" />
<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/settings.jpg" />

## Steam Deck

### 从Flathub安装
`XStreaming`已经上架Flathub，你可以直接在SteamDeck的桌面模式，使用应用商店（Discover）直接搜索XStreaming即可下载安装和后续的更新。

[![Build/release](https://flathub.org/assets/badges/flathub-badge-en.svg)](https://flathub.org/apps/io.github.Geocld.XStreamingDesktop)


### 手动安装
手动安装请参阅 [XStreaming Steam Deck 指南](./wiki/steam-deck/README.zh_CN.md)

## 本地开发

### 环境要求
- [NodeJs](https://nodejs.org/) >= 18
- [Yarn](https://yarnpkg.com/) >= 1.22

### 共建计划

欢迎加入[共建计划](https://github.com/Geocld/XStreaming/issues/45)

### 运行项目

克隆本项目到本地:

```
git clone https://github.com/Geocld/XStreaming-desktop
cd XStreaming-desktop
```
安装依赖:

```
yarn
```

启动开发模式:

```
npm run dev
```

## 开发者

XStreaming 的发展离不开这些 Hacker 们，他们贡献了大量能力，也欢迎关注他们 ❤️

<!-- readme: contributors -start -->
<table>
<tr>
    <td align="center">
        <a href="https://github.com/Geocld">
            <img src="https://avatars.githubusercontent.com/u/13679095?v=4" width="90;" alt="Geocld"/>
            <br />
            <sub><b>Geocld</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/TigerBeanst">
            <img src="https://avatars.githubusercontent.com/u/3889846?v=4" width="90;" alt="TigerBeanst"/>
            <br />
            <sub><b>TigerBeanst</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/Sirherobrine23">
            <img src="https://avatars.githubusercontent.com/u/50121801?v=4" width="90;" alt="Sirherobrine23"/>
            <br />
            <sub><b>Sirherobrine23</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/liamharper2453">
            <img src="https://avatars.githubusercontent.com/u/25060863?v=4" width="90;" alt="liamharper2453"/>
            <br />
            <sub><b>liamharper2453</b></sub>
        </a>
    </td>
    <td align="center">
        <a href="https://github.com/xAbdoAT">
            <img src="https://avatars.githubusercontent.com/u/160148781?v=4" width="90;" alt="xAbdoAT"/>
            <br />
            <sub><b>xAbdoAT</b></sub>
        </a>
    </td>
  </tr>
</table>
<!-- readme: contributors -end -->

### 开源协议

XStreaming 遵循 [MIT 协议](./LICENSE).
