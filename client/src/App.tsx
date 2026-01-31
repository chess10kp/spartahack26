import { useEffect, useState } from 'react';
import { useStore } from './store/useStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useScreenshots } from './hooks/useScreenshots';
import { Task } from './types';
import { ServerConfig } from './components/ServerConfig';
import { CapabilitiesInput } from './components/CapabilitiesInput';
import { TaskList } from './components/TaskList';
import { TeamOverview } from './components/TeamOverview';
import './App.css';

function App() {
  const [connectionError, setConnectionError] = useState<string>();
  const { currentView, myTasks, tasks, updateTaskStatus, screenshots, connectionError: storeError } = useStore();
  const { sendMessage, isConnected } = useWebSocket();
  const { captureNow } = useScreenshots();

  useEffect(() => {
    if (storeError) {
      setConnectionError(storeError);
    }
  }, [storeError]);

  useEffect(() => {
    const savedScreenshots = localStorage.getItem('screenshots');
    if (savedScreenshots) {
      const parsed = JSON.parse(savedScreenshots);
      useStore.setState({ screenshots: parsed });
    }
  }, []);

  const handleStatusChange = async (taskId: string, status: Task['status']) => {
    updateTaskStatus(taskId, status);
    
    const latestScreenshot = screenshots[0];
    
    sendMessage({
      type: 'progress_update',
      data: {
        taskId,
        status,
        timestamp: new Date().toISOString(),
        screenshot: latestScreenshot?.data
      }
    });
  };

  const handleCaptureScreenshot = async (taskId: string) => {
    try {
      await captureNow(taskId);
    } catch (error) {
      console.error('Failed to capture screenshot:', error);
      alert('Failed to capture screenshot. Please try again.');
    }
  };

  return (
    <main className="container">
      {connectionError && (
        <div style={{
          backgroundColor: '#ffebee',
          color: '#c62828',
          padding: '12px',
          borderRadius: '8px',
          marginBottom: '20px',
          border: '1px solid #ef9a9a'
        }}>
          Connection Error: {connectionError}
        </div>
      )}

      {currentView === 'config' && <ServerConfig />}
      
      {currentView === 'capabilities' && <CapabilitiesInput />}
      
      {currentView === 'dashboard' && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
            <h1>Dashboard</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: isConnected ? '#4caf50' : '#f44336'
              }} />
              <span style={{ fontSize: '14px', color: '#666' }}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px' }}>
            <div>
              <h2>My Tasks ({myTasks.length})</h2>
              <TaskList 
                tasks={myTasks} 
                onStatusChange={handleStatusChange}
                onCaptureScreenshot={handleCaptureScreenshot}
              />
            </div>

            <div>
              <h2>All Tasks ({tasks.length})</h2>
              <TaskList 
                tasks={tasks} 
                onStatusChange={handleStatusChange}
                onCaptureScreenshot={handleCaptureScreenshot}
              />
              
              <div style={{ marginTop: '32px' }}>
                <TeamOverview teamMembers={useStore.getState().teamMembers} />
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

export default App;
