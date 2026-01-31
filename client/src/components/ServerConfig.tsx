import { useState, FormEvent } from "react";
import { useStore } from "../store/useStore";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Button } from "./ui/button";

export function ServerConfig() {
  const [localUrl, setLocalUrl] = useState("ws://localhost:8080");
  const [localUsername, setLocalUsername] = useState("Adam Smith");
  const { serverUrl, username, setServerUrl, setUsername, setCurrentView } =
    useStore();

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (localUrl.trim() && localUsername.trim()) {
      setServerUrl(localUrl.trim());
      setUsername(localUsername.trim());
      setCurrentView("capabilities");
    }
  };

  return (
    <div className="container">
      <Card className="max-w-md mx-auto">
        <CardContent>
          <form onSubmit={handleSubmit}>
            <div className="grid gap-4">
              <div className="grid gap-2">
                <Label className="text-foreground" htmlFor="username">
                  Name
                </Label>
                <Input
                  id="username"
                  type="text"
                  value={localUsername || username}
                  onChange={(e) => setLocalUsername(e.target.value)}
                  placeholder="Enter your name"
                  required
                />
              </div>
              <div className="grid gap-2">
                <Label className="text-foreground" htmlFor="serverUrl">
                  WebSocket Server URL
                </Label>
                <Input
                  id="serverUrl"
                  type="text"
                  value={localUrl || serverUrl}
                  onChange={(e) => setLocalUrl(e.target.value)}
                  placeholder="ws://localhost:8080"
                  required
                />
              </div>
              <Button type="submit">Connect</Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
