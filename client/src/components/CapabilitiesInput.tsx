import { useState, FormEvent } from 'react';
import { useStore } from '../store/useStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { Capabilities } from '../types';

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
        <h1>Capabilities</h1>
        <div style={{ marginBottom: '20px' }}>
          <p><strong>Languages:</strong> {capabilities.languages.join(', ')}</p>
          <p><strong>Frameworks:</strong> {capabilities.frameworks.join(', ')}</p>
        </div>
        <button onClick={() => setCurrentView('dashboard')}>Go to Dashboard</button>
      </div>
    );
  }

  return (
    <div className="container">
      <h1>Set Your Capabilities</h1>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="languages">Programming Languages (comma-separated):</label>
          <input
            id="languages"
            type="text"
            value={languages}
            onChange={(e) => setLanguages(e.target.value)}
            placeholder="Python, JavaScript, Rust"
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="frameworks">Frameworks & Libraries (comma-separated):</label>
          <input
            id="frameworks"
            type="text"
            value={frameworks}
            onChange={(e) => setFrameworks(e.target.value)}
            placeholder="React, Django, Tauri"
            required
          />
        </div>
        <button type="submit">Register & Continue</button>
      </form>
    </div>
  );
}
