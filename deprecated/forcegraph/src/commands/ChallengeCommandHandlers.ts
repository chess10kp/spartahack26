import * as vscode from 'vscode';
import { ChallengeGenerator } from '../ai/ChallengeGenerator';
import { NavigationVerifier } from '../verification/NavigationVerifier';
import { ModificationVerifier } from '../verification/ModificationVerifier';
import { GameStateManager } from '../state/GameState';
import { ChallengeStateManager } from '../state/ChallengeState';
import { ChallengeWebviewProvider } from '../ui/ChallengeWebviewProvider';

export class ChallengeCommandHandlers {
  private challengeGenerator: ChallengeGenerator;
  private navigationVerifier: NavigationVerifier;
  private modificationVerifier: ModificationVerifier;
  private gameState: GameStateManager;
  private challengeState: ChallengeStateManager;
  private webviewProvider: ChallengeWebviewProvider;

  constructor(
    gameState: GameStateManager,
    challengeState: ChallengeStateManager,
    webviewProvider: ChallengeWebviewProvider
  ) {
    this.challengeGenerator = new ChallengeGenerator();
    this.navigationVerifier = new NavigationVerifier();
    this.modificationVerifier = new ModificationVerifier();
    this.gameState = gameState;
    this.challengeState = challengeState;
    this.webviewProvider = webviewProvider;
  }

  async startChallenge(): Promise<void> {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    if (!workspaceFolders || workspaceFolders.length === 0) {
      vscode.window.showErrorMessage('No workspace folder open');
      return;
    }

    const gameState = this.gameState.getState();
    const level = gameState.level;

    try {
      this.webviewProvider.showMessage('Generating challenge...', 'info');
      const challenge = await this.challengeGenerator.generateChallenge(workspaceFolders, level);
      this.challengeState.setCurrentChallenge(challenge);

      this.startVerification(challenge);

      this.webviewProvider.showMessage(`Challenge started! ${challenge.title}`, 'info');

      if (challenge.type === 'navigation') {
        await this.navigateToTarget(challenge);
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : 'Failed to generate challenge';
      vscode.window.showErrorMessage(message);
    }
  }

  private async navigateToTarget(challenge: any): Promise<void> {
    try {
      const uri = vscode.Uri.file(challenge.target.filePath);
      const document = await vscode.workspace.openTextDocument(uri);
      const line = challenge.target.lineNumber || 1;
      const range = new vscode.Range(line - 1, 0, line - 1, 0);

      await vscode.window.showTextDocument(document, { selection: range });
    } catch (error) {
      console.error('Failed to navigate to target:', error);
    }
  }

  private startVerification(challenge: any): void {
    if (challenge.type === 'navigation') {
      this.navigationVerifier.startVerification(challenge, (result) => {
        this.handleVerificationResult(result);
      });
    } else if (challenge.type === 'modification') {
      this.modificationVerifier.startVerification(challenge, (result) => {
        this.handleVerificationResult(result);
      });
    }
  }

  submitAnswer(): void {
    const currentChallenge = this.challengeState.getCurrentChallenge();
    if (!currentChallenge) {
      return;
    }

    this.handleVerificationResult({
      success: true,
      message: 'Challenge submitted successfully!',
      details: currentChallenge.expectedAction
    });
  }

  showHint(): void {
    const currentChallenge = this.challengeState.getCurrentChallenge();
    if (!currentChallenge) {
      return;
    }

    const hint = this.challengeState.useHint();
    if (hint) {
      this.gameState.useHint();
      this.webviewProvider.showMessage('Hint used! -10 points', 'info');
    } else {
      this.webviewProvider.showMessage('No more hints available', 'error');
    }
  }

  skipChallenge(): void {
    const currentChallenge = this.challengeState.getCurrentChallenge();
    if (!currentChallenge) {
      return;
    }

    this.navigationVerifier.cancelVerification();
    this.modificationVerifier.cancelVerification();

    this.challengeState.skipCurrentChallenge();
    this.gameState.skipChallenge();

    this.webviewProvider.showMessage('Challenge skipped (-25 points)', 'info');

    setTimeout(() => {
      this.startChallenge();
    }, 1000);
  }

  private handleVerificationResult(result: any): void {
    if (result.success) {
      const currentChallenge = this.challengeState.getCurrentChallenge();
      if (currentChallenge) {
        const usedHint = this.challengeState.getState().currentHintsUsed > 0;
        this.challengeState.completeCurrentChallenge();
        this.gameState.completeChallenge(currentChallenge, usedHint);

        this.navigationVerifier.cancelVerification();
        this.modificationVerifier.cancelVerification();

        this.webviewProvider.celebrate();
        this.webviewProvider.showMessage(result.message, 'success');

        setTimeout(() => {
          this.startChallenge();
        }, 2000);
      }
    } else {
      this.challengeState.completeCurrentChallenge();
      this.gameState.failChallenge();

      this.navigationVerifier.cancelVerification();
      this.modificationVerifier.cancelVerification();

      this.webviewProvider.showMessage(result.message, 'error');

      setTimeout(() => {
        this.startChallenge();
      }, 2000);
    }
  }
}
