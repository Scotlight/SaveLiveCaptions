# Save Live Captions

**Tired of losing live captions on Windows?**  This is a simple tool to save the content of live captions! The application is in the `dist` folder and you can also download from release.

## 🙏 Acknowledgments

This is a fork of the original [SaveLiveCaptions](https://github.com/M-T-Arden/SaveLiveCaptions) project by [M-T-Arden](https://github.com/M-T-Arden). Thank you for creating this amazing tool!

### Features in this Fork

In addition to the original features, this enhanced version includes:

- **Segmented Recording**: Pause and resume recording without restarting the application
- **File Preview**: Open saved captions with your default text editor during pauses
- **Improved Sentence Extraction**: Enhanced text processing for better sentence boundaries
- **Duplicate Prevention**: Smart deduplication to avoid repeated captions
- **Better User Interface**: Clear status indicators and improved button layout

###  Features

---

- Save live captions to a text file.
- Minimalist floating dashboard.
- Customizable save location.
- **NEW**: Pause/resume recording functionality.
- **NEW**: Open saved files directly from the interface.

### Guidelines

---

1. Before you open this application, make sure you already **open the live captions on Windows** (or it will exit automatically). Then double click the `SaveLiveCaptions.exe`. A small dashboard will appear in the top-left corner of your screen. You can drag the background to move this window.

![Dashboard Preview](./assets/dashboard.png)

2. **Enhanced Button Layout**:
   - **● Start**: Begin a new recording session (creates a new file)
   - **⏸ Pause**: Pause current recording and opens the saved file for viewing
   - **▶ Resume**: Continue recording in the same file
   - **📂 Open**: Open saved captions file with default text editor (available during pause)
   - **◼ Exit**: Stop recording and close the application

3. **Segmented Recording**: You can now pause and resume recording multiple times without closing the application. All segments will be saved to the same file with timestamps for easy tracking.

4. **Improved File Management**: Your captions file `YYYY-MM-DD_HH-MM-SS_captions.txt` will be saved in the chosen location with enhanced formatting including:
   - Accurate timestamps for each segment
   - Pause/resume markers for easy navigation
   - Improved sentence segmentation
   - Better text processing to avoid fragments

![Captions File Example](./assets/captionsFile.png)

## License

This project is licensed under the MIT License.
