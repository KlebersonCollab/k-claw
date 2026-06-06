# YouTube Transcript

> Skill to automate the extraction of transcripts from YouTube videos with AI fallback (Whisper).

[![Version](https://img.shields.io/badge/Version-2.3.0-blue)](#changelog)
[![Status](https://img.shields.io/badge/Status-Stable-green)](#)

---

## 📖 Overview

The **YouTube Transcript** skill is an orchestration tool designed to obtain the textual content of YouTube videos in the most efficient way possible. It automates the decision flow between existing captions and synthetic AI transcription, always ensuring a clean output file ready for consumption.

### 🚀 Key Differentiators
- **Resource Efficiency:** Does not download the full video; only metadata, captions, or audio.
- **Intelligent Cleaning:** Python algorithm to remove HTML tags and deduplicate repeated words common in automatic captions.
- **Local Fallback:** Utilizes the local OpenAI Whisper model (via `uv`) when the video lacks original captions.

---

## ⚙️ Prerequisites

For full functionality, ensure you have the following tools installed:

1.  **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** For metadata and caption extraction.
    - Installation: `brew install yt-dlp` or `uv add yt-dlp`
2.  **[ffmpeg](https://ffmpeg.org/):** Necessary for audio manipulation and Whisper fallback.
    - Installation: `brew install ffmpeg`
3.  **[uv](https://github.com/astral-sh/uv):** Python dependency manager used to run Whisper without polluting your global environment.

---

## 🛠️ How to Use

The skill is invoked by passing the URL of the desired video.

### Automatic Flow
1.  **Mapping:** The skill checks for manual captions (e.g., EN, PT-BR).
2.  **Download:** If found, it downloads the VTT file.
3.  **Fallback:** If no captions are present, the skill will request permission to download the audio and run **Whisper (AI)**.
4.  **Cleaning:** The text passes through a sanitization script to generate the final `.txt`.

### Output Example
```text
Video Name: "How to make coffee.txt"
Content:
Hello, today we are going to learn how to make coffee in a simple and fast way...
```

---

## 🧩 Technical Details

- **Whisper Model:** By default, it uses the `base` model for a balance between speed and precision.
- **Final Format:** Always UTF-8, without timestamps.

---

## 📝 Changelog

Consult the [CHANGELOG.md](CHANGELOG.md) for the full version history.

---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "YT-TRANSCRIPT-ALIGNMENT"
phase: "IMPLEMENT"
status: "COMPLETED"
last_update: "2026-05-06T10:15:00Z"
evidence_checksum: "8e52f6a"
```
