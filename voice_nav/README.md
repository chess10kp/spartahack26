# Voice Navigation - Element Selection

A Python-based system for screenshot capture, element detection using CV, and interactive element selection with voice control.

## Features

- **Screen Capture**: Takes full-screen screenshots using PIL
- **Element Detection**: Uses OpenCV Canny edge detection and contour analysis to detect UI elements
- **Hint-based Selection**: Assigns keyboard-friendly hints (asdfghjkl) to detected elements
- **Automatic Clicking**: Clicks on selected elements using pynput
- **Voice Control**: Uses ElevenLabs Speech-to-Text API for voice commands
- **AI Command Planning**: Plans actions based on voice commands and detected elements
- **AI Query**: Query OpenRouter AI for intelligent responses via voice commands

## Installation

1. Clone the repository
2. Install Python dependencies using uv:
   ```bash
   uv sync
   ```

## Usage

### Voice Control with ElevenLabs

1. Set your ElevenLabs API key:
    ```bash
    export ELEVENLABS_API_KEY=your_api_key_here
    ```

2. (Optional) Set your OpenRouter API key for AI queries:
    ```bash
    export OPENROUTER_API_KEY=your_openrouter_key_here
    ```

2. Run the voice navigation demo:
   ```bash
   python example_elevenlabs.py
   ```

3. Test the ElevenLabs integration:
   ```bash
   python test_elevenlabs_stt.py
   ```

For detailed documentation on ElevenLabs STT integration, see [ELEVENLABS_README.md](ELEVENLABS_README.md).

### CLI Mode (No system dependencies)

Run the CLI-based element selector:
```bash
.venv/bin/python element_selector_cli.py
```

This will:
1. Capture the screen
2. Detect UI elements
3. Display a list of hints
4. Prompt you to enter a hint
5. Click on the selected element

### Voice Commands

Use voice to type text or query AI:

1. Set up API keys (ElevenLabs required, OpenRouter optional for AI)
2. Run the voice navigation system:
   ```bash
   .venv/bin/python main.py
   ```
3. Press `Ctrl+Alt+V` and speak:
   - "hello world" → Types "hello world" at cursor
   - "AI what is Python?" → Queries OpenRouter AI and types the response
   - "type hello" → Types "hello" (legacy format)

**AI Query Examples:**
- "AI explain quantum physics"
- "AI what's the capital of France"
- "ask AI how to write a for loop in Python"

### GUI Mode (Requires system packages)

To use the graphical overlay, install system packages:
```bash
sudo pacman -S python-pycairo python-pygobject
```

Then run:
```bash
.venv/bin/python main.py
```

This starts a background daemon that listens for `Ctrl+Alt+E` to trigger element selection.

## Architecture

```
Screenshot Capture (PIL.ImageGrab)
    ↓
Element Detection (OpenCV)
    - Canny edge detection
    - Contour finding
    - Bounding box extraction
    ↓
Hint Generation
    - Maps alphabet (asdfghjkl) to elements
    - Uses product() for multi-character hints
    ↓
User Selection
    - CLI: Type hint to select
    - GUI: Hint labels overlay on elements
    ↓
Click Execution (pynput)
    - Moves mouse to element center
    - Performs click action
```

## Files

- `element_selector_cli.py` - CLI-based element selector (no GUI dependencies)
- `element_selector.py` - GUI-based selector using GTK (requires PyGObject)
- `minimal_overlay.py` - GTK overlay window for hint display
- `child.py` - Element representation class
- `mouse.py` - Mouse control using pynput
- `mouse_enums.py` - Mouse button and state enums
- `main.py` - Main daemon with hotkey listener
- `stt.py` - Whisper-based speech-to-text module
- `stt_elevenlabs.py` - ElevenLabs STT integration module
- `ai_client.py` - OpenRouter AI client for intelligent responses
- `typing_control.py` - Keyboard typing helpers using pynput
- `planner.py` - AI command planning for voice commands
- `schemas.py` - Data models for commands and blocks
- `example_elevenlabs.py` - Example usage of ElevenLabs STT
- `test_elevenlabs_stt.py` - Tests for ElevenLabs integration
- `test_voice_nav.py` - Voice navigation system tests
- `ELEVENLABS_README.md` - Detailed documentation for ElevenLabs integration

## Configuration

Edit `element_selector_cli.py` or `element_selector.py` to adjust detection parameters:

- `canny_min_val`: Canny edge detection minimum threshold (default: 50)
- `canny_max_val`: Canny edge detection maximum threshold (default: 150)
- `kernel_size`: Dilation kernel size (default: 3)
- Element size filters in `detect_elements()`

## Example Output

```
Detected 208 elements:

Type hint to select element, or 'q' to quit:

Elements:
  aaa: Position (21, 1005), Size 49x34
  aas: Position (1564, 976), Size 28x27
  aad: Position (817, 976), Size 30x26
  ...

Enter hint: aas
Clicked at (1578, 989)
```
