"""
Transcript Cleaner for YouTube Videos

Cleans up VTT subtitle files and Whisper transcripts by removing:
- VTT headers and timestamps
- HTML tags
- Extra whitespace
- Redundancies from rolling auto-subs
"""

import re
import sys
from pathlib import Path


def clean_vtt(content: str) -> str:
    """
    Clean VTT subtitle content.

    Args:
        content: Raw VTT content

    Returns:
        Cleaned text without timestamps and metadata
    """
    lines = content.split("\n")
    cleaned = []

    for line in lines:
        # Skip VTT header and metadata
        if line.strip() == "WEBVTT":
            continue
        if "-->" in line:
            continue
        if line.strip().isdigit():
            continue
        if "Kind:" in line or "Language:" in line:
            continue

        # Remove HTML tags and extra whitespace
        line = re.sub(r"<[^>]+>", "", line).strip()

        if line:
            cleaned.append(line)

    # Advanced deduplication for rolling auto-subs
    final = []
    for line in cleaned:
        if not final:
            final.append(line)
            continue

        # If current line starts with previous line, replace previous with current
        if line.startswith(final[-1]):
            final[-1] = line
        else:
            final.append(line)

    return " ".join(final)


def clean_whisper(content: str) -> str:
    """
    Clean Whisper transcript output.

    Args:
        content: Raw Whisper transcript

    Returns:
        Cleaned text with proper formatting
    """
    # Remove any remaining timestamps
    content = re.sub(r"\[\d+:\d+:\d+\.\d+ --> \d+:\d+:\d+\.\d+\]", "", content)

    # Remove extra whitespace
    content = re.sub(r"\s+", " ", content).strip()

    # Fix common punctuation issues
    content = re.sub(r"\s+([.,!?;:])", r"\1", content)

    return content


def clean_transcript(input_file: Path, output_file: Path | None = None) -> str:
    """
    Clean a transcript file.

    Args:
        input_file: Path to input transcript file
        output_file: Optional path to output file

    Returns:
        Cleaned transcript text
    """
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    with open(input_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Determine file type and clean accordingly
    if input_file.suffix == ".vtt":
        cleaned = clean_vtt(content)
    else:
        cleaned = clean_whisper(content)

    # Write to output file if specified
    if output_file:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(cleaned)

    return cleaned


def main():
    """Main entry point for CLI usage."""
    if len(sys.argv) < 2:
        print("Usage: python transcript_cleaner.py <input_file> [output_file]")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    try:
        cleaned = clean_transcript(input_file, output_file)

        if output_file:
            print(f"✅ Cleaned transcript saved to: {output_file}")
        else:
            print(cleaned)

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
