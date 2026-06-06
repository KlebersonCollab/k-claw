# yt-dlp Guide for YouTube Transcript Extraction

## What is yt-dlp?

yt-dlp is a youtube-dl fork with additional features and fixes. It's a powerful command-line tool for downloading videos and extracting metadata from YouTube and other video platforms.

## Installation

```bash
# Using pip
pip install yt-dlp

# Using uv
uv add yt-dlp

# Using homebrew (macOS)
brew install yt-dlp
```

## Basic Usage

### Download Video
```bash
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Audio Only
```bash
yt-dlp -x --audio-format mp3 "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Subtitles
```bash
# Download manual subtitles
yt-dlp --write-sub --sub-lang en "https://www.youtube.com/watch?v=VIDEO_ID"

# Download automatic subtitles
yt-dlp --write-auto-sub --sub-lang en "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Transcript Extraction

### Get Available Subtitles
```bash
yt-dlp --list-subs "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Specific Subtitle Language
```bash
yt-dlp --write-sub --sub-lang en --sub-format vtt "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download All Available Subtitles
```bash
yt-dlp --write-all-subs "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Advanced Options

### Get Video Metadata
```bash
yt-dlp --get-title --get-description --get-duration "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Best Quality
```bash
yt-dlp -f "bestvideo+bestaudio" "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download with Custom Filename
```bash
yt-dlp -o "%(title)s.%(ext)s" "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Download Playlist
```bash
yt-dlp "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

## Subtitle Formats

### VTT (WebVTT)
```bash
yt-dlp --write-sub --sub-format vtt "https://www.youtube.com/watch?v=VIDEO_ID"
```

### SRT (SubRip)
```bash
yt-dlp --write-sub --sub-format srt "https://www.youtube.com/watch?v=VIDEO_ID"
```

### ASS (Advanced SubStation Alpha)
```bash
yt-dlp --write-sub --sub-format ass "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Python Integration

### Basic Usage
```python
import yt_dlp

def get_video_info(url):
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'title': info['title'],
            'description': info['description'],
            'duration': info['duration'],
            'subtitles': info.get('subtitles', {}),
            'automatic_captions': info.get('automatic_captions', {}),
        }
```

### Download Subtitles
```python
import yt_dlp

def download_subtitles(url, lang='en'):
    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': [lang],
        'subtitlesformat': 'vtt',
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
```

### Get Subtitle Content
```python
import yt_dlp

def get_subtitle_content(url, lang='en'):
    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': [lang],
        'skip_download': True,
        'quiet': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if 'subtitles' in info and lang in info['subtitles']:
            subtitle_url = info['subtitles'][lang][0]['url']
            import requests
            response = requests.get(subtitle_url)
            return response.text
    return None
```

## Error Handling

### Common Errors

#### Video Not Available
```python
try:
    info = ydl.extract_info(url, download=False)
except yt_dlp.utils.DownloadError as e:
    print(f"Error: {e}")
```

#### No Subtitles Available
```python
info = ydl.extract_info(url, download=False)
if not info.get('subtitles') and not info.get('automatic_captions'):
    print("No subtitles available")
```

#### Rate Limiting
```bash
# Add delay between requests
yt-dlp --sleep-interval 5 "https://www.youtube.com/watch?v=VIDEO_ID"
```

## Best Practices

1. **Check for Manual Subtitles First** - Manual subtitles are more accurate than automatic ones
2. **Use Appropriate Language Codes** - Use ISO 639-1 language codes (en, es, fr, etc.)
3. **Handle Errors Gracefully** - Always wrap yt-dlp calls in try-except blocks
4. **Respect Rate Limits** - Add delays between multiple requests
5. **Clean Up Temporary Files** - Remove downloaded subtitle files after processing

## Resources

- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [YouTube Video ID Format](https://en.wikipedia.org/wiki/YouTube#Video_format)
- [Subtitle Formats](https://en.wikipedia.org/wiki/Subtitle_(captioning)#Formats)
---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "YT-TRANSCRIPT-ALIGNMENT"
phase: "VERIFY"
status: "COMPLETED"
last_update: "2026-05-06T10:48:00Z"
evidence_checksum: "8e52f6a"
```
