import * as vscode from 'vscode';
import { OpenAIClient } from './OpenAIClient';
import { ContextExtractor } from './ContextExtractor';
import { Challenge, CodeContext } from '../types';

export class ChallengeGenerator {
  private openaiClient: OpenAIClient;
  private contextExtractor: ContextExtractor;

  constructor() {
    this.openaiClient = new OpenAIClient();
    this.contextExtractor = new ContextExtractor();
  }

  async generateChallenge(workspaceFolders: readonly vscode.WorkspaceFolder[], level: number): Promise<Challenge> {
    const context = await this.contextExtractor.extractContext(workspaceFolders);
    const prompt = this.buildPrompt(context, level);

    const response = await this.openaiClient.generateCompletion(prompt);
    const parsed = JSON.parse(response);

    return {
      id: this.generateId(),
      type: parsed.challenge.type,
      title: parsed.challenge.title,
      description: parsed.challenge.description,
      difficulty: parsed.challenge.difficulty,
      target: parsed.challenge.target,
      expectedAction: parsed.challenge.expectedAction,
      hints: parsed.challenge.hints,
      points: this.calculatePoints(parsed.challenge.difficulty),
      completed: false
    };
  }

  private buildPrompt(context: CodeContext, level: number): string {
    const filesSummary = context.files.map(f => ({
      path: f.path,
      language: f.language,
      functions: f.functions.map(fn => fn.name),
      classes: f.classes.map(cls => cls.name),
      exports: f.exports
    }));

    return `You are generating a ${level > 3 ? 'hard' : level > 1 ? 'medium' : 'easy'} difficulty coding challenge.

Context about the codebase:
- Primary language: ${context.language}
- Frameworks: ${context.frameworks.join(', ') || 'None detected'}
- Files: ${JSON.stringify(filesSummary, null, 2)}

Generate a challenging but solvable task. It should be either:
1. A navigation challenge: Ask the user to find a specific function, class, or code pattern
2. A modification challenge: Ask the user to make a small, well-defined change to the code

Return a JSON response with this exact structure:
{
  "challenge": {
    "type": "navigation" | "modification",
    "title": "Short, engaging title (max 10 words)",
    "description": "Clear, detailed instructions for the user (2-3 sentences)",
    "target": {
      "filePath": "path/to/file.ts (must be one of the files listed above)",
      "lineNumber": number (for navigation) | undefined (for modification),
      "pattern": "regex pattern to match (optional, for verification)",
      "functionName": "name (optional)",
      "className": "name (optional)"
    },
    "expectedAction": "What the user needs to do (e.g., 'Find the function', 'Add error handling')",
    "hints": [
      "First hint (specific but not giving it away)",
      "Second hint (more detailed, closer to answer)"
    ],
    "difficulty": "easy" | "medium" | "hard"
  }
}

Requirements:
- Target MUST be a real file from the context
- For navigation: specify lineNumber and optionally functionName/className
- For modification: specify filePath and what change to make
- Provide exactly 2 hints
- Make it challenging but achievable
- Ensure the target file exists in the provided files list`;
  }

  private generateId(): string {
    return `challenge_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  private calculatePoints(difficulty: string): number {
    switch (difficulty) {
      case 'easy':
        return 50;
      case 'medium':
        return 100;
      case 'hard':
        return 150;
      default:
        return 100;
    }
  }
}
