import { useStore } from "../store/useStore";
import { Button } from "./ui/button";
import { cn } from "../lib/utils";
import { useWebSocket } from "../hooks/useWebSocket";

export function Navbar() {
  const { currentView, setCurrentView, isConnected, serverUrl, logout } =
    useStore();
  const { disconnect } = useWebSocket();

  const handleDisconnect = () => {
    disconnect();
    logout();
  };

  return (
    <nav className="border-b bg-card">
      <div className="container flex h-14 items-center justify-between px-4">
        <div className="flex items-center gap-6">
          <div className="font-bold text-lg">SpartaHack26</div>

          <div className="hidden md:flex items-center gap-1">
            <Button
              variant={currentView === "config" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setCurrentView("config")}
            >
              Config
            </Button>
            <Button
              variant={currentView === "capabilities" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setCurrentView("capabilities")}
            >
              Capabilities
            </Button>
            <Button
              variant={currentView === "dashboard" ? "secondary" : "ghost"}
              size="sm"
              onClick={() => setCurrentView("dashboard")}
            >
              Dashboard
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {serverUrl && (
            <span className="text-xs text-muted-foreground hidden sm:inline">
              {serverUrl}
            </span>
          )}

          <div className="flex items-center gap-2">
            <div
              className={cn(
                "w-2 h-2 rounded-full",
                isConnected ? "bg-green-500" : "bg-red-500",
              )}
            />
            <span className="text-xs text-muted-foreground">
              {isConnected ? "Connected" : "Disconnected"}
            </span>
          </div>

          {serverUrl && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleDisconnect}
              className="text-destructive hover:bg-destructive/10 hover:text-destructive"
            >
              Disconnect
            </Button>
          )}
        </div>
      </div>
    </nav>
  );
}
