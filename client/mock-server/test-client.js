#!/usr/bin/env node
import WebSocket from "ws";

// ANSI color codes for better output
const colors = {
  reset: "\x1b[0m",
  green: "\x1b[32m",
  blue: "\x1b[34m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  cyan: "\x1b[36m",
  magenta: "\x1b[35m",
};

function log(message, color = colors.reset) {
  console.log(`${color}${message}${colors.reset}`);
}

function logSent(message) {
  console.log(`\n${colors.cyan}📤 SENT:${colors.reset}`);
  console.log(JSON.stringify(message, null, 2));
}

function logReceived(message) {
  console.log(`\n${colors.green}📥 RECEIVED:${colors.reset}`);
  console.log(JSON.stringify(message, null, 2));
}

// Test scenarios
const scenarios = {
  1: "Register capabilities with JavaScript/React skills",
  2: "Register capabilities with Python/Django skills",
  3: "Register capabilities with full-stack skills",
  4: "Register capabilities with no skills (default)",
  5: "Update first task to in_progress",
  6: "Update first task to completed",
  7: "Custom message input",
  8: "Run automated test suite",
};

// Sample capabilities for different scenarios
const capabilitySets = {
  js: {
    languages: ["JavaScript", "TypeScript"],
    frameworks: ["React", "Node.js", "Express"],
  },
  python: {
    languages: ["Python", "SQL"],
    frameworks: ["Django", "Flask", "FastAPI"],
  },
  fullstack: {
    languages: ["JavaScript", "Python", "Go"],
    frameworks: [
      "React",
      "Node.js",
      "Django",
      "PostgreSQL",
      "Docker",
      "Kubernetes",
    ],
  },
  minimal: {
    languages: [],
    frameworks: [],
  },
};

class TestClient {
  constructor(url) {
    this.url = url;
    this.ws = null;
    this.connected = false;
    this.currentTasks = [];
    this.messageCount = 0;
  }

  connect() {
    log(`🔌 Connecting to ${this.url}...`, colors.yellow);

    this.ws = new WebSocket(this.url);

    this.ws.on("open", () => {
      this.connected = true;
      log("\n✅ Connected successfully!\n", colors.green);
      this.showMenu();
    });

    this.ws.on("message", (data) => {
      this.messageCount++;
      try {
        const message = JSON.parse(data.toString());
        this.handleMessage(message);
      } catch (error) {
        log(`❌ Failed to parse message: ${error.message}`, colors.red);
      }
    });

    this.ws.on("error", (error) => {
      log(`\n❌ WebSocket error: ${error.message}`, colors.red);
      this.connected = false;
    });

    this.ws.on("close", () => {
      log("\n🔌 Connection closed\n", colors.yellow);
      this.connected = false;
      this.showMenu();
    });
  }

  handleMessage(message) {
    logReceived(message);

    switch (message.type) {
      case "welcome":
        log(`Client ID: ${message.data.clientId}`, colors.magenta);
        log(
          `Supported messages: ${message.data.supportedMessages.join(", ")}`,
          colors.magenta,
        );
        break;

      case "tasks_assigned":
        this.currentTasks = message.data;
        log(`\n📋 Received ${this.currentTasks.length} tasks:`, colors.blue);
        this.currentTasks.forEach((task, index) => {
          log(
            `  ${index + 1}. ${task.title} (${task.priority} priority)`,
            colors.blue,
          );
        });
        break;

      case "task_updated":
        const updatedTask = this.currentTasks.find(
          (t) => t.id === message.data.id,
        );
        if (updatedTask) {
          updatedTask.status = message.data.status;
          log(
            `\n✅ Task "${updatedTask.title}" updated to: ${message.data.status}`,
            colors.green,
          );
        }
        break;

      case "team_update":
        log(
          `\n👥 Team update - ${message.data.length} members:`,
          colors.magenta,
        );
        message.data.forEach((member) => {
          const taskInfo = member.currentTask
            ? ` - Working on: ${member.currentTask.title}`
            : "";
          log(
            `  - ${member.name} (${member.completedTasks} completed)${taskInfo}`,
            colors.magenta,
          );
        });
        break;

      case "error":
        log(`\n❌ Server error: ${message.data.message}`, colors.red);
        break;

      default:
        log(`\n⚠️  Unknown message type: ${message.type}`, colors.yellow);
    }

    log(`\nMessages exchanged: ${this.messageCount}`, colors.cyan);
    log("\nPress Enter to see menu...", colors.yellow);
  }

  send(type, data = {}) {
    if (!this.connected) {
      log("❌ Not connected to server", colors.red);
      return;
    }

    const message = { type, data };
    logSent(message);

    try {
      this.ws.send(JSON.stringify(message));
    } catch (error) {
      log(`❌ Failed to send message: ${error.message}`, colors.red);
    }
  }

  showMenu() {
    console.log("\n" + "=".repeat(60));
    log("📝 Mock Server Test Client", colors.green);
    log("=".repeat(60), colors.green);
    log("\nSelect a scenario:\n", colors.yellow);

    Object.entries(scenarios).forEach(([num, description]) => {
      log(`  ${num}. ${description}`, colors.cyan);
    });

    log("\n  0.  Exit", colors.red);
    log("\n" + "=".repeat(60) + "\n", colors.green);
  }

  async runScenario(scenarioNum) {
    if (!this.connected) {
      log("❌ Not connected to server", colors.red);
      return;
    }

    switch (parseInt(scenarioNum)) {
      case 1:
        log(
          "\n🎯 Running: Register with JavaScript/React skills",
          colors.yellow,
        );
        this.send("register_capabilities", capabilitySets.js);
        break;

      case 2:
        log("\n🎯 Running: Register with Python/Django skills", colors.yellow);
        this.send("register_capabilities", capabilitySets.python);
        break;

      case 3:
        log("\n🎯 Running: Register with full-stack skills", colors.yellow);
        this.send("register_capabilities", capabilitySets.fullstack);
        break;

      case 4:
        log("\n🎯 Running: Register with minimal skills", colors.yellow);
        this.send("register_capabilities", capabilitySets.minimal);
        break;

      case 5:
        if (this.currentTasks.length === 0) {
          log(
            "❌ No tasks assigned yet. Register capabilities first.",
            colors.red,
          );
          return;
        }
        log("\n🎯 Running: Update first task to in_progress", colors.yellow);
        this.send("progress_update", {
          taskId: this.currentTasks[0].id,
          status: "in_progress",
          timestamp: new Date().toISOString(),
        });
        break;

      case 6:
        if (this.currentTasks.length === 0) {
          log(
            "❌ No tasks assigned yet. Register capabilities first.",
            colors.red,
          );
          return;
        }
        log("\n🎯 Running: Update first task to completed", colors.yellow);
        this.send("progress_update", {
          taskId: this.currentTasks[0].id,
          status: "completed",
          timestamp: new Date().toISOString(),
        });
        break;

      case 7:
        await this.customMessage();
        break;

      case 8:
        await this.runAutomatedTests();
        break;

      case 0:
        log("\n👋 Goodbye!", colors.green);
        this.disconnect();
        process.exit(0);

      default:
        log("❌ Invalid scenario number", colors.red);
    }
  }

  async customMessage() {
    const readline = await import("readline");
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    const type = await new Promise((resolve) => {
      rl.question("Enter message type: ", resolve);
    });

    const dataStr = await new Promise((resolve) => {
      rl.question(
        "Enter data (JSON format, or press Enter for empty): ",
        resolve,
      );
    });

    rl.close();

    let data = {};
    if (dataStr.trim()) {
      try {
        data = JSON.parse(dataStr);
      } catch (error) {
        log("❌ Invalid JSON, sending empty data", colors.red);
      }
    }

    this.send(type, data);
  }

  async runAutomatedTests() {
    log("\n🧪 Starting automated test suite...", colors.yellow);
    log("This will test various scenarios automatically.\n", colors.cyan);

    const tests = [
      {
        name: "Test 1: Register with JS skills",
        delay: 2000,
        action: () => this.send("register_capabilities", capabilitySets.js),
      },
      {
        name: "Test 2: Wait for task assignment",
        delay: 3000,
        action: () => {},
      },
      {
        name: "Test 3: Update task to in_progress",
        delay: 2000,
        action: () => {
          if (this.currentTasks.length > 0) {
            this.send("progress_update", {
              taskId: this.currentTasks[0].id,
              status: "in_progress",
              timestamp: new Date().toISOString(),
            });
          }
        },
      },
      {
        name: "Test 4: Update task to completed",
        delay: 2000,
        action: () => {
          if (this.currentTasks.length > 0) {
            this.send("progress_update", {
              taskId: this.currentTasks[0].id,
              status: "completed",
              timestamp: new Date().toISOString(),
            });
          }
        },
      },
      {
        name: "Test 5: Wait for new task assignment",
        delay: 3000,
        action: () => {},
      },
      {
        name: "Test 6: Register with Python skills",
        delay: 2000,
        action: () => this.send("register_capabilities", capabilitySets.python),
      },
    ];

    for (const test of tests) {
      log(`\n${test.name}...`, colors.magenta);
      test.action();
      await new Promise((resolve) => setTimeout(resolve, test.delay));
    }

    log("\n✅ Automated test suite completed!", colors.green);
    log(`Total messages exchanged: ${this.messageCount}`, colors.cyan);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.connected = false;
    }
  }
}

// Main execution
async function main() {
  const args = process.argv.slice(2);
  const url = args[0] || "ws://localhost:8080";
  const autoTest = args.includes("--auto-test");

  const client = new TestClient(url);
  client.connect();

  // Wait a bit for connection
  await new Promise((resolve) => setTimeout(resolve, 1000));

  if (autoTest) {
    await client.runAutomatedTests();
    setTimeout(() => {
      client.disconnect();
      process.exit(0);
    }, 3000);
  } else {
    // Interactive mode
    const readline = await import("readline");
    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    const waitForInput = () => {
      rl.question("\nEnter scenario number (or 0 to exit): ", async (input) => {
        await client.runScenario(input.trim());
        if (client.connected) {
          waitForInput();
        } else {
          rl.close();
        }
      });
    };

    waitForInput();
  }
}

// Handle Ctrl+C
process.on("SIGINT", () => {
  log("\n\n👋 Shutting down gracefully...", colors.yellow);
  process.exit(0);
});

main().catch((error) => {
  log(`\n❌ Fatal error: ${error.message}`, colors.red);
  process.exit(1);
});
