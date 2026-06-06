---
name: youtube-transcript
version: 2.3.0
description: "High-performance extraction of YouTube transcripts with AI fallback (Whisper) and advanced deduplication."
category: automation
---

## 🔒 Prerequisites (Mandatory)
This skill operates WITHIN the **SDD** framework. Before starting any technical execution:

0. **Mode Check**: Verify `.hub-mode` and apply `token-distiller` guidelines.
1. **Session Bootstrap**:
   - Rehydrate context from `.specs/project/STATE.md`, `.specs/project/MEMORY.md`, and `.specs/project/LEARNINGS.md`.
   - Align with `onboarding-navigator` for project culture.
2. **SDD Verification**:
   - Validate if `spec.md` and `plan.md` exist for the target feature in `.specs/features/`.
   - Perform a final review against the Acceptance Criteria (ACs).
3. **Task Integrity**: Ensure tasks in `tasks.md` are atomized and mapped to Git commits with evidence.

---

# YouTube Transcript Expert (v2.3.0)

> "Content is king, but structure is the kingdom. Precision in extraction, rigor in cleanup."

---

## 🎯 Goal
Provide a fast and robust mechanism to obtain textual content from YouTube videos, prioritizing existing captions (manual or automatic) to save resources, and using AI models (Whisper) only as a verified fallback.

---

## 🧩 Protocol (4-Phase Workflow)

### Phase 1: DISCOVERY (Metadata & Mapping)
*   **Goal**: Understand the video's available resources.
*   **Action**: Execute `yt-dlp --get-title --list-subs "{{url}}"`.
*   **Logic**: Map if manual captions exist for the desired language.

### Phase 2: SPECIFY (Selection Strategy)
Choose the source in order of descending accuracy:
1.  **Manual Subtitles** (`--write-sub`): Highest accuracy. Use VTT format.
2.  **Automatic Subtitles** (`--write-auto-sub`): Medium accuracy. Download if manual is unavailable.
3.  **AI Fallback (Whisper)**: Last resort.
    - Download audio only (`bestaudio`).
    - Run: `uv run --with openai-whisper whisper audio_file.mp3 --model base`.

### Phase 3: IMPLEMENT (Advanced Cleanup)
Process the raw output (VTT or Whisper) through the standard deduplication script.

**Deduplication Logic (Why?)**: Automatic captions often "roll" text, repeating previous lines. The script deduplicates by checking if a new line starts with the previous one.

```python
# standard-cleanup.py
import sys, re

def clean_transcript(content):
    lines = content.split('\n')
    cleaned = []
    for line in lines:
        if '-->' in line or line.strip() == 'WEBVTT' or line.strip().isdigit():
            continue
        line = re.sub(r'<[^>]+>', '', line).strip()
        if line: cleaned.append(line)

    final = []
    for line in cleaned:
        if not final:
            final.append(line)
            continue
        if line.startswith(final[-1]):
            final[-1] = line
        else:
            final.append(line)
    return ' '.join(final)

if __name__ == "__main__":
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        print(clean_transcript(f.read()))
```

### Phase 4: VERIFY (Delivery & Cleanup)
1.  Save as `{video_title}.txt`.
2.  Purge temporary files (`.vtt`, `.mp3`, `.wav`).
3.  Validate readability.

---

## 🏗️ Output Structure
- **Transcript (.txt)**: Cleaned, plain-text content.
- **Metadata**: Filename based on sanitized video title.

---

## ⚖️ Quality Rules
- **Manual > Auto > Whisper**: Never use AI if captions exist.
- **Resource Economy**: Never download video files; audio or text only.
- **Cleanliness**: Zero HTML tags or timestamps in the final delivery.

---

## 🚫 Prohibited
- NEVER commit audio files to the repository.
- NEVER skip the deduplication phase for auto-captions.
- NEVER overwrite files without user verification.

---

> **Law of the Transcript**: A transcript without cleanup is just noise. Precision is the metric of success.

---

<!-- @sdd-state -->
```yaml
version: "2.3.0"
feature_id: "YT-TRANSCRIPT-ALIGNMENT"
phase: "IMPLEMENT"
status: "COMPLETED"
last_update: "2026-05-06T10:11:00Z"
evidence_checksum: "8e52f6a"
```
