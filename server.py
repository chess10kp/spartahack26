from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import whisper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model = whisper.load_model("base")
def parse_command(text: str):
    t = text.strip().lower()

    if t == "click":
        return {"type": "COMMAND", "name": "click"}
    if t == "scroll down":
        return {"type": "COMMAND", "name": "scroll_down"}
    if t.startswith("type "):
        return {"type": "COMMAND", "name": "type", "args": text[5:]}
    if t.startswith("open "):
        return {"type": "COMMAND", "name": "open", "args": t[5:]}
    return None

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    # Save upload to temp file
    suffix = ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    result = model.transcribe(tmp_path)
    text = (result.get("text") or "").strip()

    cmd = parse_command(text)

    return {
        "text": text,
        "command": cmd
    }
