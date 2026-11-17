# 🎧 Gemini Text-to-Audio

**Turn any text, article, or textbook PDF into spoken audio, for free, with one command.**

Not everyone can, or wants to, read from a screen. This small Python tool takes a PDF, a text file, or anything you type and turns it into a natural-sounding `.wav` audio file using Google's Gemini text-to-speech. Listen on your phone, on a walk, on the bus, or with your eyes closed.

```bash
python text_to_audio.py chapter1.pdf --pages 1-5
```

---

## 💡 Why this is useful

Reading is not equally easy for everyone. Listening can make learning more accessible and more flexible.

| Who | How it helps |
|---|---|
| 📚 **Students** | Turn lecture notes, chapters, and papers into audio to review while commuting, cooking, or exercising. |
| 🧠 **People with dyslexia or ADHD** | Hearing text while following along can reduce reading strain and help focus. |
| 👁️ **People with low vision or eye strain** | Give your eyes a rest, or get a spoken version of material that is hard to read on a screen. |
| 🌍 **Language learners** | Hear correct pronunciation and natural rhythm, in over 100 languages. |
| 🚗 **Busy people** | Catch up on reports, articles, and documents hands-free. |
| ✍️ **Writers and editors** | Hear your own draft read aloud to catch awkward sentences and typos. |

> This tool is a handy study and reading aid. It is not a replacement for professional assistive technology such as dedicated screen readers.

---

## ✨ Features

- 📄 Reads **PDFs**, **text files**, or **text typed on the command line**
- 📑 Pick just the pages you need (`--pages 5-12`)
- 🗣️ Choose from many voices (Kore, Puck, Charon, Fenrir, Zephyr, and more)
- 🎭 Optional speaking style (`--style "calm and slow"`)
- ✂️ Automatically splits long documents into chunks and joins them into **one audio file**
- 🔁 Resume a long job where it stopped (`--start 12`)
- 🧪 `--dry-run` previews the plan without using any quota
- 🆓 Works with the **free Gemini API tier**, with no credit card needed
- 🪶 Tiny: one script, one dependency (`pypdf`)

---

## 🚀 Quick start

### 1. Get a free API key
1. Go to [aistudio.google.com](https://aistudio.google.com) and sign in with a Google account.
2. Click **Get API key** → **Create API key**.
3. Copy the key and **keep it private**.

### 2. Install

```bash
git clone https://github.com/Shailja-Jindal/gemini-text-to-audio.git
cd gemini-text-to-audio

python -m venv venv
# Windows PowerShell:  venv\Scripts\activate
# Mac / Linux:         source venv/bin/activate

pip install -r requirements.txt
```

> **Windows tip:** if PowerShell blocks activation, run
> `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once.

### 3. Set your key

```powershell
# Windows PowerShell
$env:GEMINI_API_KEY="your-key-here"
```
```bash
# Mac / Linux
export GEMINI_API_KEY="your-key-here"
```

### 4. Make some audio

```bash
python text_to_audio.py --text "Hello! This is my first audio project."
```

Open the `speech_audio.wav` file that appears in the folder. 🎉

---

## 📖 Usage

```bash
# Speak a sentence
python text_to_audio.py --text "Studying is easier when you can listen."

# Convert a whole text file
python text_to_audio.py notes.txt

# Convert only pages 5 to 12 of a PDF
python text_to_audio.py textbook.pdf --pages 5-12

# Different voice and speaking style
python text_to_audio.py notes.txt --voice Puck --style "calm and slow"

# Preview how long a document will take (no API calls)
python text_to_audio.py textbook.pdf --dry-run

# Resume a long job from chunk 12
python text_to_audio.py textbook.pdf --start 12
```

### Options

| Option | What it does |
|---|---|
| `file` | PDF or text file to read |
| `--text "..."` | Speak this text instead of a file |
| `--pages 5-12` | PDF page range |
| `--voice NAME` | Voice to use (default `Kore`) |
| `--style "..."` | Optional delivery style, e.g. `"warm and friendly"` |
| `--out file.wav` | Custom output filename |
| `--start N` | Resume from chunk number N |
| `--dry-run` | Show chunk count and estimated length, with no API calls |

**Voices to try:** Kore, Puck, Charon, Fenrir, Zephyr, Aoede, Leda, Orus, Sulafat, Achird.

---

## ⚙️ How it works

1. **Extract**: reads text from your PDF or file and cleans it up (fixes words split across lines, joins broken sentences).
2. **Chunk**: splits the text into pieces of about 1,500 characters at sentence boundaries.
3. **Speak**: sends each chunk to Gemini's text-to-speech model, with automatic retries and a fallback model if one is busy.
4. **Join**: stitches all the audio into a single `.wav` file.

---

## ⚠️ Limitations

- **Scanned PDFs won't work.** If a PDF is just pictures of pages, there is no text to read. It needs OCR first.
- **Free tier has limits.** Long books may hit rate or daily limits. The script waits and retries, and tells you where to resume with `--start`.
- **Preview models.** Google's TTS models change often. If a model name stops working, update the `MODELS` list at the top of `text_to_audio.py`.
- **Large files.** WAV audio is uncompressed, roughly 3 MB per minute. Convert to MP3 with a tool like [ffmpeg](https://ffmpeg.org) if you need smaller files.
- **Privacy.** Your text is sent to Google's API to be converted. Don't use confidential documents. On the free tier, Google may use inputs to improve its products.
- **Copyright.** Use this for material you have the right to use, such as your own notes or textbooks for personal study.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| `Set GEMINI_API_KEY first` | Set the key in the **same** terminal window you run the script from. |
| `HTTP 429` / `limit: 0` | Free-tier limit reached, or TTS not available for your key. Wait and retry. |
| `HTTP 404` / `NOT_FOUND` | The model name changed. Update `MODELS` in the script. |
| `No text found` | The PDF is scanned images. Use an OCR tool first. |
| PowerShell won't activate the venv | Run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`. |

---

## 🗺️ Ideas for the future

- [ ] MP3 output
- [ ] OCR support for scanned PDFs
- [ ] Simple web interface (drag and drop a PDF)
- [ ] Read-along highlighting
- [ ] Offline fallback voice
- [ ] Support for EPUB and Word files

Contributions and ideas are welcome. Open an issue or a pull request!

---

## 🔒 Keep your key safe

Never put your API key in the code or commit it to GitHub. This project reads it from the `GEMINI_API_KEY` environment variable, and `.gitignore` is set up to keep `.env` files and audio output out of your repository.

## 📄 License

MIT. Free to use, modify, and share.

---

Built with Python and the [Gemini API](https://ai.google.dev). Made to make reading more accessible. 💙
