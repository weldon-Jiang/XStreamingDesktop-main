<p align="center">
  <a href="https://github.com/Geocld/XStreaming">
    <img src="https://raw.githubusercontent.com/Geocld/XStreaming/main/images/logo.png" width="546">
  </a>
</p>

<p align="center">
  Open-source Xbox Remote Client.
</p>

**English** | [中文](./README.zh_CN.md)

## Intro

XStreaming is an open-source mobile client for xCloud and Xbox home streaming, great inspired by [Greenlight](https://github.com/unknownskl/greenlight).

> DISCLAIMER: XStreaming is not affiliated with Microsoft, Xbox. All rights and trademarks are property of their respective owners.

## Android

If you are looking for an Android Xbox streaming application, you can use [XStreaming](https://github.com/Geocld/XStreaming).

## Features

- Cross platform, support Windows/macOS/Linux
- Stream video and audio from Xbox One and Xbox Series X|S
- Support for 1080P resolution
- Support for OTG/bluetooth gamepad controls
- Support gamepad vibration
- Supports rumble on xCloud without any proxy in some regions.
- IPv6
- Trigger rumble

## Application Flow

### 1. Startup Process
1. **Application Initialization**
   - Load application settings and configuration
   - Initialize Electron app with GPU acceleration settings
   - Set up IPC communication channels
   - Initialize authentication modules (both XAL and MSAL)
   
   **Code Entry:**
   - `main/application.ts:45-83` - Application constructor
   - `main/application.ts:74-78` - IPC and authentication initialization

2. **Main Window Creation**
   - Create and configure the main application window
   - Load the web interface
   - Set up keyboard shortcuts for fullscreen control
   
   **Code Entry:**
   - `main/application.ts:163-172` - Electron ready event handler
   - `main/application.ts:289-373` - openMainWindow method
   - `main/helpers/create-window.ts` - Window creation helper

### 2. Authentication Process
1. **Login Flow**
   - User clicks "Sign in" button
   - Authentication window opens for Microsoft account login
   - User enters Microsoft account credentials
   - Microsoft authentication server returns tokens
   
   **Code Entry:**
   - `main/authentication.ts` - Authentication class
   - `main/MsalAuthentication.ts` - MSAL authentication implementation

2. **Token Management**
   - Store authentication tokens securely using electron-store
   - Refresh tokens when needed
   - Retrieve user profile information (gamertag, gamerpic, gamerscore)
   
   **Code Entry:**
   - `main/helpers/tokenstore.ts` - AuthTokenStore implementation
   - `main/helpers/streamTokenStore.ts` - Stream token storage
   - `main/helpers/webTokenStore.ts` - Web token storage
   - `main/application.ts:213-287` - authenticationCompleted method

3. **Authentication Verification**
   - Check if tokens are valid on startup
   - Attempt silent token refresh if tokens are expired
   - Fall back to full login flow if refresh fails
   
   **Code Entry:**
   - `main/authentication.ts:41-75` - checkAuthentication method
   - `main/authentication.ts:77-284` - startSilentFlow method

### 3. Console Discovery Process
1. **Xbox Console Detection**
   - Use Xbox Web API to discover available Xbox consoles
   - Fetch console information including name, IP address, and status
   - Display consoles in the "Consoles" tab
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:280-288` - getConsoles method
   - `main/helpers/xcloudapi.ts` - Xbox API implementation

2. **Console Status Monitoring**
   - Check if consoles are online and available for streaming
   - Display real-time status of each console
   
   **Code Entry:**
   - `renderer/pages/[locale]/home.tsx` - Console list component
   - `main/ipc/consoles.ts` - Console IPC handlers

### 4. Streaming Connection Process
1. **Stream Initiation**
   - User selects a console from the list
   - Application requests stream token from Xbox API
   - Create streaming session with the selected console
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:53-76` - startStream method
   - `main/helpers/xcloudapi.ts` - startStream API call

2. **Session Setup**
   - Monitor session state until it's ready
   - Handle MSAL authentication for the session
   - Set up WebRTC connection for video/audio streaming
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:165-254` - monitorSession method
   - `main/ipc/streaming.ts` - Streaming IPC handlers

3. **Connection Establishment**
   - Exchange SDP (Session Description Protocol) information
   - Handle ICE (Interactive Connectivity Establishment) candidates
   - Establish peer-to-peer connection
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:98-146` - sendSdp and sendIce methods
   - `renderer/pages/[locale]/stream.tsx` - WebRTC connection setup

### 5. Streaming Control Process
1. **Video/Audio Streaming**
   - Receive video stream from Xbox console
   - Receive audio stream from Xbox console
   - Display video and play audio in real-time
   
   **Code Entry:**
   - `renderer/pages/[locale]/stream.tsx` - Video/audio rendering
   - `main/helpers/xboxWorker.ts` - Stream processing

2. **Input Handling**
   - Capture gamepad input
   - Capture keyboard/mouse input
   - Send input commands to Xbox console
   - Support for gamepad vibration/rumble
   
   **Code Entry:**
   - `main/ipc/streaming.ts` - Input handling
   - `renderer/components/KeyboardMap.tsx` - Keyboard mapping
   - `renderer/components/GamepadMapModal.tsx` - Gamepad mapping

3. **Streaming Settings**
   - Adjust resolution and bitrate
   - Configure audio settings
   - Enable/disable features like HDR
   
   **Code Entry:**
   - `renderer/pages/[locale]/settings.tsx` - Streaming settings
   - `main/ipc/settings.ts` - Settings IPC handlers

### 6. Stream Termination Process
1. **User Initiated Stop**
   - User clicks "Stop Streaming" button
   - Application sends stop stream request to Xbox API
   - Clean up streaming session
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:78-96` - stopStream method
   - `renderer/pages/[locale]/stream.tsx` - Stop streaming button handler

2. **Automatic Termination**
   - Handle network disconnections
   - Handle console shutdown
   - Clean up resources when stream ends
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:165-254` - monitorSession method (error handling)
   - `renderer/pages/[locale]/stream.tsx` - Network error handling

3. **Session Cleanup**
   - Remove session from active sessions list
   - Release allocated resources
   - Return to console selection screen
   
   **Code Entry:**
   - `main/helpers/streammanager.ts:86-89` - Session cleanup in stopStream
   - `renderer/pages/[locale]/stream.tsx` - Stream end cleanup

<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/console.jpg" /> 
<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/xcloud.jpg" />
<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/xcloud2.jpg" />
<img src="https://raw.githubusercontent.com/Geocld/XStreaming-desktop/main/images/settings.jpg" />

## Steam Deck

### Installing from Flathub
`XStreaming` is now available on Flathub. You can directly search for XStreaming in the application store (Discover) in desktop mode on your Steam Deck to install and receive future updates.

[![Build/release](https://flathub.org/assets/badges/flathub-badge-en.svg)](https://flathub.org/apps/io.github.Geocld.XStreamingDesktop)

### Manual Installation
For manual installation, please refer to the [XStreaming Steam Deck Guide](./wiki/steam-deck/README.md)

## Local Development

### Requirements
- [NodeJs](https://nodejs.org/) >= 18
- [Yarn](https://yarnpkg.com/) >= 1.22

### Steps to get up and running

Clone the repository:

```
git clone https://github.com/Geocld/XStreaming-desktop
cd XStreaming-desktop
```

Install dependencies:

```
yarn
```

Run development build:

```
npm run dev
```

## Developers

XStreaming-desktop's development can not be without these Hackers. They contributed a lot of capabilities for XStreaming-desktop. Also, welcome to follow them! ❤️

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


### License

XStreaming is [MIT licensed](./LICENSE).
