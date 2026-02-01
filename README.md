# Multimodal Hands-Free Interface  
**Eye Gaze + Hand Gestures + Voice Control with AI Smarts**  
*(Hackathon Project – February 2026)*

![Demo Screenshot Placeholder](https://via.placeholder.com/800x450.png?text=Live+Demo:+Gaze+Cursor+with+Hand+Gestures+and+Voice)  
*(Replace with actual screenshot or GIF of the running app showing webcam feed, overlays, cursor movement, recognized gesture/voice)*

## Overview

This project creates an intelligent, **hands-free human-computer interface** that lets users control their computer using only their eyes, hands, and voice — no mouse, keyboard, or touch required.

- **Eye gaze** (via webcam) moves the cursor naturally and quickly.  
- **Hand gestures** (detected mid-air) handle precise actions: pinch to click, wave/open-palm to scroll, grab-and-drag, etc.  
- **Voice input** handles text typing (dictation) and natural-language commands ("scroll down", "open browser", "type hello world").  
- **AI enhancements** make it smarter: smoother gaze tracking, robust gesture recognition, intent prediction, multimodal fusion to reduce errors, and proactive suggestions.

Built for **accessibility** (motor impairments, RSI relief), experimentation, and as a proof-of-concept for future XR/spatial computing interfaces. Inspired by systems like Apple Vision Pro but runs on a regular laptop with just a webcam and microphone — all in **Python**.

### Key Features
- Real-time cursor control via eye gaze (MediaPipe Face Mesh / Iris landmarks)
- Mid-air hand gestures for click, drag, scroll (MediaPipe Hands + Gesture Recognizer)
- Voice dictation and command parsing (speech recognition + optional lightweight intent understanding)
- AI-powered improvements:
  - Jitter reduction & gaze prediction (Kalman filter / moving average)
  - Pre-trained gesture classification for reliability
  - Multimodal fusion (e.g., gaze highlights + hand confirms + voice disambiguates)
  - Error recovery & feedback (text-to-speech responses)
- Visual overlays in webcam feed for demo (gaze point, hand skeleton, recognized text/gestures)
- Cross-platform (Windows/macOS/Linux tested conceptually)

### Why This Project?
Traditional inputs (mouse + keyboard) are precise but inaccessible for many. Pure eye-tracking fatigues eyes and struggles with clicking. Pure gestures cause "gorilla arm". Voice alone is slow for navigation.

This **hybrid multimodal** approach divides labor naturally:
- Eyes = fast pointing  
- Hands = precise manipulation  
- Voice = rich content/commands  

AI glues it together → reduces fatigue, errors, and feels intuitive.

## Demo Video / Screenshots
*(Add links or embed here once recorded)*

- Live demo GIF: gaze moving cursor, pinch click, voice typing  
- Overlay example: red dot for gaze, green skeleton for hand, text bubble for voice

## Tech Stack
- **Language**: Python 3.10+
- **Computer Vision**:
  - MediaPipe (Google) – Face Mesh / Iris for gaze, Hands for landmarks & built-in Gesture Recognizer
  - OpenCV (cv2) – Webcam capture, drawing overlays
- **Input Control**:
  - pyautogui – Move cursor, click, scroll, type
  - (Alternative: pynput for more events)
- **Voice**:
  - speech_recognition – Microphone input (Google API or Vosk offline)
  - pyttsx3 – Text-to-speech feedback
- **AI / Smoothing**:
  - numpy / scipy – Kalman filter, averaging for gaze stability
  - scikit-learn – Simple ML for fusion / calibration (optional)
  - (Stretch: tiny torch models for intent if feasible)
- **Other**: threading (parallel modalities), time, argparse

**No GPU required** — runs on CPU in real-time (~30 FPS on mid-range laptop).

## Installation

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/multimodal-handsfree.git
   cd multimodal-handsfree
