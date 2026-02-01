import { useEffect, useRef, useState, useCallback } from 'react';

export interface GazeData {
  x: number;
  y: number;
}

export interface UseWebGazerOptions {
  showVideoFeed?: boolean;
  showPredictionPoints?: boolean;
  mirrorVideo?: boolean;
  regressionType?: 'ridge' | 'weightedRidge';
  trackerType?: 'clmtrackr' | 'TMM' | 'patch';
}

interface WebGazer {
  setRegression: (type: string) => WebGazer;
  setTracker: (type: string) => WebGazer;
  setGazeListener: (listener: (data: GazeData | null, clock: number) => void) => WebGazer;
  begin: () => Promise<void>;
  end: () => Promise<void>;
  isReady: () => boolean;
  showPredictionPoints: (show: boolean) => WebGazer;
  showVideoFeed: (show: boolean) => WebGazer;
  params: {
    imgWidth: number;
    imgHeight: number;
  };
  getTracker: () => unknown;
  getRegression: () => unknown;
}

declare global {
  interface Window {
    webgazer: WebGazer;
  }
}

export function useWebGazer(options: UseWebGazerOptions = {}) {
  const {
    showVideoFeed = false,
    showPredictionPoints = false,
    regressionType = 'ridge',
    trackerType = 'clmtrackr',
  } = options;

  const [isReady, setIsReady] = useState(false);
  const [isTracking, setIsTracking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [gazePosition, setGazePosition] = useState<GazeData | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  const webgazerRef = useRef<WebGazer | null>(null);
  const gazeListenerRef = useRef<((data: GazeData | null, clock: number) => void) | null>(null);
  const isTrackingRef = useRef(false);

  const startTracking = useCallback(async () => {
    if (!webgazerRef.current) {
      setError('WebGazer not initialized');
      return;
    }

    try {
      await webgazerRef.current.begin();
      setIsTracking(true);
      isTrackingRef.current = true;
    } catch (err) {
      setError('Failed to start eye tracking');
      console.error(err);
    }
  }, []);

  const stopTracking = useCallback(async () => {
    if (!webgazerRef.current) return;

    try {
      await webgazerRef.current.end();
      setIsTracking(false);
      isTrackingRef.current = false;
      setGazePosition(null);
    } catch (err) {
      console.error('Error stopping WebGazer:', err);
    }
  }, []);

  const setGazeCallback = useCallback((callback: (data: GazeData | null, clock: number) => void) => {
    gazeListenerRef.current = callback;
  }, []);

  useEffect(() => {
    let isMounted = true;

    const initWebGazer = async () => {
      try {
        if (typeof window !== 'undefined' && !window.webgazer) {
          const script = document.createElement('script');
          script.src = 'https://webgazer.cs.brown.edu/webgazer.js';
          script.async = true;
          
          await new Promise<void>((resolve, reject) => {
            script.onload = () => resolve();
            script.onerror = () => reject(new Error('Failed to load WebGazer script'));
            document.head.appendChild(script);
          });
        }

        if (!window.webgazer) {
          throw new Error('WebGazer not available');
        }

        webgazerRef.current = window.webgazer;

        webgazerRef.current
          .setRegression(regressionType)
          .setTracker(trackerType)
          .setGazeListener((data, clock) => {
            if (isMounted && data) {
              setGazePosition({ x: data.x, y: data.y });
            }
            if (gazeListenerRef.current) {
              gazeListenerRef.current(data, clock);
            }
          })
          .showPredictionPoints(showPredictionPoints)
          .showVideoFeed(showVideoFeed);

        setIsReady(true);
      } catch (err) {
        if (isMounted) {
          setError(err instanceof Error ? err.message : 'Failed to initialize WebGazer');
        }
      }
    };

    const checkPermission = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        stream.getTracks().forEach(track => track.stop());
        setHasPermission(true);
      } catch {
        setHasPermission(false);
        setError('Camera permission denied');
      }
    };

    initWebGazer();
    checkPermission();

    return () => {
      isMounted = false;
      if (webgazerRef.current && isTrackingRef.current) {
        webgazerRef.current.end();
      }
    };
  }, [regressionType, trackerType, showPredictionPoints, showVideoFeed]);

  return {
    isReady,
    isTracking,
    error,
    gazePosition,
    hasPermission,
    startTracking,
    stopTracking,
    setGazeCallback,
  };
}

export default useWebGazer;
