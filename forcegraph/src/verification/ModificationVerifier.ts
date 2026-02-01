import * as vscode from 'vscode';
import { Challenge, VerificationResult } from '../types';
import * as diff from 'diff';

interface FileState {
  uri: string;
  content: string;
  timestamp: number;
}

export class ModificationVerifier {
  private originalFileStates: Map<string, FileState> = new Map();
  private activeVerification: { challenge: Challenge; callback: (result: VerificationResult) => void } | null = null;

  async startVerification(challenge: Challenge, callback: (result: VerificationResult) => void): Promise<void> {
    this.activeVerification = { challenge, callback };

    const targetUri = vscode.Uri.file(challenge.target.filePath);
    try {
      const document = await vscode.workspace.openTextDocument(targetUri);
      this.originalFileStates.set(targetUri.toString(), {
        uri: targetUri.toString(),
        content: document.getText(),
        timestamp: Date.now()
      });
    } catch (error) {
      callback({
        success: false,
        message: 'Could not open target file',
        details: 'Please check if the file exists'
      });
      this.activeVerification = null;
      return;
    }

    const disposable = vscode.workspace.onDidChangeTextDocument(event => this.onDocumentChange(event));

    setTimeout(() => {
      disposable.dispose();
      if (this.activeVerification?.challenge.id === challenge.id) {
        callback({
          success: false,
          message: 'Time limit exceeded',
          details: 'Please try again or skip to the next challenge'
        });
        this.activeVerification = null;
        this.originalFileStates.clear();
      }
    }, 60000);
  }

  private onDocumentChange(event: vscode.TextDocumentChangeEvent): void {
    if (!this.activeVerification) {return;}

    const { challenge, callback } = this.activeVerification;
    const uri = event.document.uri.toString();

    if (uri.includes(challenge.target.filePath)) {
      this.verifyChanges(event.document, challenge, callback);
    }
  }

  private verifyChanges(document: vscode.TextDocument, challenge: Challenge, callback: (result: VerificationResult) => void): void {
    const originalState = this.originalFileStates.get(document.uri.toString());
    if (!originalState) {return;}

    const currentContent = document.getText();
    const changes = diff.diffLines(originalState.content, currentContent);

    const hasChanges = changes.some(change => change.added || change.removed);

    if (!hasChanges) {
      return;
    }

    let success = false;
    let message = 'Changes detected!';

    if (challenge.target.pattern) {
      const pattern = new RegExp(challenge.target.pattern, 'g');
      const matches = currentContent.match(pattern);
      success = matches !== null && matches.length > 0;
      message = success ? 'Pattern found in code!' : 'Expected pattern not found';
    } else {
      const addedLines = changes.filter((change: diff.Change) => change.added).map((change: diff.Change) => change.value);
      const removedLines = changes.filter((change: diff.Change) => change.removed).map((change: diff.Change) => change.value);

      const addedText = addedLines.join('');
      const removedText = removedLines.join('');

      if (addedText.length > 0) {
        success = true;
        message = 'Code successfully modified!';
      }
    }

    if (success) {
      callback({
        success: true,
        message,
        details: challenge.expectedAction
      });
      this.activeVerification = null;
    }
  }

  cancelVerification(): void {
    this.activeVerification = null;
    this.originalFileStates.clear();
  }

  async getDiff(challenge: Challenge): Promise<string | null> {
    const targetUri = vscode.Uri.file(challenge.target.filePath);
    const originalState = this.originalFileStates.get(targetUri.toString());

    if (!originalState) {return null;}

    try {
      const document = await vscode.workspace.openTextDocument(targetUri);
      const currentContent = document.getText();
      const changes = diff.diffLines(originalState.content, currentContent);

      return changes.map((change: diff.Change) => {
        if (change.added) {return `+${change.value}`;}
        if (change.removed) {return `-${change.value}`;}
        return change.value;
      }).join('');
    } catch (error) {
      return null;
    }
  }
}
