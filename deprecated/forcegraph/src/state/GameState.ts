import { GameState, Challenge } from '../types';

const POINTS_PER_LEVEL = 500;
const POINTS_FOR_CORRECT_ANSWER = 100;
const POINTS_FOR_HINT = -10;
const POINTS_FOR_SKIP = -25;
const STREAK_MULTIPLIER_THRESHOLD = 3;

export class GameStateManager {
  private state: GameState;
  private onStateChange?: (state: GameState) => void;

  constructor() {
    this.state = this.createInitialState();
  }

  private createInitialState(): GameState {
    return {
      points: 0,
      streak: 0,
      level: 1,
      levelProgress: 0,
      challengesCompleted: 0,
      challengesSkipped: 0,
      hintsUsed: 0,
      sessionStartTime: new Date()
    };
  }

  getState(): GameState {
    return { ...this.state };
  }

  completeChallenge(challenge: Challenge, usedHint: boolean): void {
    let points = POINTS_FOR_CORRECT_ANSWER;

    if (this.state.streak >= STREAK_MULTIPLIER_THRESHOLD) {
      points *= 2;
    }

    if (usedHint) {
      points += POINTS_FOR_HINT;
    }

    this.state.points += points;
    this.state.streak++;
    this.state.challengesCompleted++;

    this.updateLevelProgress();
    this.notifyStateChange();
  }

  failChallenge(): void {
    this.state.streak = 0;
    this.notifyStateChange();
  }

  skipChallenge(): void {
    this.state.points += POINTS_FOR_SKIP;
    this.state.streak = 0;
    this.state.challengesSkipped++;
    this.notifyStateChange();
  }

  useHint(): void {
    this.state.points += POINTS_FOR_HINT;
    this.state.hintsUsed++;
    this.notifyStateChange();
  }

  private updateLevelProgress(): void {
    const pointsInCurrentLevel = this.state.points % POINTS_PER_LEVEL;
    const progressPercentage = (pointsInCurrentLevel / POINTS_PER_LEVEL) * 100;
    this.state.levelProgress = progressPercentage;

    const potentialLevel = Math.floor(this.state.points / POINTS_PER_LEVEL) + 1;
    if (potentialLevel > this.state.level) {
      this.state.level = potentialLevel;
    }
  }

  reset(): void {
    this.state = this.createInitialState();
    this.notifyStateChange();
  }

  onStateChanged(callback: (state: GameState) => void): void {
    this.onStateChange = callback;
  }

  private notifyStateChange(): void {
    if (this.onStateChange) {
      this.onStateChange(this.getState());
    }
  }
}
