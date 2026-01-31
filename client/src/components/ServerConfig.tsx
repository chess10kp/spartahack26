import { useState, FormEvent } from 'react';
import { useStore } from '../store/useStore';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';

export function ServerConfig() {
  const [localUrl, setLocalUrl] = useState('');
  const { serverUrl, setServerUrl, setCurrentView } = useStore();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (localUrl.trim()) {
      setServerUrl(localUrl.trim());
      setCurrentView('capabilities');
    }
  };

  return (
    <div className="container">
      <Card className="max-w-md mx-auto">
        <CardHeader>
          <CardTitle>Server Configuration</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label htmlFor="serverUrl">WebSocket Server URL</Label>
                <Input
                  id="serverUrl"
                  type="text"
                  value={localUrl}
                  onChange={(e) => setLocalUrl(e.target.value)}
                  placeholder="ws://localhost:8080"
                  required
                />
                {serverUrl && (
                  <p className="text-sm text-muted-foreground">
                    Current: {serverUrl}
                  </p>
                )}
              </div>
              <Button type="submit">Connect</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
