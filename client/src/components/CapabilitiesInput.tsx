import { useState, FormEvent } from 'react';
import { useStore } from '../store/useStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { Capabilities } from '../types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';

export function CapabilitiesInput() {
  const [languages, setLanguages] = useState('');
  const [frameworks, setFrameworks] = useState('');
  const { setCapabilities, setCurrentView, capabilities } = useStore();
  const { sendMessage } = useWebSocket();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    const caps: Capabilities = {
      languages: languages.split(',').map(s => s.trim()).filter(Boolean),
      frameworks: frameworks.split(',').map(s => s.trim()).filter(Boolean)
    };

    setCapabilities(caps);
    sendMessage({ type: 'register_capabilities', data: caps });
    setCurrentView('dashboard');
  };

  if (capabilities) {
    return (
      <div className="container">
        <Card className="max-w-md mx-auto">
          <CardHeader>
            <CardTitle>Your Capabilities</CardTitle>
            <CardDescription>
              These are your registered capabilities
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4">
              <div>
                <Label>Languages</Label>
                <p className="text-sm text-muted-foreground mt-1">
                  {capabilities.languages.join(', ')}
                </p>
              </div>
              <div>
                <Label>Frameworks & Libraries</Label>
                <p className="text-sm text-muted-foreground mt-1">
                  {capabilities.frameworks.join(', ')}
                </p>
              </div>
              <Button onClick={() => setCurrentView('dashboard')}>
                Go to Dashboard
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Set Your Capabilities</CardTitle>
          <CardDescription>
            Tell us about your technical skills and expertise
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="languages">
                  Programming Languages (comma-separated)
                </Label>
                <Input
                  id="languages"
                  type="text"
                  value={languages}
                  onChange={(e) => setLanguages(e.target.value)}
                  placeholder="Python, JavaScript, Rust"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="frameworks">
                  Frameworks & Libraries (comma-separated)
                </Label>
                <Input
                  id="frameworks"
                  type="text"
                  value={frameworks}
                  onChange={(e) => setFrameworks(e.target.value)}
                  placeholder="React, Django, Tauri"
                  required
                />
              </div>
              <Button type="submit">Register & Continue</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
