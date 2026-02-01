import * as vscode from 'vscode';
import { Challenge, VerificationResult } from '../types';

export class NavigationVerifier {
  private activeVerification: { challenge: Challenge; callback: (result: VerificationResult) => void } | null = null;

  startVerification(challenge: Challenge, callback: (result: VerificationResult) => void): void {
    this.activeVerification = { challenge, callback };

    const disposable = vscode.window.onDidChangeActiveTextEditor(editor => this.onEditorChange(editor));
    const cursorDisposable = vscode.window.onDidChangeTextEditorSelection(event => this.onSelectionChange(event));

    setTimeout(() => {
      disposable.dispose();
      cursorDisposable.dispose();
      if (this.activeVerification?.challenge.id === challenge.id) {
        callback({
          success: false,
          message: 'Time limit exceeded',
          details: 'Please try again or skip to the next challenge'
        });
        this.activeVerification = null;
      }
    }, 30000);
  }

  private onEditorChange(editor: vscode.TextEditor | undefined): void {
    if (!editor || !this.activeVerification) {return;}

    const { challenge, callback } = this.activeVerification;
    const documentUri = editor.document.uri.toString();

    if (documentUri.includes(challenge.target.filePath)) {
      this.checkPosition(editor, challenge, callback);
    }
  }

  private onSelectionChange(event: vscode.TextEditorSelectionChangeEvent): void {
    if (!this.activeVerification) {return;}

    const { challenge, callback } = this.activeVerification;
    const documentUri = event.textEditor.document.uri.toString();

    if (documentUri.includes(challenge.target.filePath)) {
      this.checkPosition(event.textEditor, challenge, callback);
    }
  }

  private checkPosition(editor: vscode.TextEditor, challenge: Challenge, callback: (result: VerificationResult) => void): void {
    const selection = editor.selection;
    const currentLine = selection.active.line + 1;

    if (challenge.target.lineNumber) {
      const targetLine = challenge.target.lineNumber;
      const tolerance = 3;

      if (Math.abs(currentLine - targetLine) <= tolerance) {
        callback({
          success: true,
          message: 'You found it!',
          details: challenge.expectedAction
        });
        this.activeVerification = null;
      }
    }

    if (challenge.target.pattern) {
      const lineContent = editor.document.lineAt(currentLine - 1).text;
      if (new RegExp(challenge.target.pattern).test(lineContent)) {
        callback({
          success: true,
          message: 'Pattern matched!',
          details: challenge.expectedAction
        });
        this.activeVerification = null;
      }
    }

    if (challenge.target.functionName) {
      const lineContent = editor.document.lineAt(currentLine - 1).text;
      if (lineContent.includes(challenge.target.functionName)) {
        callback({
          success: true,
          message: 'Function found!',
          details: challenge.expectedAction
        });
        this.activeVerification = null;
      }
    }

    if (challenge.target.className) {
      const lineContent = editor.document.lineAt(currentLine - 1).text;
      if (lineContent.includes(challenge.target.className)) {
        callback({
          success: true,
          message: 'Class found!',
          details: challenge.expectedAction
        });
        this.activeVerification = null;
      }
    }
  }

  cancelVerification(): void {
    this.activeVerification = null;
  }
}
