import { TeamMember } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Badge } from './ui/badge';

interface TeamOverviewProps {
  teamMembers: TeamMember[];
}

export function TeamOverview({ teamMembers }: TeamOverviewProps) {
  if (teamMembers.length === 0) {
    return (
      <Card>
        <CardContent className="py-10 text-center text-muted-foreground">
          No team members available
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Team Overview</CardTitle>
      </CardHeader>
      <CardContent className="grid gap-4">
        {teamMembers.map(member => (
          <div
            key={member.id}
            className="flex justify-between items-start gap-4 p-4 border rounded-lg"
          >
            <div className="flex gap-3">
              <Avatar size="lg">
                <AvatarFallback className="bg-primary text-primary-foreground">
                  {member.name.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div>
                <div className="font-semibold">{member.name}</div>
                <div className="text-sm text-muted-foreground">
                  {member.completedTasks} task(s) completed
                </div>
                
                {member.currentTask ? (
                  <div className="text-sm mt-2 p-2 bg-muted rounded">
                    <Badge variant="outline" className="mr-2">Current</Badge>
                    {member.currentTask.title}
                  </div>
                ) : (
                  <div className="text-sm text-muted-foreground italic mt-2">
                    No active task
                  </div>
                )}
              </div>
            </div>

            <div className="text-right">
              <div className="text-2xl font-bold text-green-600">
                {member.completedTasks}
              </div>
              <div className="text-xs text-muted-foreground">
                Completed
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
