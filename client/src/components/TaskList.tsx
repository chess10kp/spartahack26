import { useState } from 'react';
import { Task } from '../types';
import { TaskItem } from './TaskItem';

interface TaskListProps {
  tasks: Task[];
  onStatusChange: (taskId: string, status: Task['status']) => void;
  onCaptureScreenshot: (taskId: string) => void;
}

export function TaskList({ tasks, onStatusChange, onCaptureScreenshot }: TaskListProps) {
  const [filter, setFilter] = useState<'all' | Task['status']>('all');

  const filteredTasks = filter === 'all' 
    ? tasks 
    : tasks.filter(task => task.status === filter);

  return (
    <div>
      <div style={{ 
        display: 'flex', 
        gap: '8px', 
        marginBottom: '16px',
        flexWrap: 'wrap'
      }}>
        <button
          onClick={() => setFilter('all')}
          style={{
            padding: '8px 16px',
            backgroundColor: filter === 'all' ? '#2196f3' : '#e0e0e0',
            color: filter === 'all' ? 'white' : '#333'
          }}
        >
          All ({tasks.length})
        </button>
        <button
          onClick={() => setFilter('pending')}
          style={{
            padding: '8px 16px',
            backgroundColor: filter === 'pending' ? '#9e9e9e' : '#e0e0e0',
            color: filter === 'pending' ? 'white' : '#333'
          }}
        >
          Pending ({tasks.filter(t => t.status === 'pending').length})
        </button>
        <button
          onClick={() => setFilter('in_progress')}
          style={{
            padding: '8px 16px',
            backgroundColor: filter === 'in_progress' ? '#2196f3' : '#e0e0e0',
            color: filter === 'in_progress' ? 'white' : '#333'
          }}
        >
          In Progress ({tasks.filter(t => t.status === 'in_progress').length})
        </button>
        <button
          onClick={() => setFilter('completed')}
          style={{
            padding: '8px 16px',
            backgroundColor: filter === 'completed' ? '#4caf50' : '#e0e0e0',
            color: filter === 'completed' ? 'white' : '#333'
          }}
        >
          Completed ({tasks.filter(t => t.status === 'completed').length})
        </button>
      </div>

      {filteredTasks.length === 0 ? (
        <div style={{ 
          textAlign: 'center', 
          padding: '40px', 
          color: '#999',
          border: '2px dashed #ddd',
          borderRadius: '8px'
        }}>
          No tasks found
        </div>
      ) : (
        filteredTasks
          .sort((a, b) => {
            const priorityOrder = { high: 0, medium: 1, low: 2 };
            return priorityOrder[a.priority] - priorityOrder[b.priority];
          })
          .map(task => (
            <TaskItem
              key={task.id}
              task={task}
              onStatusChange={onStatusChange}
              onCaptureScreenshot={onCaptureScreenshot}
            />
          ))
      )}
    </div>
  );
}
