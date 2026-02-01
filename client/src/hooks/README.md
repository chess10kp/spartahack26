# Eye Tracking with WebGazer.js

This project uses [WebGazer.js](https://webgazer.cs.brown.edu/), a browser-based eye tracking library that uses the user's webcam to detect gaze position.

## Usage

### Basic Example

```tsx
import { EyeTracker } from './components/EyeTracker';

function App() {
  const handleGazeUpdate = (x: number, y: number) => {
    console.log(`Gaze position: ${x}, ${y}`);
  };

  return (
    <EyeTracker
      onGazeUpdate={handleGazeUpdate}
      showDebug={true}
    />
  );
}
```

### Using the Hook Directly

```tsx
import { useWebGazer } from './hooks/useWebGazer';

function MyComponent() {
  const {
    isReady,
    isTracking,
    gazePosition,
    startTracking,
    stopTracking,
  } = useWebGazer({
    showVideoFeed: true,
    showPredictionPoints: true,
  });

  useEffect(() => {
    if (isReady && !isTracking) {
      startTracking();
    }
  }, [isReady, isTracking]);

  return (
    <div>
      {gazePosition && (
        <p>Gaze: ({gazePosition.x}, {gazePosition.y})</p>
      )}
    </div>
  );
}
```

## Requirements

- Modern browser with webcam support (Chrome, Firefox, Edge, Safari)
- User must grant camera permission
- Adequate lighting for eye detection
- Face visible to the camera

## How It Works

1. WebGazer.js uses computer vision to detect the user's face and eyes from the webcam feed
2. It creates a mapping between eye features and screen positions
3. The model self-calibrates as the user interacts with the page (moves mouse, clicks)
4. Gaze predictions are returned as (x, y) coordinates relative to the viewport

## Privacy

All eye tracking happens entirely in the browser - no video data is sent to any server.

## For Tauri

When running in Tauri, you may need to enable camera permissions. Add this to `tauri.conf.json`:

```json
{
  "app": {
    "windows": [
      {
        "permissions": ["default:default", "core:default", "shell:allow-open"]
      }
    ]
  }
}
```

And in your Tauri permissions configuration, enable camera access.
