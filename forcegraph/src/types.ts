export interface Challenge {
  id: string;
  type: 'navigation' | 'modification';
  title: string;
  description: string;
  difficulty: 'easy' | 'medium' | 'hard';
  target: {
    filePath: string;
    lineNumber?: number;
    pattern?: string;
    functionName?: string;
    className?: string;
  };
  expectedAction: string;
  hints: string[];
  points: number;
  completed: boolean;
  completedAt?: Date;
}

export interface GameState {
  points: number;
  streak: number;
  level: number;
  levelProgress: number;
  challengesCompleted: number;
  challengesSkipped: number;
  hintsUsed: number;
  sessionStartTime: Date;
}

export interface ChallengeState {
  currentChallenge: Challenge | null;
  challengeHistory: Challenge[];
  currentHintsUsed: number;
  awaitingVerification: boolean;
}

export interface CodeContext {
  files: FileContext[];
  projectStructure: string;
  language: string;
  frameworks: string[];
}

export interface FileContext {
  path: string;
  language: string;
  exports: string[];
  imports: string[];
  functions: FunctionInfo[];
  classes: ClassInfo[];
  lineCount: number;
}

export interface FunctionInfo {
  name: string;
  line: number;
  parameters: string[];
  returnType?: string;
}

export interface ClassInfo {
  name: string;
  line: number;
  methods: string[];
  properties: string[];
}

export interface OpenAIResponse {
  challenge: {
    type: 'navigation' | 'modification';
    title: string;
    description: string;
    target: {
      filePath: string;
      lineNumber?: number;
      pattern?: string;
      functionName?: string;
      className?: string;
    };
    expectedAction: string;
    hints: string[];
    difficulty: 'easy' | 'medium' | 'hard';
  };
}

export interface VerificationResult {
  success: boolean;
  message: string;
  details?: string;
}
