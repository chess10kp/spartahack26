# Voice Navigation with ElevenLabs STT

This guide explains how to use ElevenLabs Speech-to-Text (STT) API for voice navigation in the voice-nav project.

## Prerequisites

1. **ElevenLabs API Key**: Get your API key from https://elevenlabs.io
2. **Dependencies**: Install the required packages

## Setup

1. Set your ElevenLabs API key as an environment variable:
    ```bash
    export ELEVENLABS_API_KEY=your_api_key_here
    ```

2. (Optional) Set your OpenRouter API key for AI queries:
    ```bash
    export OPENROUTER_API_KEY=your_openrouter_key_here
    ```
   Get your API key from https://openrouter.ai/keys

3. Install dependencies (if not already installed):
    ```bash
    cd voice_nav
    pip install -e .
    ```

## Features

- Microphone recording using `sounddevice` and `soundfile`
- Transcription using ElevenLabs STT API
- Voice command integration with UI element detection
- AI querying via OpenRouter for intelligent responses
- Hotkey support for hands-free operation

## Usage

### Quick Start

1. Run the simple transcription demo:
   ```bash
   python example_elevenlabs.py
   ```

2. Choose option 1 for simple transcription, or option 2 for full voice navigation.

### Programmatic Usage

#### Basic Transcription

```python
from stt_elevenlabs import transcribe_from_mic

# Record and transcribe from microphone
transcript = transcribe_from_mic(duration_sec=4, api_key="your_api_key")
print(f"Transcript: {transcript}")
```

#### File Transcription

```python
from stt_elevenlabs import transcribe_file, record_microphone

# Record audio
temp_file = record_microphone(duration_sec=4)

# Transcribe the file
transcript = transcribe_file(temp_file, api_key="your_api_key")
print(f"Transcript: {transcript}")
```

#### Voice Command Processing

```python
from main import resolve_voice_command, execute_command
from stt_elevenlabs import transcribe_from_mic
import asyncio

# Get transcript from voice
transcript = transcribe_from_mic()

# Process voice command
result = await resolve_voice_command(audio_path="path_to_audio.wav")

# Execute the planned command
await execute_command(result.command)
```

### Hotkey Usage

The voice navigation system supports global hotkeys:

- **E**: Trigger element selection mode
- **Ctrl+Alt+V**: Start voice recording and type the transcript or query AI

Voice commands:
- Say any text to type it directly (e.g., "hello world")
- Say "AI <query>" to query OpenRouter and type the response (e.g., "AI what is Python?")
- The "type " prefix is optional (e.g., both "type hello" and "hello" work)

Examples:
- "hello world" → types "hello world"
- "AI explain quantum physics" → queries AI and types the response
- "type hello" → types "hello" (legacy format still supported)

## API Reference

### `stt_elevenlabs.py`

#### Functions

**`record_microphone(duration_sec=4, sample_rate=16000) -> str`**
- Records audio from the default microphone
- Returns: Path to temporary WAV file
- Parameters:
  - `duration_sec`: Recording duration in seconds
  - `sample_rate`: Audio sample rate (default 16000 Hz)

**`transcribe_file(path, api_key=None, model_id="scribe_v2") -> str`**
- Transcribes an audio file using ElevenLabs STT
- Returns: Transcribed text
- Parameters:
  - `path`: Path to audio file
  - `api_key`: ElevenLabs API key (defaults to env variable)
  - `model_id`: Model to use for transcription

**`transcribe_from_mic(duration_sec=4, sample_rate=16000, api_key=None) -> str`**
- Convenience function: records from mic and transcribes
- Returns: Transcribed text
- Parameters:
  - `duration_sec`: Recording duration in seconds
  - `sample_rate`: Audio sample rate
  - `api_key`: ElevenLabs API key

#### Classes

**`ElevenLabsSTTError`**
- Exception raised when ElevenLabs API returns an error

## Testing

Run the test suite to verify the ElevenLabs integration:

```bash
python test_elevenlabs_stt.py
```

The tests include:
1. Microphone recording
2. File transcription
3. Real-time microphone transcription

## ElevenLabs STT API Details

### Model Options

- `scribe_v1`: Standard model
- `scribe_v1_experimental`: Experimental model
- `scribe_v2`: Enhanced model (recommended, default)

### API Endpoint

```
POST https://api.elevenlabs.io/v1/speech-to-text
```

### Request Format

The API accepts multipart/form-data with:
- `file`: Audio file (WAV, MP3, etc.)
- `model_id`: Model identifier
- `language_code`: Optional language code (ISO-639-1 or ISO-639-3)

### Response Format

```json
{
  "text": "Transcribed text",
  "language_code": "eng",
  "language_probability": 0.95,
  "words": [...]
}
```

## Troubleshooting

### API Key Not Set
```
Error: Missing ELEVENLABS_API_KEY
```
Solution: Set the environment variable `export ELEVENLABS_API_KEY=your_key`

### Microphone Not Working
```
Error: Could not access microphone
```
Solution: Ensure microphone permissions are granted and the device is available

### API Request Failed
```
Error: STT failed 401: Unauthorized
```
Solution: Verify your API key is correct and has not expired

## Examples

See `example_elevenlabs.py` for complete usage examples.

## License

This project uses the ElevenLabs API. See the ElevenLabs terms of service for API usage restrictions.
