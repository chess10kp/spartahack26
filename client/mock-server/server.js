import { WebSocketServer } from "ws";

// Mock data store
const clients = new Map();
const registeredUsers = new Map();

// Sample tasks that will be assigned
const sampleTasks = [
  {
    id: "task-1",
    title: "Design Homepage UI",
    description:
      "Create a modern, responsive homepage design with hero section and feature cards.",
    status: "pending",
    priority: "high",
    dependencies: [],
    assignee: "Alice Chen",
    deadline: "2025-01-20",
  },
  {
    id: "task-2",
    title: "Implement Authentication",
    description: "Build login and registration system with JWT tokens.",
    status: "pending",
    priority: "high",
    dependencies: ["task-1"],
    assignee: "Bob Smith",
    deadline: "2025-01-22",
  },
  {
    id: "task-3",
    title: "Create Dashboard",
    description:
      "Build main dashboard with task overview and team member cards.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-1"],
    assignee: "",
    deadline: "2025-01-25",
  },
  {
    id: "task-4",
    title: "Setup Database",
    description: "Configure PostgreSQL database and create initial schema.",
    status: "pending",
    priority: "high",
    dependencies: [],
    assignee: "Carol White",
    deadline: "2025-01-18",
  },
  {
    id: "task-5",
    title: "Write API Documentation",
    description: "Document all API endpoints using OpenAPI/Swagger.",
    status: "pending",
    priority: "low",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-01-28",
  },
  {
    id: "task-6",
    title: "Implement Real-time Updates",
    description: "Add WebSocket support for live task updates.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-01-26",
  },
  {
    id: "task-7",
    title: "Setup CI/CD Pipeline",
    description:
      "Configure GitHub Actions for automated testing and deployment.",
    status: "pending",
    priority: "medium",
    dependencies: [],
    assignee: "",
    deadline: "2025-01-30",
  },
  {
    id: "task-8",
    title: "Implement Rate Limiting",
    description: "Add API rate limiting to prevent abuse.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-02-01",
  },
  {
    id: "task-9",
    title: "Design User Profile Page",
    description: "Create user profile page with avatar and settings.",
    status: "pending",
    priority: "low",
    dependencies: ["task-1", "task-2"],
    assignee: "",
    deadline: "2025-02-05",
  },
  {
    id: "task-10",
    title: "Add Email Notifications",
    description: "Add email notifications for task assignments.",
    status: "pending",
    priority: "low",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-02-10",
  },
  {
    id: "task-11",
    title: "Implement Search Feature",
    description: "Add full-text search for tasks and team members.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-3", "task-4"],
    assignee: "",
    deadline: "2025-02-15",
  },
  {
    id: "task-12",
    title: "Add Dark Mode Support",
    description: "Implement dark mode theme for the entire application.",
    status: "pending",
    priority: "low",
    dependencies: ["task-1"],
    assignee: "",
    deadline: "2025-02-20",
  },
  {
    id: "task-13",
    title: "Implement File Upload Feature",
    description: "Add file upload functionality for task attachments.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-02-22",
  },
  {
    id: "task-14",
    title: "Add Keyboard Shortcuts",
    description: "Implement keyboard shortcuts for common actions.",
    status: "pending",
    priority: "low",
    dependencies: ["task-3"],
    assignee: "",
    deadline: "2025-02-25",
  },
  {
    id: "task-15",
    title: "Setup Load Testing",
    description: "Configure load tests for API endpoints.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-4"],
    assignee: "",
    deadline: "2025-02-28",
  },
  {
    id: "task-16",
    title: "Implement Audit Logging",
    description: "Add audit logs for user actions and system events.",
    status: "pending",
    priority: "high",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-03-01",
  },
  {
    id: "task-17",
    title: "Create Admin Dashboard",
    description: "Build admin panel for system management.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-3"],
    assignee: "",
    deadline: "2025-03-05",
  },
  {
    id: "task-18",
    title: "Add Two-Factor Authentication",
    description: "Implement 2FA for user account security.",
    status: "pending",
    priority: "high",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-03-08",
  },
  {
    id: "task-19",
    title: "Implement Webhook System",
    description: "Add webhook support for external integrations.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-2"],
    assignee: "",
    deadline: "2025-03-10",
  },
  {
    id: "task-20",
    title: "Add Task Export Feature",
    description: "Implement task export to CSV and PDF formats.",
    status: "pending",
    priority: "low",
    dependencies: ["task-3"],
    assignee: "",
    deadline: "2025-03-12",
  },
  {
    id: "task-21",
    title: "Setup Multi-Language Support",
    description: "Add internationalization (i18n) for multiple languages.",
    status: "pending",
    priority: "low",
    dependencies: ["task-1"],
    assignee: "",
    deadline: "2025-03-15",
  },
  {
    id: "task-22",
    title: "Implement Data Caching",
    description: "Add Redis caching for frequently accessed data.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-4"],
    assignee: "",
    deadline: "2025-03-18",
  },
  {
    id: "task-23",
    title: "Add Real-Time Notifications",
    description: "Implement in-app notification system.",
    status: "pending",
    priority: "medium",
    dependencies: ["task-6"],
    assignee: "",
    deadline: "2025-03-20",
  },
  {
    id: "task-24",
    title: "Create API Rate Limit Dashboard",
    description: "Build dashboard to monitor API usage and rate limits.",
    status: "pending",
    priority: "low",
    dependencies: ["task-8"],
    assignee: "",
    deadline: "2025-03-22",
  },
  {
    id: "task-25",
    title: "Implement Data Backup System",
    description: "Setup automated database backups.",
    status: "pending",
    priority: "high",
    dependencies: ["task-4"],
    assignee: "",
    deadline: "2025-03-25",
  },
];

// Sample team members
const sampleTeamMembers = [
  {
    id: "team-1",
    name: "Alice Chen",
    currentTask: null,
    completedTasks: 5,
  },
  {
    id: "team-2",
    name: "Bob Smith",
    currentTask: null,
    completedTasks: 3,
  },
  {
    id: "team-3",
    name: "Carol White",
    currentTask: null,
    completedTasks: 7,
  },
];

// WebSocket server
const wss = new WebSocketServer({ port: 8080 });

console.log("🚀 Mock WebSocket Server running on ws://localhost:8080");
console.log("📝 Available endpoints:");
console.log("   - Connect: ws://localhost:8080");
console.log(
  "   - Messages supported: register_capabilities, tasks_assigned, task_updated, progress_update\n",
);

wss.on("connection", (ws, req) => {
  const clientId = `client-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  console.log(`✅ New client connected: ${clientId}`);

  clients.set(ws, clientId);

  // Send initial team update
  setTimeout(() => {
    sendToClient(ws, {
      type: "team_update",
      data: sampleTeamMembers,
    });
  }, 1000);

  ws.on("message", (data) => {
    try {
      const message = JSON.parse(data.toString());
      console.log(`📨 Received message from ${clientId}:`, message.type);

      handleClientMessage(ws, clientId, message);
    } catch (error) {
      console.error(
        `❌ Error parsing message from ${clientId}:`,
        error.message,
      );
      sendToClient(ws, {
        type: "error",
        data: { message: "Invalid message format" },
      });
    }
  });

  ws.on("close", () => {
    console.log(`🔌 Client disconnected: ${clientId}`);
    const userCapabilities = registeredUsers.get(clientId);
    if (userCapabilities) {
      console.log(
        `👤 Unregistered user: ${userCapabilities.username || "Unknown"}`,
      );
      registeredUsers.delete(clientId);
    }
    clients.delete(ws);
  });

  ws.on("error", (error) => {
    console.error(`❌ WebSocket error for ${clientId}:`, error.message);
  });

  // Send welcome message
  sendToClient(ws, {
    type: "welcome",
    data: {
      message: "Connected to Mock Server",
      clientId: clientId,
      supportedMessages: [
        "register_capabilities",
        "tasks_assigned",
        "task_updated",
        "team_update",
        "progress_update",
      ],
    },
  });

  // Send sample tasks immediately on connection
  sendSampleTasksOnConnection(ws, clientId);
});

function sendSampleTasksOnConnection(ws, clientId) {
  // Send all sample tasks to the new client
  const tasksWithAssignee = sampleTasks.map((task) => ({
    ...task,
    assignee: "",
  }));

  console.log(
    `📋 Sending ${tasksWithAssignee.length} sample tasks to ${clientId}`,
  );

  setTimeout(() => {
    sendToClient(ws, {
      type: "tasks_assigned",
      data: tasksWithAssignee,
    });
  }, 500);
}

function handleClientMessage(ws, clientId, message) {
  switch (message.type) {
    case "register_capabilities":
      handleRegisterCapabilities(ws, clientId, message.data);
      break;

    case "progress_update":
      handleProgressUpdate(ws, clientId, message.data);
      break;

    default:
      console.log(`⚠️  Unknown message type: ${message.type}`);
      sendToClient(ws, {
        type: "error",
        data: { message: `Unknown message type: ${message.type}` },
      });
  }
}

function handleRegisterCapabilities(ws, clientId, capabilities) {
  console.log(
    `User registered with capabilities:`,
    JSON.stringify(capabilities, null, 2),
  );

  // Store user capabilities
  registeredUsers.set(clientId, {
    ...capabilities,
    registeredAt: new Date().toISOString(),
  });

  // Assign 2 tasks based on capabilities (simulate intelligent task assignment)
  const assignedTasks = assignTasksToUser(clientId, capabilities);

  console.log(
    `Assigning ${assignedTasks.length} tasks to user: ${capabilities.username || "Unknown"}`,
  );

  // Send assigned tasks
  setTimeout(() => {
    sendToClient(ws, {
      type: "tasks_assigned",
      data: assignedTasks,
    });

    // Update team members to include this user
    const userName = capabilities.username || "Unknown User";
    const updatedTeam = [
      ...sampleTeamMembers,
      {
        id: clientId,
        name: userName,
        currentTask: assignedTasks[0]?.id || null,
        completedTasks: 0,
      },
    ];

    setTimeout(() => {
      sendToClient(ws, {
        type: "team_update",
        data: updatedTeam,
      });
    }, 500);
  }, 1000);
}

function assignTasksToUser(clientId, capabilities) {
  // Simple task assignment logic based on skills - assign max 2 tasks
  const assignedTasks = [];
  const userName = capabilities.username || "Unknown User";

  for (const task of sampleTasks) {
    if (assignedTasks.length >= 2) break; // Max 2 tasks per user

    const taskLower =
      task.title.toLowerCase() + " " + task.description.toLowerCase();
    const hasRelevantSkill =
      capabilities.languages?.some((lang) =>
        taskLower.includes(lang.toLowerCase()),
      ) ||
      capabilities.frameworks?.some((fw) =>
        taskLower.includes(fw.toLowerCase()),
      ) ||
      task.priority === "high" || // Always assign high priority tasks
      task.dependencies.length === 0; // Assign tasks with no dependencies first

    if (hasRelevantSkill && !task.assignee) {
      const taskCopy = { ...task };
      taskCopy.assignee = userName;
      assignedTasks.push(taskCopy);
    }
  }

  // If no tasks assigned, assign first pending task
  if (assignedTasks.length === 0) {
    const firstTask = sampleTasks.find(
      (t) => !t.assignee && t.dependencies.length === 0,
    );
    if (firstTask) {
      const taskCopy = { ...firstTask };
      taskCopy.assignee = userName;
      assignedTasks.push(taskCopy);
    }
  }

  return assignedTasks;
}

function handleProgressUpdate(ws, clientId, progressData) {
  console.log(
    `Progress update for task ${progressData.taskId}:`,
    progressData.status,
  );

  // Simulate task status update
  const updatedTask = {
    id: progressData.taskId,
    status: progressData.status,
    timestamp: progressData.timestamp || new Date().toISOString(),
  };

  // Send task updated confirmation
  sendToClient(ws, {
    type: "task_updated",
    data: updatedTask,
  });

  // Simulate team member update (increment completed tasks if completed)
  if (progressData.status === "completed") {
    const userCapabilities = registeredUsers.get(clientId);
    if (userCapabilities) {
      userCapabilities.completedTasks =
        (userCapabilities.completedTasks || 0) + 1;

      // Send updated team overview
      setTimeout(() => {
        sendToClient(ws, {
          type: "team_update",
          data: [
            ...sampleTeamMembers,
            {
              id: clientId,
              name: "You (Test User)",
              currentTask: null,
              completedTasks: userCapabilities.completedTasks,
            },
          ],
        });
      }, 500);
    }
  }

  // Simulate assigning a new task when one is completed
  if (progressData.status === "completed") {
    const unassignedTask = sampleTasks.find((t) => !t.assignee);
    if (unassignedTask) {
      setTimeout(() => {
        const newTask = { ...unassignedTask, assignee: "You" };
        unassignedTask.assignee = "You";

        console.log(`Assigned new task: ${newTask.title}`);
        sendToClient(ws, {
          type: "task_updated",
          data: newTask,
        });
      }, 2000);
    }
  }
}

function sendToClient(ws, message) {
  if (ws.readyState === WebSocket.OPEN) {
    try {
      ws.send(JSON.stringify(message));
    } catch (error) {
      console.error("Error sending message to client:", error.message);
    }
  }
}

// Graceful shutdown
process.on("SIGINT", () => {
  console.log("\nShutting down mock server...");
  wss.clients.forEach((ws) => ws.close());
  wss.close(() => {
    console.log("Server closed");
    process.exit(0);
  });
});
