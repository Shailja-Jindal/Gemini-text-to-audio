"""
Text-to-Audio: turn a PDF, text file, or any typed text into a spoken .wav file
using Gemini's free text-to-speech.

Setup:
    pip install pypdf
    PowerShell:  $env:GEMINI_API_KEY="your-key"

Examples:
    python text_to_audio.py chapter1.pdf
    python text_to_audio.py chapter1.pdf --pages 5-12
    python text_to_audio.py notes.txt --voice Puck --style "calm and slow"
    python text_to_audio.py --text "Hello! This is a test of my audio project."
    python text_to_audio.py book.pdf --dry-run        (no API call, shows the plan)
    python text_to_audio.py book.pdf --start 12       (resume from chunk 12)

Voices to try: Kore, Puck, Charon, Fenrir, Zephyr, Aoede, Leda, Orus, Sulafat, Achird
"""
import argparse
import base64
import io
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
import wave
from pathlib import Path

# Tries the first model, then falls back to the second if it keeps failing.
MODELS = ["gemini-3.8-flash-lite-tts", "gemini-3.8-flash-tts"]
RATE, WIDTH, CHANNELS = 24000, 2, 1  # output: 24 kHz, 16-bit mono
CHUNK_CHARS = 1500                   # text sent per request


def parse_pages(spec):
    if not spec:
        return None
    a, _, b = spec.partition("-")
    return int(a), int(b or a)


def read_source(args):
    if args.text:
        return args.text
    p = Path(args.file)
    if not p.exists():
        sys.exit(f"File not found: {p}")
    if p.suffix.lower() == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError:
            sys.exit("Run: pip install pypdf")
        pages = PdfReader(str(p)).pages
        rng = parse_pages(args.pages)
        start, end = (rng[0] - 1, min(rng[1], len(pages))) if rng else (0, len(pages))
        text = "\n\n".join((pages[i].extract_text() or "") for i in range(start, end))
        if not text.strip():
            sys.exit("No text found. This PDF may be scanned images (needs OCR).")
        return text
    return p.read_text(encoding="utf-8", errors="ignore")


def make_chunks(text):
    text = re.sub(r"-\n(\w)", r"\1", text)      # fix words split across lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)  # single newlines -> spaces
    parts = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n{2,}", text) if s.strip()]
    chunks, cur = [], ""
    for s in parts:
        if cur and len(cur) + len(s) + 1 > CHUNK_CHARS:
            chunks.append(cur)
            cur = s
        else:
            cur = f"{cur} {s}".strip()
    if cur:
        chunks.append(cur)
    return chunks


def to_pcm(data):
    """Gemini 3.8 TTS returns a full WAV file; strip its header to get raw PCM."""
    if data[:4] == b"RIFF":
        with wave.open(io.BytesIO(data), "rb") as w:
            return w.readframes(w.getnframes())
    return data  # already raw PCM


API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"


def synthesize(api_key, chunk, voice, style):
    """Call Gemini TTS over plain REST (no SDK, so no version problems)."""
    part = {"text": chunk}
    if style:
        part["speech_metadata"] = {"style": style}
    body = {
        "contents": [{"role": "user", "parts": [part]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"voice": voice}},
        },
    }
    payload = json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}

    for model in MODELS:
        for attempt in range(3):
            req = urllib.request.Request(
                API_URL.format(model=model), data=payload, headers=headers
            )
            try:
                with urllib.request.urlopen(req, timeout=180) as r:
                    resp = json.load(r)
                out = resp["candidates"][0]["content"]["parts"][0]
                b64 = out.get("inlineData", {}).get("data")
                if b64:
                    return to_pcm(base64.b64decode(b64))
                print(f"  [{model}] returned no audio data", flush=True)
                continue
            except urllib.error.HTTPError as e:
                msg = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')}"
            except Exception as e:
                msg = f"{type(e).__name__}: {e}"
            print(f"  [{model}] {msg[:500]}", flush=True)
            if "NOT_FOUND" in msg or "HTTP 404" in msg or "limit: 0" in msg:
                break  # this model won't work for this key; try the next one
            if "HTTP 429" in msg or "RESOURCE_EXHAUSTED" in msg:
                print("  (rate limit hit, waiting 30s...)", flush=True)
                time.sleep(30)
            else:
                time.sleep(3)
    return None


def main():
    ap = argparse.ArgumentParser(description="Turn text or PDFs into spoken audio.")
    ap.add_argument("file", nargs="?", help="PDF or text file")
    ap.add_argument("--text", help="Text to speak instead of a file")
    ap.add_argument("--pages", help="PDF page range, e.g. 5-12")
    ap.add_argument("--voice", default="Kore")
    ap.add_argument("--style", default="", help='Optional, e.g. "calm and slow"')
    ap.add_argument("--out", help="Output .wav filename")
    ap.add_argument("--start", type=int, default=1, help="Resume from this chunk number")
    ap.add_argument("--dry-run", action="store_true", help="Show the plan, no API calls")
    args = ap.parse_args()

    if not args.file and not args.text:
        ap.error("Give a file or use --text \"...\"")

    chunks = make_chunks(read_source(args))
    if not chunks:
        sys.exit("Nothing to read.")
    words = sum(len(c.split()) for c in chunks)
    print(f"{len(chunks)} chunks, about {words} words (~{words // 150} min of audio).")
    if args.dry_run:
        print("Dry run: first chunk preview:\n" + chunks[0][:300])
        return

    if "GEMINI_API_KEY" not in os.environ:
        sys.exit("Set GEMINI_API_KEY first (see the top of this file).")
    api_key = os.environ["GEMINI_API_KEY"]

    stem = Path(args.file).stem if args.file else "speech"
    suffix = f"_from{args.start}" if args.start > 1 else ""
    out = Path(args.out or f"{stem}_audio{suffix}.wav")

    done = 0
    with wave.open(str(out), "wb") as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(WIDTH)
        wf.setframerate(RATE)
        for i in range(args.start - 1, len(chunks)):
            print(f"Chunk {i + 1}/{len(chunks)}...", flush=True)
            pcm = synthesize(api_key, chunks[i], args.voice, args.style)
            if pcm is None:
                print(f"\nStopped at chunk {i + 1} (daily limit or servers busy).")
                print(f"Resume later with:  --start {i + 1}")
                break
            wf.writeframes(pcm)
            done += 1
            time.sleep(4)  # stay under free-tier per-minute limits

    if done:
        print(f"\nSaved: {out}  ({done} chunks)")
    else:
        out.unlink(missing_ok=True)
        print("No audio was created.")


if __name__ == "__main__":
    main()
