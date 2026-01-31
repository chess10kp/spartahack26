import { Task } from '../types';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';

interface TaskItemProps {
  task: Task;
  onStatusChange: (taskId: string, status: Task['status']) => void;
  onCaptureScreenshot: (taskId: string) => void;
}

export function TaskItem({ task, onStatusChange, onCaptureScreenshot }: TaskItemProps) {
  const priorityVariant = {
    low: 'secondary' as const,
    medium: 'default' as const,
    high: 'destructive' as const
  };

  const statusVariant = {
    pending: 'secondary' as const,
    in_progress: 'default' as const,
    completed: 'secondary' as const
  };

  return (
    <Card className="mb-3">
      <CardContent className="pt-4">
        <div className="flex flex-col sm:flex-row justify-between gap-4">
          <div className="flex-1">
            <h3 className="font-semibold text-base mb-2">{task.title}</h3>
            <p className="text-sm text-muted-foreground mb-3">{task.description}</p>
            
            <div className="flex flex-wrap gap-2 mb-2">
              <Badge variant={priorityVariant[task.priority]}>
                {task.priority.toUpperCase()}
              </Badge>
              <Badge variant={statusVariant[task.status]}>
                {task.status.replace('_', ' ').toUpperCase()}
              </Badge>
            </div>

            {task.dependencies.length > 0 && (
              <p className="text-xs text-muted-foreground mt-2">
                Depends on: {task.dependencies.join(', ')}
              </p>
            )}

            {task.deadline && (
              <p className="text-xs text-muted-foreground mt-1">
                Deadline: {new Date(task.deadline).toLocaleDateString()}
              </p>
            )}
          </div>

          <div className="flex flex-col gap-2">
            <div className="flex gap-1">
              <Button
                size="sm"
                variant={task.status === 'pending' ? 'default' : 'outline'}
                onClick={() => onStatusChange(task.id, 'pending')}
                disabled={task.status === 'pending'}
              >
                Pending
              </Button>
              <Button
                size="sm"
                variant={task.status === 'in_progress' ? 'default' : 'outline'}
                onClick={() => onStatusChange(task.id, 'in_progress')}
                disabled={task.status === 'in_progress'}
              >
                In Progress
              </Button>
              <Button
                size="sm"
                variant={task.status === 'completed' ? 'default' : 'outline'}
                onClick={() => onStatusChange(task.id, 'completed')}
                disabled={task.status === 'completed'}
              >
                Completed
              </Button>
            </div>
            
            <Button
              size="sm"
              variant="outline"
              onClick={() => onCaptureScreenshot(task.id)}
            >
              Attach Screenshot
            </Button>

            {task.screenshotIds && task.screenshotIds.length > 0 && (
              <p className="text-xs text-muted-foreground text-center">
                {task.screenshotIds.length} screenshot(s) attached
              </p>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
