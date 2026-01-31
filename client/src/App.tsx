import { useEffect, useState } from 'react';
import { useStore } from './store/useStore';
import { useWebSocket } from './hooks/useWebSocket';
import { useScreenshots } from './hooks/useScreenshots';
import { Task } from './types';
import { ServerConfig } from './components/ServerConfig';
import { CapabilitiesInput } from './components/CapabilitiesInput';
import { TaskList } from './components/TaskList';
import { TeamOverview } from './components/TeamOverview';
import { Navbar } from './components/Navbar';
import { Card, CardContent } from './components/ui/card';
import './App.css';

function App() {
  const [connectionError, setConnectionError] = useState<string>();
  const { currentView, myTasks, tasks, updateTaskStatus, screenshots, connectionError: storeError } = useStore();
  const { sendMessage } = useWebSocket();
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
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container py-6">
      {connectionError && (
        <Card className="mb-5 border-destructive bg-destructive/10">
          <CardContent className="py-3">
            <span className="text-destructive font-medium">
              Connection Error: {connectionError}
            </span>
          </CardContent>
        </Card>
      )}

      {currentView === 'config' && <ServerConfig />}
      
      {currentView === 'capabilities' && <CapabilitiesInput />}
      
      {currentView === 'dashboard' && (
        <div>
          <div className="flex justify-between items-center mb-6">
            <h1 className="text-2xl font-bold">Dashboard</h1>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h2 className="text-xl font-semibold mb-4">
                My Tasks ({myTasks.length})
              </h2>
              <TaskList 
                tasks={myTasks} 
                onStatusChange={handleStatusChange}
                onCaptureScreenshot={handleCaptureScreenshot}
              />
            </div>

            <div>
              <h2 className="text-xl font-semibold mb-4">
                All Tasks ({tasks.length})
              </h2>
              <TaskList 
                tasks={tasks} 
                onStatusChange={handleStatusChange}
                onCaptureScreenshot={handleCaptureScreenshot}
              />
              
              <div className="mt-8">
                <TeamOverview teamMembers={useStore.getState().teamMembers} />
              </div>
            </div>
          </div>
        </div>
      )}
      </main>
    </div>
  );
}

export default App;
