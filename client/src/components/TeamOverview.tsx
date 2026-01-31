import { TeamMember } from '../types';

interface TeamOverviewProps {
  teamMembers: TeamMember[];
}

export function TeamOverview({ teamMembers }: TeamOverviewProps) {
  if (teamMembers.length === 0) {
    return (
      <div style={{ 
        textAlign: 'center', 
        padding: '40px', 
        color: '#999',
        border: '2px dashed #ddd',
        borderRadius: '8px'
      }}>
        No team members available
      </div>
    );
  }

  return (
    <div>
      <h2 style={{ marginBottom: '16px' }}>Team Overview</h2>
      <div style={{ display: 'grid', gap: '12px' }}>
        {teamMembers.map(member => (
          <div
            key={member.id}
            style={{
              border: '1px solid #ddd',
              borderRadius: '8px',
              padding: '16px',
              backgroundColor: '#fff',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}
          >
            <div>
              <div style={{ 
                display: 'flex', 
                alignItems: 'center', 
                gap: '12px',
                marginBottom: '8px'
              }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  backgroundColor: '#2196f3',
                  color: 'white',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  fontSize: '18px'
                }}>
                  {member.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div style={{ fontWeight: 'bold', fontSize: '16px' }}>{member.name}</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    {member.completedTasks} task(s) completed
                  </div>
                </div>
              </div>
              
              {member.currentTask ? (
                <div style={{ 
                  fontSize: '14px', 
                  color: '#333',
                  marginTop: '8px',
                  padding: '8px',
                  backgroundColor: '#f5f5f5',
                  borderRadius: '4px'
                }}>
                  <strong>Current:</strong> {member.currentTask.title}
                </div>
              ) : (
                <div style={{ 
                  fontSize: '14px', 
                  color: '#999',
                  marginTop: '8px',
                  fontStyle: 'italic'
                }}>
                  No active task
                </div>
              )}
            </div>

            <div style={{ textAlign: 'right' }}>
              <div style={{ 
                fontSize: '24px', 
                fontWeight: 'bold',
                color: '#4caf50'
              }}>
                {member.completedTasks}
              </div>
              <div style={{ fontSize: '12px', color: '#666' }}>
                Completed
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
