import tempfile
import os
import subprocess
import whisper

_model = whisper.load_model("base")

async def transcribe_audio(audio_upload):
    raw = await audio_upload.read()

    # Save upload
    with tempfile.NamedTemporaryFile(delete=False, suffix=".input") as f:
        f.write(raw)
        in_path = f.name

    # Convert to wav 16k mono (handles webm/opus too if ffmpeg installed)
    out_path = in_path + ".wav"
    subprocess.run([
        "ffmpeg", "-y", "-i", in_path,
        "-ac", "1", "-ar", "16000", "-vn",
        out_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    result = _model.transcribe(out_path)
    text = (result.get("text") or "").strip()

    # cleanup
    for p in [in_path, out_path]:
        try: os.remove(p)
        except: pass

    return text
