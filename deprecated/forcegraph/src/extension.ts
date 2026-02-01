import * as vscode from 'vscode';
import { GameStateManager } from './state/GameState';
import { ChallengeStateManager } from './state/ChallengeState';
import { ChallengeWebviewProvider } from './ui/ChallengeWebviewProvider';
import { ChallengeCommandHandlers } from './commands/ChallengeCommandHandlers';

let gameStateManager: GameStateManager;
let challengeStateManager: ChallengeStateManager;
let webviewProvider: ChallengeWebviewProvider;
let commandHandlers: ChallengeCommandHandlers;

export function activate(context: vscode.ExtensionContext) {
  console.log('Code Quest extension activated!');
  vscode.window.showInformationMessage('🎯 Code Quest: Ready for challenges!');

  gameStateManager = new GameStateManager();
  challengeStateManager = new ChallengeStateManager();
  webviewProvider = new ChallengeWebviewProvider(context.extensionUri, gameStateManager, challengeStateManager);
  commandHandlers = new ChallengeCommandHandlers(gameStateManager, challengeStateManager, webviewProvider);

  context.subscriptions.push(
    vscode.window.registerWebviewViewProvider('forcegraph-sidebar', webviewProvider)
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forcegraph.startChallenge', () => commandHandlers.startChallenge())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forcegraph.submitAnswer', () => commandHandlers.submitAnswer())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forcegraph.showHint', () => commandHandlers.showHint())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forcegraph.skipChallenge', () => commandHandlers.skipChallenge())
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('forcegraph.resetGame', () => {
      gameStateManager.reset();
      challengeStateManager.reset();
      vscode.window.showInformationMessage('Game reset!');
    })
  );

  if (!process.env.OPENAI_API_KEY) {
    vscode.window.showWarningMessage(
      'Code Quest: OPENAI_API_KEY not set. Please set the environment variable and reload VS Code.',
      'Open Settings'
    ).then(selection => {
      if (selection === 'Open Settings') {
        vscode.commands.executeCommand('workbench.action.openSettings', 'forcegraph');
      }
    });
  }
}

export function deactivate() {
  console.log('Code Quest extension deactivated');
}
