import { useState, FormEvent } from 'react';
import { useStore } from '../store/useStore';

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
      <h1>Server Configuration</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="serverUrl">WebSocket Server URL:</label>
          <input
            id="serverUrl"
            type="text"
            value={localUrl}
            onChange={(e) => setLocalUrl(e.target.value)}
            placeholder="ws://localhost:8080"
            required
          />
          {serverUrl && (
            <p style={{ marginTop: '10px', color: '#666' }}>
              Current: {serverUrl}
            </p>
          )}
        </div>
        <button type="submit">Connect</button>
      </form>
    </div>
  );
}
