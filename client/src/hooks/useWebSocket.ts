import { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { wsService } from '../services/websocket';
import { WebSocketMessage, Task, TeamMember } from '../types';

export const useWebSocket = () => {
  const { serverUrl, isConnected, setConnected, setConnectionError, setTasks, addTask, updateTask, setTeamMembers } = useStore();

  useEffect(() => {
    if (!serverUrl) return;

    const handler = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'tasks_assigned':
          if (Array.isArray(message.data)) {
            setTasks(message.data as Task[]);
          }
          break;
          
        case 'task_updated':
          if (typeof message.data === 'object' && !Array.isArray(message.data)) {
            const task = message.data as Task;
            const existingTask = useStore.getState().tasks.find(t => t.id === task.id);
            if (existingTask) {
              updateTask(task.id, task);
            } else {
              addTask(task);
            }
          }
          break;
          
        case 'team_update':
          if (Array.isArray(message.data)) {
            setTeamMembers(message.data as TeamMember[]);
          }
          break;
          
        case 'register_capabilities':
        case 'progress_update':
          console.log('Received message:', message.type, message.data);
          break;
          
        default:
          console.warn('Unknown message type:', message.type);
      }
    };

    const unsubscribe = wsService.onMessage(handler);

    if (serverUrl && !wsService.isConnected()) {
      try {
        wsService.connect(serverUrl);
        setConnected(true);
        setConnectionError(undefined);
      } catch (error) {
        setConnectionError(error instanceof Error ? error.message : 'Connection failed');
      }
    }

    return () => {
      unsubscribe();
    };
  }, [serverUrl, setConnected, setConnectionError, setTasks, addTask, updateTask, setTeamMembers]);

  const sendMessage = (message: WebSocketMessage) => {
    wsService.send(message);
  };

  const disconnect = () => {
    wsService.disconnect();
    setConnected(false);
  };

  return {
    isConnected,
    sendMessage,
    disconnect
  };
};
