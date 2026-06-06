# OpenAI Whisper Guide for Audio Transcription

## What is Whisper?

Whisper is OpenAI's automatic speech recognition (ASR) system trained on 680,000 hours of multilingual data. It provides high-quality transcription for audio and video files.

## Installation

```bash
# Using pip
pip install openai-whisper

# Using uv
uv add openai-whisper

# With ffmpeg dependency (required)
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Basic Usage

### Command Line
```bash
# Transcribe audio file
whisper audio.mp3

# Transcribe with specific model
whisper audio.mp3 --model base

# Transcribe with language specified
whisper audio.mp3 --language en

# Transcribe with timestamp output
whisper audio.mp3 --output_format srt
```

### Python API
```python
import whisper

# Load model
model = whisper.load_model("base")

# Transcribe audio
result = model.transcribe("audio.mp3")

# Get text
print(result["text"])

# Get segments with timestamps
for segment in result["segments"]:
    print(f"[{segment['start']:.2f} -> {segment['end']:.2f}] {segment['text']}")
```

## Model Sizes

| Model | Parameters | English-only | Multilingual | VRAM (GB) | Speed |
|-------|------------|--------------|-------------|-----------|-------|
| tiny | 39 M | tiny.en | tiny | ~1 | ~32x |
| base | 74 M | base.en | base | ~1 | ~16x |
| small | 244 M | small.en | small | ~2 | ~6x |
| medium | 769 M | medium.en | medium | ~5 | ~2x |
| large | 1550 M | N/A | large | ~10 | 1x |

## Advanced Options

### Language Detection
```python
# Auto-detect language
result = model.transcribe("audio.mp3")
print(f"Detected language: {result['language']}")

# Specify language
result = model.transcribe("audio.mp3", language="en")
```

### Task Types
```python
# Transcribe (default)
result = model.transcribe("audio.mp3", task="transcribe")

# Translate to English
result = model.transcribe("audio.mp3", task="translate")
```

### Temperature Control
```python
# Lower temperature = more deterministic
result = model.transcribe("audio.mp3", temperature=0.0)

# Higher temperature = more creative
result = model.transcribe("audio.mp3", temperature=0.5)
```

### Beam Search
```python
# Use beam search for better accuracy
result = model.transcribe("audio.mp3", beam_size=5)
```

## Output Formats

### Plain Text
```python
result = model.transcribe("audio.mp3")
with open("output.txt", "w") as f:
    f.write(result["text"])
```

### SRT (SubRip)
```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")

with open("output.srt", "w") as f:
    for i, segment in enumerate(result["segments"]):
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        f.write(f"{i + 1}\n")
        f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
        f.write(f"{text}\n\n")

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
```

### VTT (WebVTT)
```python
import whisper

model = whisper.load_model("base")
result = model.transcribe("audio.mp3")

with open("output.vtt", "w") as f:
    f.write("WEBVTT\n\n")
    for segment in result["segments"]:
        start = segment["start"]
        end = segment["end"]
        text = segment["text"]
        f.write(f"{format_timestamp(start)} --> {format_timestamp(end)}\n")
        f.write(f"{text}\n\n")

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"
```

## Performance Optimization

### Use Smaller Models for Faster Transcription
```python
# Use tiny model for quick transcription
model = whisper.load_model("tiny")
```

### Use GPU Acceleration
```python
# Use CUDA if available
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"
model = whisper.load_model("base", device=device)
```

### Batch Processing
```python
import os
import whisper

model = whisper.load_model("base")

for audio_file in os.listdir("audio_files"):
    if audio_file.endswith((".mp3", ".wav", ".m4a")):
        result = model.transcribe(f"audio_files/{audio_file}")
        with open(f"transcripts/{audio_file}.txt", "w") as f:
            f.write(result["text"])
```

## Error Handling

### Common Errors

#### File Not Found
```python
try:
    result = model.transcribe("audio.mp3")
except FileNotFoundError:
    print("Audio file not found")
```

#### Unsupported Format
```python
try:
    result = model.transcribe("audio.mp3")
except Exception as e:
    print(f"Error: {e}")
    # Try converting to WAV first
```

#### Out of Memory
```python
# Use smaller model or CPU
model = whisper.load_model("tiny", device="cpu")
```

## Best Practices

1. **Use Appropriate Model Size** - Balance between speed and accuracy
2. **Pre-process Audio** - Remove noise and normalize volume
3. **Specify Language** - Improves accuracy for known languages
4. **Handle Long Audio** - Split long files into segments
5. **Post-process Text** - Clean up punctuation and formatting

## Resources

- [OpenAI Whisper GitHub](https://github.com/openai/whisper)
- [Whisper Paper](https://arxiv.org/abs/2212.04356)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
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
