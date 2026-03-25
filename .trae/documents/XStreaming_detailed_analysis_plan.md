# XStreaming 代码详解计划

## 任务 1: 项目概述与框架解读

### [ ] 1.1 项目技术栈深入分析
- Electron 主进程架构
- Next.js 渲染进程架构
- TypeScript 类型系统应用
- Nextron 构建工具原理

### [ ] 1.2 目录结构与模块划分
- main/ 目录结构详解
- renderer/ 目录结构详解
- 模块间依赖关系

### [ ] 1.3 双进程通信机制
- IPC 通道注册与路由
- preload.js 桥梁作用
- contextBridge API 暴露

## 任务 2: 核心流程代码解读

### [ ] 2.1 启动流程代码解读
- [ ] 2.1.1 Application 构造函数详解
  - GPU 配置逻辑 (use_vulkan 判断)
  - electron-store 初始化
  - startupFlags 解析 (--fullscreen, --auto-connect)
- [ ] 2.1.2 窗口创建流程
  - createWindow helper 函数
  - 窗口选项配置
  - 快捷键注册 (F11 全屏)
- [ ] 2.1.3 路由加载逻辑
  - 生产环境 vs 开发环境 URL
  - locale 多语言路由

### [ ] 2.2 认证流程代码解读
- [ ] 2.2.1 XAL 认证流程
  - checkAuthentication() 令牌检查逻辑
  - startSilentFlow() 静默刷新
  - _xal.refreshTokens() 令牌刷新机制
  - getStreamingToken() 获取串流令牌
- [ ] 2.2.2 MSAL 认证流程
  - MsalAuthentication.ts 实现差异
  - deviceCode 登录流程
- [ ] 2.2.3 令牌存储机制
  - AuthTokenStore 结构
  - StreamingToken 类设计
  - 令牌有效期管理 (getSecondsValid)

### [ ] 2.3 控制台发现流程代码解读
- [ ] 2.3.1 getConsoles API 调用
  - HTTP 请求构造
  - X-MS-Device-Info 头信息
  - 错误处理与降级
- [ ] 2.3.2 控制台列表 IPC 通信
  - consoles channel 注册
  - 前端 Ipc.send() 调用链
- [ ] 2.3.3 控制台状态轮询
  - powerState 状态类型
  - ConnectedStandby 唤醒逻辑

### [ ] 2.4 串流连接流程代码解读
- [ ] 2.4.1 startStream 会话创建
  - POST /v5/sessions/{type}/play
  - deviceInfo 构造逻辑
  - sessionPath 解析
- [ ] 2.4.2 会话状态监控
  - monitorSession 轮询机制
  - 状态机: Provisioning → ReadyToConnect → Provisioned
  - MSAL Auth 发送时机
- [ ] 2.4.3 WebRTC SDP 交换
  - createOffer 生成逻辑
  - sendSdp API 调用
  - setRemoteOffer 设置远端Answer
- [ ] 2.4.4 ICE Candidate 交换
  - checkIce 递归获取
  - Teredo 地址解析 (IPv6)
  - candidate 优先级排序
- [ ] 2.4.5 keepalive 保活机制
  - 30秒定时发送
  - 会话超时处理

### [ ] 2.5 串流控制流程代码解读
- [ ] 2.5.1 xStreamingPlayer 初始化
  - 输入配置 (touch/mouse/keyboard)
  - 编解码器设置
- [ ] 2.5.2 游戏手柄输入处理
  - setGamepadIndex
  - setVibration 振动反馈
  - setGamepadDeadZone 死区设置
- [ ] 2.5.3 键盘映射
  - input_mousekeyboard_maping 配置
  - setKeyboardInput 控制
- [ ] 2.5.4 音频控制
  - setAudioVolumeDirect
  - 麦克风开关

## 任务 3: 核心模块代码详解

### [ ] 3.1 Application 主类详解
- [ ] 3.1.1 类属性与成员变量
- [ ] 3.1.2 构造函数初始化顺序
- [ ] 3.1.3 认证完成回调 (authenticationCompleted)
- [ ] 3.1.4 窗口生命周期管理

### [ ] 3.2 IPC 通信机制详解
- [ ] 3.2.1 Ipc 类的角色
- [ ] 3.2.2 Channel 模块注册
- [ ] 3.2.3 onEvent 事件分发
- [ ] 3.2.4 前端 Ipc.send 封装

### [ ] 3.3 StreamManager 详解
- [ ] 3.3.1 会话存储结构 (_sessions)
- [ ] 3.3.2 getApi 多态实现
- [ ] 3.3.3 startStream/stopStream 对称设计
- [ ] 3.3.4 sendSdp/sendIce 方法分层

### [ ] 3.4 xCloudApi 详解
- [ ] 3.4.1 HTTP 请求封装 (get/post)
- [ ] 3.4.2 认证头构造
- [ ] 3.4.3 startStream 参数构建
- [ ] 3.4.4 SDP/ICE 交换实现

### [ ] 3.5 Authentication 模块详解
- [ ] 3.5.1 XAL 与 MSAL 双轨设计
- [ ] 3.5.2 TokenStore 抽象
- [ ] 3.5.3 WebView Hook 机制

## 任务 4: 前端渲染层代码详解

### [ ] 4.1 Next.js 页面结构
- [ ] 4.1.1 getStaticPaths/getStaticProps
- [ ] 4.1.2 locale 路由处理
- [ ] 4.1.3 _app.tsx 全局布局

### [ ] 4.2 Home 页面代码详解
- [ ] 4.2.1 控制台列表获取
- [ ] 4.2.2 游戏手柄导航
- [ ] 4.2.3 登录状态检查
- [ ] 4.2.4 autoConnect 自动连接

### [ ] 4.3 Stream 页面代码详解
- [ ] 4.3.1 xStreamingPlayer 初始化
- [ ] 4.3.2 WebRTC 事件监听
- [ ] 4.3.3 连接状态管理
- [ ] 4.3.4 资源清理 (useEffect return)

### [ ] 4.4 组件化架构
- [ ] 4.4.1 ActionBar 操作栏
- [ ] 4.4.2 Loading 加载组件
- [ ] 4.4.3 Modal 对话框
- [ ] 4.4.4 Context 状态管理

## 任务 5: 输出完整代码解读文档
