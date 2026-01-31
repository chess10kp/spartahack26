import { create } from "zustand";
import { AppState, AppActions } from "../types";

type AppStore = AppState &
  AppActions & {
    logout: () => void;
  };

const savedServerUrl = localStorage.getItem("serverUrl") || "";
const savedUsername = localStorage.getItem("username") || "";
const savedCapabilities = localStorage.getItem("capabilities");

export const useStore = create<AppStore>((set, get) => ({
  serverUrl: savedServerUrl,
  username: savedUsername,
  isConnected: false,
  capabilities: savedCapabilities ? JSON.parse(savedCapabilities) : null,
  tasks: [],
  myTasks: [],
  teamMembers: [],
  screenshots: [],
  currentView: savedServerUrl ? "dashboard" : "config",

  setServerUrl: (url) => {
    localStorage.setItem("serverUrl", url);
    set({ serverUrl: url });
  },

  setUsername: (username) => {
    localStorage.setItem("username", username);
    set({ username });
  },

  setConnected: (connected) =>
    set({ isConnected: connected, connectionError: undefined }),

  setConnectionError: (error) =>
    set({ connectionError: error, isConnected: !error }),

  setCapabilities: (caps) => {
    localStorage.setItem("capabilities", JSON.stringify(caps));
    set({ capabilities: caps });
  },

  setTasks: (tasks) =>
    set({ tasks, myTasks: tasks.filter((task) => task.assignee === "me") }),

  addTask: (task) => {
    const state = get();
    const newTasks = [...state.tasks, task];
    set({
      tasks: newTasks,
      myTasks: newTasks.filter((t) => t.assignee === "me"),
    });
  },

  updateTask: (taskId, updates) => {
    const state = get();
    const newTasks = state.tasks.map((task) =>
      task.id === taskId ? { ...task, ...updates } : task,
    );
    set({
      tasks: newTasks,
      myTasks: newTasks.filter((t) => t.assignee === "me"),
    });
  },

  updateTaskStatus: (taskId, status) => {
    get().updateTask(taskId, { status });
  },

  setTeamMembers: (members) => set({ teamMembers: members }),

  addScreenshot: (screenshot) => {
    const state = get();
    const newScreenshots = [...state.screenshots, screenshot];
    localStorage.setItem("screenshots", JSON.stringify(newScreenshots));
    set({ screenshots: newScreenshots });
  },

  attachScreenshot: (taskId, screenshotId) => {
    const state = get();
    const task = state.tasks.find((t) => t.id === taskId);
    if (task) {
      const screenshotIds = task.screenshotIds || [];
      if (!screenshotIds.includes(screenshotId)) {
        get().updateTask(taskId, {
          screenshotIds: [...screenshotIds, screenshotId],
        });
      }
    }
  },

  setCurrentView: (view) => set({ currentView: view }),

  logout: () => {
    // Clear localStorage
    localStorage.removeItem("serverUrl");
    localStorage.removeItem("username");
    localStorage.removeItem("capabilities");
    localStorage.removeItem("screenshots");

    // Reset state to initial values
    set({
      serverUrl: "",
      username: "",
      isConnected: false,
      capabilities: null,
      tasks: [],
      myTasks: [],
      teamMembers: [],
      screenshots: [],
      currentView: "config",
      connectionError: undefined,
    });
  },
}));
