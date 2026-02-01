import { useEffect, useRef, useState, useCallback } from 'react';
import { useWebGazer } from '../hooks/useWebGazer';

interface EyeTrackerProps {
  onGazeUpdate?: (x: number, y: number) => void;
  showDebug?: boolean;
}

export function EyeTracker({ onGazeUpdate, showDebug = false }: EyeTrackerProps) {
  const {
    isReady,
    isTracking,
    error,
    gazePosition,
    hasPermission,
    startTracking,
    stopTracking,
  } = useWebGazer({
    showVideoFeed: showDebug,
    showPredictionPoints: showDebug,
  });

  const [isCalibrating, setIsCalibrating] = useState(false);
  const debugRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (gazePosition && onGazeUpdate) {
      onGazeUpdate(gazePosition.x, gazePosition.y);
    }
  }, [gazePosition, onGazeUpdate]);

  useEffect(() => {
    if (debugRef.current && gazePosition) {
      const marker = debugRef.current.querySelector('.gaze-marker');
      if (marker) {
        (marker as HTMLElement).style.left = `${gazePosition.x}px`;
        (marker as HTMLElement).style.top = `${gazePosition.y}px`;
      }
    }
  }, [gazePosition]);

  const handleStartCalibration = useCallback(async () => {
    setIsCalibrating(true);
    if (!isTracking && isReady) {
      await startTracking();
    }
  }, [isTracking, isReady, startTracking]);

  const handleStopCalibration = useCallback(async () => {
    setIsCalibrating(false);
    if (isTracking) {
      await stopTracking();
    }
  }, [isTracking, stopTracking]);

  if (hasPermission === false) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 rounded text-red-700">
        Camera permission denied. Please allow camera access to use eye tracking.
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 bg-red-100 border border-red-400 rounded text-red-700">
        Error: {error}
      </div>
    );
  }

  return (
    <div className="eye-tracker-container">
      {!isReady && (
        <div className="p-4 bg-yellow-100 border border-yellow-400 rounded text-yellow-700">
          Loading eye tracking...
        </div>
      )}

      {isReady && !isTracking && (
        <div className="space-y-4">
          <p className="text-gray-600">
            Eye tracking is ready. Click "Start" to begin tracking.
          </p>
          <button
            onClick={handleStartCalibration}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Start Eye Tracking
          </button>
        </div>
      )}

      {isTracking && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <span className="text-green-600 font-medium">● Tracking Active</span>
            <button
              onClick={handleStopCalibration}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            >
              Stop
            </button>
          </div>

          {gazePosition && (
            <div className="text-sm text-gray-600">
              Gaze position: ({Math.round(gazePosition.x)}, {Math.round(gazePosition.y)})
            </div>
          )}

          {isCalibrating && (
            <div className="text-sm text-blue-600">
              Calibrating... Move your eyes around the screen and click on different points.
            </div>
          )}
        </div>
      )}

      {showDebug && (
        <div
          ref={debugRef}
          className="fixed inset-0 pointer-events-none"
          style={{ position: 'relative', width: '100%', height: '100vh' }}
        >
          <div
            className="gaze-marker"
            style={{
              position: 'absolute',
              width: '20px',
              height: '20px',
              backgroundColor: 'rgba(255, 0, 0, 0.5)',
              borderRadius: '50%',
              transform: 'translate(-50%, -50%)',
              pointerEvents: 'none',
            }}
          />
        </div>
      )}
    </div>
  );
}

export default EyeTracker;
