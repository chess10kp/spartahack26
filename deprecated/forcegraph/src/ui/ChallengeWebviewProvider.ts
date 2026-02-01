import * as vscode from 'vscode';
import { GameState, Challenge } from '../types';
import { GameStateManager } from '../state/GameState';
import { ChallengeStateManager } from '../state/ChallengeState';

export class ChallengeWebviewProvider implements vscode.WebviewViewProvider {
  private webviewView: vscode.WebviewView | undefined;
  private gameState: GameStateManager;
  private challengeState: ChallengeStateManager;

  constructor(
    private readonly extensionUri: vscode.Uri,
    gameState: GameStateManager,
    challengeState: ChallengeStateManager
  ) {
    this.gameState = gameState;
    this.challengeState = challengeState;

    this.gameState.onStateChanged(state => this.updateUI());
    this.challengeState.onStateChanged(state => this.updateUI());
  }

  resolveWebviewView(webviewView: vscode.WebviewView): void | Thenable<void> {
    this.webviewView = webviewView;
    webviewView.webview.options = { enableScripts: true };
    webviewView.webview.html = this.getHtml();

    webviewView.webview.onDidReceiveMessage(message => {
      this.handleMessage(message);
    });
  }

  private handleMessage(message: any): void {
    switch (message.command) {
      case 'startChallenge':
        vscode.commands.executeCommand('forcegraph.startChallenge');
        break;
      case 'submitAnswer':
        vscode.commands.executeCommand('forcegraph.submitAnswer');
        break;
      case 'showHint':
        vscode.commands.executeCommand('forcegraph.showHint');
        break;
      case 'skipChallenge':
        vscode.commands.executeCommand('forcegraph.skipChallenge');
        break;
    }
  }

  private updateUI(): void {
    if (this.webviewView) {
      const gameState = this.gameState.getState();
      const challengeState = this.challengeState.getState();
      this.webviewView.webview.html = this.getHtml();
    }
  }

  showMessage(message: string, type: 'success' | 'error' | 'info'): void {
    if (this.webviewView) {
      this.webviewView.webview.postMessage({ command: 'showMessage', message, type });
    }
  }

  celebrate(): void {
    if (this.webviewView) {
      this.webviewView.webview.postMessage({ command: 'celebrate' });
    }
  }

  private getHtml(): string {
    const gameState = this.gameState.getState();
    const challengeState = this.challengeState.getState();

    return `<!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
          * { box-sizing: border-box; margin: 0; padding: 0; }
          body {
            font-family: var(--vscode-font-family);
            background-color: var(--vscode-sideBar-background);
            color: var(--vscode-sideBar-foreground);
            padding: 15px;
            font-size: var(--vscode-font-size);
          }

          .header {
            text-align: center;
            margin-bottom: 20px;
          }

          .stats {
            display: flex;
            justify-content: space-between;
            background: var(--vscode-editor-background);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          }

          .stat {
            text-align: center;
            flex: 1;
          }

          .stat-value {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
          }

          .stat-label {
            font-size: 11px;
            color: var(--vscode-descriptionForeground);
            text-transform: uppercase;
            margin-top: 4px;
          }

          .streak {
            color: #ff6b6b !important;
          }

          .progress-bar {
            background: var(--vscode-progressBar-background);
            height: 4px;
            border-radius: 2px;
            margin: 5px 0;
            overflow: hidden;
          }

          .progress-fill {
            background: var(--vscode-progressBar-foreground);
            height: 100%;
            transition: width 0.3s ease;
          }

          .challenge-card {
            background: var(--vscode-editor-background);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          }

          .challenge-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
          }

          .challenge-type {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
            text-transform: uppercase;
          }

          .type-navigation {
            background: #4ec9b0;
            color: #000;
          }

          .type-modification {
            background: #ce9178;
            color: #000;
          }

          .difficulty {
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
          }

          .difficulty-easy { background: #89d185; color: #000; }
          .difficulty-medium { background: #dcdcaa; color: #000; }
          .difficulty-hard { background: #f14c4c; color: #000; }

          .challenge-title {
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
            color: var(--vscode-foreground);
          }

          .challenge-description {
            font-size: 13px;
            color: var(--vscode-descriptionForeground);
            line-height: 1.5;
            margin-bottom: 12px;
          }

          .hint-box {
            background: var(--vscode-textBlockQuote-background);
            border-left: 3px solid var(--vscode-textLink-foreground);
            padding: 10px;
            margin: 10px 0;
            font-size: 12px;
            font-style: italic;
          }

          .buttons {
            display: flex;
            gap: 8px;
            margin-top: 10px;
          }

          button {
            flex: 1;
            padding: 10px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
          }

          .btn-primary {
            background: var(--vscode-button-foreground);
            color: var(--vscode-button-background);
          }

          .btn-secondary {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
          }

          .btn-hint {
            background: var(--vscode-textBlockQuote-background);
            color: var(--vscode-foreground);
            flex: 0.5;
          }

          button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
          }

          button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
          }

          .no-challenge {
            text-align: center;
            padding: 30px;
            color: var(--vscode-descriptionForeground);
          }

          .start-button {
            width: 100%;
            padding: 15px;
            margin-top: 10px;
          }

          .confetti {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
          }

          .confetti-piece {
            position: absolute;
            width: 10px;
            height: 10px;
            animation: confetti-fall 3s linear forwards;
          }

          @keyframes confetti-fall {
            0% {
              transform: translateY(0) rotate(0deg);
              opacity: 1;
            }
            100% {
              transform: translateY(100vh) rotate(720deg);
              opacity: 0;
            }
          }

          .message {
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
            animation: slideIn 0.3s ease;
          }

          .message.success {
            background: #89d185;
            color: #000;
          }

          .message.error {
            background: #f14c4c;
            color: #000;
          }

          .message.info {
            background: #4ec9b0;
            color: #000;
          }

          @keyframes slideIn {
            from { transform: translateX(-100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
          }

          .level-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
          }
        </style>
      </head>
      <body>
        <div id="confetti" class="confetti"></div>

        <div class="header">
          <h2 style="color: var(--vscode-foreground); font-size: 18px;">🎯 Code Quest</h2>
        </div>

        <div class="stats">
          <div class="stat">
            <div class="stat-value">${gameState.points}</div>
            <div class="stat-label">Points</div>
          </div>
          <div class="stat">
            <div class="stat-value streak">🔥 ${gameState.streak}</div>
            <div class="stat-label">Streak</div>
          </div>
          <div class="stat">
            <div class="level-badge">Lvl ${gameState.level}</div>
            <div class="progress-bar">
              <div class="progress-fill" style="width: ${gameState.levelProgress}%"></div>
            </div>
            <div class="stat-label">Level ${gameState.level}</div>
          </div>
        </div>

        <div id="messages"></div>

        ${this.renderChallenge(challengeState.currentChallenge, 2 - challengeState.currentHintsUsed)}

        <script>
          const vscode = acquireVsCodeApi();

          window.addEventListener('message', event => {
            const message = event.data;

            if (message.command === 'showMessage') {
              showMessage(message.message, message.type);
            } else if (message.command === 'celebrate') {
              celebrate();
            }
          });

          function showMessage(text, type) {
            const container = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = \`message \${type}\`;
            messageDiv.textContent = text;
            container.appendChild(messageDiv);

            setTimeout(() => messageDiv.remove(), 3000);
          }

          function celebrate() {
            const confetti = document.getElementById('confetti');
            const colors = ['#f14c4c', '#4ec9b0', '#dcdcaa', '#569cd6', '#ce9178'];

            for (let i = 0; i < 50; i++) {
              const piece = document.createElement('div');
              piece.className = 'confetti-piece';
              piece.style.left = Math.random() * 100 + '%';
              piece.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
              piece.style.animationDelay = Math.random() * 2 + 's';
              confetti.appendChild(piece);

              setTimeout(() => piece.remove(), 5000);
            }
          }
        </script>
      </body>
      </html>`;
  }

  private renderChallenge(challenge: Challenge | null, availableHints: number): string {
    if (!challenge) {
      return `
        <div class="no-challenge">
          <p>Ready for a challenge?</p>
          <button class="btn-primary start-button" onclick="vscode.postMessage({ command: 'startChallenge' })">
            🚀 Start Challenge
          </button>
        </div>
      `;
    }

    return `
      <div class="challenge-card">
        <div class="challenge-header">
          <span class="challenge-type type-${challenge.type}">${challenge.type}</span>
          <span class="difficulty difficulty-${challenge.difficulty}">${challenge.difficulty}</span>
        </div>
        <div class="challenge-title">${challenge.title}</div>
        <div class="challenge-description">${challenge.description}</div>
        <div id="hint-container"></div>
        <div class="buttons">
          ${availableHints > 0 ? `<button class="btn-hint" onclick="showHint()">💡 Hint (${availableHints})</button>` : ''}
          <button class="btn-primary" onclick="vscode.postMessage({ command: 'submitAnswer' })">✓ Submit</button>
          <button class="btn-secondary" onclick="vscode.postMessage({ command: 'skipChallenge' })">Skip</button>
        </div>
      </div>

      <script>
        function showHint() {
          const hints = ${JSON.stringify(challenge.hints)};
          const usedHints = 2 - ${availableHints};
          if (usedHints < hints.length) {
            const container = document.getElementById('hint-container');
            const hintBox = document.createElement('div');
            hintBox.className = 'hint-box';
            hintBox.textContent = '💡 ' + hints[usedHints];
            container.appendChild(hintBox);
            vscode.postMessage({ command: 'showHint' });
          }
        }
      </script>
    `;
  }
}
