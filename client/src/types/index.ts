export interface Capabilities {
  languages: string[];
  frameworks: string[];
}

export type TaskStatus = "pending" | "in_progress" | "completed";
export type TaskPriority = "low" | "medium" | "high";

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  dependencies: string[];
  assignee: string;
  deadline?: string;
  screenshotIds?: string[];
}

export interface ProgressReport {
  taskId: string;
  status: TaskStatus;
  screenshot?: string;
  timestamp: string;
}

export interface TeamMember {
  id: string;
  name: string;
  currentTask?: Task;
  completedTasks: number;
}

export interface Screenshot {
  id: string;
  taskId?: string;
  data: string;
  timestamp: string;
}

export type WebSocketMessageType =
  | "register_capabilities"
  | "tasks_assigned"
  | "task_updated"
  | "team_update"
  | "progress_update";

export interface WebSocketMessage {
  type: WebSocketMessageType;
  data: Capabilities | Task[] | Task | TeamMember[] | ProgressReport;
}

export interface AppState {
  serverUrl: string;
  isConnected: boolean;
  connectionError?: string;
  capabilities: Capabilities | null;
  tasks: Task[];
  myTasks: Task[];
  teamMembers: TeamMember[];
  screenshots: Screenshot[];
  currentView: "config" | "capabilities" | "dashboard";
}

export type AppActions = {
  setServerUrl: (url: string) => void;
  setConnected: (connected: boolean) => void;
  setConnectionError: (error?: string) => void;
  setCapabilities: (caps: Capabilities) => void;
  setTasks: (tasks: Task[]) => void;
  addTask: (task: Task) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  updateTaskStatus: (taskId: string, status: TaskStatus) => void;
  setTeamMembers: (members: TeamMember[]) => void;
  addScreenshot: (screenshot: Screenshot) => void;
  attachScreenshot: (taskId: string, screenshotId: string) => void;
  setCurrentView: (view: AppState["currentView"]) => void;
};
