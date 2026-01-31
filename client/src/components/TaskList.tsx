import { useState } from 'react';
import { Task } from '../types';
import { TaskItem } from './TaskItem';
import { Button } from './ui/button';

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

  const statusCounts = {
    all: tasks.length,
    pending: tasks.filter(t => t.status === 'pending').length,
    in_progress: tasks.filter(t => t.status === 'in_progress').length,
    completed: tasks.filter(t => t.status === 'completed').length
  };

  return (
    <div>
      <div className="flex flex-wrap gap-2 mb-4">
        <Button
          size="sm"
          variant={filter === 'all' ? 'default' : 'outline'}
          onClick={() => setFilter('all')}
        >
          All ({statusCounts.all})
        </Button>
        <Button
          size="sm"
          variant={filter === 'pending' ? 'default' : 'outline'}
          onClick={() => setFilter('pending')}
        >
          Pending ({statusCounts.pending})
        </Button>
        <Button
          size="sm"
          variant={filter === 'in_progress' ? 'default' : 'outline'}
          onClick={() => setFilter('in_progress')}
        >
          In Progress ({statusCounts.in_progress})
        </Button>
        <Button
          size="sm"
          variant={filter === 'completed' ? 'default' : 'outline'}
          onClick={() => setFilter('completed')}
        >
          Completed ({statusCounts.completed})
        </Button>
      </div>

      {filteredTasks.length === 0 ? (
        <div className="text-center py-10 text-muted-foreground border-2 border-dashed rounded-lg">
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
