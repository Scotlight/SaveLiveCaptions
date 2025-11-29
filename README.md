# Save Live Captions - Enhanced Version

**Tired of losing live captions on Windows?** This is an enhanced tool to save and manage live captions with improved functionality! The application is in the `dist` folder and you can also download from release.

---

**🌐 Language / 语言:**
📖 [English](README.md) | [中文](README_zh.md)

---

## 🙏 Acknowledgments

This is a fork of the original [SaveLiveCaptions](https://github.com/M-T-Arden/SaveLiveCaptions) project by [M-T-Arden](https://github.com/M-T-Arden). Thank you for creating this amazing tool!

## ✨ Enhanced Features

This version includes significant improvements over the original:

### 🎯 Core Features
- **Live Caption Capture**: Automatically captures Windows live captions
- **Draggable Interface**: Minimal floating dashboard that can be moved anywhere
- **Customizable Save Location**: Choose where to save your caption files

### 🚀 New Enhancements
- **Segmented Recording**: Pause and resume recording without restarting the application
- **Smart Sentence Extraction**: Improved text processing for better sentence boundaries
- **Duplicate Prevention**: Intelligent deduplication to avoid repeated content
- **File Preview**: Open saved captions directly from the interface during pauses
- **Status Indicators**: Clear visual feedback for current recording state
- **5-Button Layout**: Enhanced interface with intuitive controls

## 📖 User Guide

### 1. Getting Started
1. Make sure Windows Live Captions is **enabled** before launching
2. Double click `SaveLiveCaptions.exe`
3. A floating dashboard appears in the top-left corner of your screen
4. Drag the background to move the window anywhere

### 2. Interface Controls

![Enhanced Dashboard](./assets/2025-11-29_19-32-52.png)

The enhanced interface features 5 buttons with clear functions:

- **🔴 Start** (Red Circle): Begin a new recording session with a fresh file
- **⏸ Pause** (Orange Pause): Pause current recording and enable file preview
- **▶ Resume** (Green Triangle): Continue recording in the same file
- **📂 Open** (Folder): Open the saved captions file with your default text editor (only available when paused)
- **⬛ Exit** (Black Square): Stop recording and close the application

### 3. Recording Workflow

**Single Session Recording:**
1. Click **🔴 Start** to begin recording
2. Choose your save location when prompted
3. Click **⬛ Exit** when finished

**Segmented Recording (New Feature):**
1. Click **🔴 Start** to begin recording
2. Click **⏸ Pause** whenever you need a break
3. Click **📂 Open** to review what you've captured so far
4. Click **▶ Resume** to continue recording in the same file
5. Repeat steps 2-4 as needed
6. Click **⬛ Exit** when completely finished

### 4. File Management

Your captions are saved as `YYYY-MM-DD_HH-MM-SS_captions.txt` with enhanced formatting:

```
[19:00:44] I bought all the food you like, dear.
[19:00:45] ===== Recording Paused =====
[19:01:15] ===== Recording Resumed =====
[19:01:16] Thank you so much for this.
```

**Enhanced Features:**
- ✅ Precise timestamps for every segment
- ✅ Clear pause/resume markers for easy navigation
- ✅ Improved sentence segmentation
- ✅ Smart text processing that reduces fragments
- ✅ Automatic duplicate prevention

### 5. Status Indicators

The dashboard shows current recording state:
- **🔴 Recording**: Actively capturing captions
- **🟠 Paused**: Recording paused, file preview available
- **⚪ Stopped**: Not recording, ready to start

![Captions File Example](./assets/captionsFile.png)

## 🔧 Technical Improvements

- **Enhanced Text Processing**: Better sentence boundary detection and cleanup
- **Smart Buffer Management**: Prevents duplicate and fragmented content
- **Async Architecture**: Smooth performance without UI freezing
- **Improved Error Handling**: Better reliability and graceful degradation

## 📋 Comparison

| Feature | Original | Enhanced |
|----------|-----------|----------|
| Recording | Single session only | ✅ Segmented recording |
| Interface | 2 basic buttons | ✅ 5 enhanced buttons |
| File Access | Manual | ✅ In-app preview |
| Text Quality | Basic capture | ✅ Smart processing |
| Status Feedback | Limited | ✅ Clear indicators |

## 🚀 Installation & Usage

1. Download the latest release from the [releases page](https://github.com/Scotlight/SaveLiveCaptions/releases)
2. Extract and run `SaveLiveCaptions.exe`
3. No installation required - just make sure Windows Live Captions is enabled

## 🤝 Contributing

This enhanced version maintains the simplicity of the original while adding powerful new features. Feel free to submit issues or pull requests!

## 📄 License

This project is licensed under the MIT License - same as the original.

---

**Special thanks to [M-T-Arden](https://github.com/M-T-Arden) for creating the original SaveLiveCaptions tool that made this enhanced version possible!**