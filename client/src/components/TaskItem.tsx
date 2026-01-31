import { Task } from '../types';

interface TaskItemProps {
  task: Task;
  onStatusChange: (taskId: string, status: Task['status']) => void;
  onCaptureScreenshot: (taskId: string) => void;
}

export function TaskItem({ task, onStatusChange, onCaptureScreenshot }: TaskItemProps) {
  const priorityColors = {
    low: '#4caf50',
    medium: '#ff9800',
    high: '#f44336'
  };

  const statusColors = {
    pending: '#9e9e9e',
    in_progress: '#2196f3',
    completed: '#4caf50'
  };

  return (
    <div style={{ 
      border: '1px solid #ddd', 
      borderRadius: '8px', 
      padding: '16px', 
      marginBottom: '12px',
      backgroundColor: '#fff'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1 }}>
          <h3 style={{ margin: '0 0 8px 0' }}>{task.title}</h3>
          <p style={{ margin: '0 0 8px 0', color: '#666' }}>{task.description}</p>
          
          <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
            <span style={{
              backgroundColor: priorityColors[task.priority],
              color: 'white',
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: 'bold'
            }}>
              {task.priority.toUpperCase()}
            </span>
            <span style={{
              backgroundColor: statusColors[task.status],
              color: 'white',
              padding: '2px 8px',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: 'bold'
            }}>
              {task.status.replace('_', ' ').toUpperCase()}
            </span>
          </div>

          {task.dependencies.length > 0 && (
            <p style={{ fontSize: '12px', color: '#888', margin: '4px 0' }}>
              Depends on: {task.dependencies.join(', ')}
            </p>
          )}

          {task.deadline && (
            <p style={{ fontSize: '12px', color: '#888', margin: '4px 0' }}>
              Deadline: {new Date(task.deadline).toLocaleDateString()}
            </p>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', gap: '4px' }}>
            <button
              onClick={() => onStatusChange(task.id, 'pending')}
              disabled={task.status === 'pending'}
              style={{
                padding: '4px 8px',
                fontSize: '11px',
                backgroundColor: task.status === 'pending' ? '#9e9e9e' : '#e0e0e0',
                cursor: task.status === 'pending' ? 'default' : 'pointer'
              }}
            >
              Pending
            </button>
            <button
              onClick={() => onStatusChange(task.id, 'in_progress')}
              disabled={task.status === 'in_progress'}
              style={{
                padding: '4px 8px',
                fontSize: '11px',
                backgroundColor: task.status === 'in_progress' ? '#2196f3' : '#e0e0e0',
                cursor: task.status === 'in_progress' ? 'default' : 'pointer'
              }}
            >
              In Progress
            </button>
            <button
              onClick={() => onStatusChange(task.id, 'completed')}
              disabled={task.status === 'completed'}
              style={{
                padding: '4px 8px',
                fontSize: '11px',
                backgroundColor: task.status === 'completed' ? '#4caf50' : '#e0e0e0',
                cursor: task.status === 'completed' ? 'default' : 'pointer'
              }}
            >
              Completed
            </button>
          </div>
          
          <button
            onClick={() => onCaptureScreenshot(task.id)}
            style={{
              padding: '6px 12px',
              fontSize: '12px',
              backgroundColor: '#2196f3',
              color: 'white'
            }}
          >
            📸 Attach Screenshot
          </button>

          {task.screenshotIds && task.screenshotIds.length > 0 && (
            <div style={{ fontSize: '12px', color: '#666', textAlign: 'center' }}>
              {task.screenshotIds.length} screenshot(s) attached
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
