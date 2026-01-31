import { useState, useCallback, useRef, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { useStore } from '../store/useStore';

export const useScreenshots = () => {
  const [isCapturing, setIsCapturing] = useState(false);
  const [captureInterval, setCaptureInterval] = useState<number | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const { addScreenshot, attachScreenshot } = useStore();

  const captureNow = useCallback(async (taskId?: string) => {
    try {
      setIsCapturing(true);
      const filePath = await invoke<string>('capture_screenshot');
      
      const screenshot = {
        id: Date.now().toString(),
        taskId,
        data: filePath,
        timestamp: new Date().toISOString()
      };

      addScreenshot(screenshot);

      if (taskId) {
        attachScreenshot(taskId, screenshot.id);
      }

      return screenshot;
    } catch (error) {
      console.error('Failed to capture screenshot:', error);
      throw error;
    } finally {
      setIsCapturing(false);
    }
  }, [addScreenshot, attachScreenshot]);

  const startPeriodicCapture = useCallback((intervalMinutes: number = 10, taskId?: string) => {
    stopPeriodicCapture();
    
    const intervalMs = intervalMinutes * 60 * 1000;
    setCaptureInterval(intervalMs);

    intervalRef.current = setInterval(() => {
      captureNow(taskId);
    }, intervalMs);

    console.log(`Started periodic screenshot capture every ${intervalMinutes} minutes`);
  }, [captureNow]);

  const stopPeriodicCapture = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
      setCaptureInterval(null);
      console.log('Stopped periodic screenshot capture');
    }
  }, []);

  useEffect(() => {
    return () => {
      stopPeriodicCapture();
    };
  }, [stopPeriodicCapture]);

  return {
    captureNow,
    startPeriodicCapture,
    stopPeriodicCapture,
    isCapturing,
    captureInterval
  };
};
