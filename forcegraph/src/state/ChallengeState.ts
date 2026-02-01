import { Challenge, ChallengeState } from '../types';

const MAX_HINTS = 2;

export class ChallengeStateManager {
  private state: ChallengeState;
  private onStateChange?: (state: ChallengeState) => void;

  constructor() {
    this.state = this.createInitialState();
  }

  private createInitialState(): ChallengeState {
    return {
      currentChallenge: null,
      challengeHistory: [],
      currentHintsUsed: 0,
      awaitingVerification: false
    };
  }

  getState(): ChallengeState {
    return { ...this.state, currentChallenge: this.state.currentChallenge ? { ...this.state.currentChallenge } : null };
  }

  setCurrentChallenge(challenge: Challenge): void {
    if (this.state.currentChallenge) {
      this.state.challengeHistory.push(this.state.currentChallenge);
    }
    this.state.currentChallenge = challenge;
    this.state.currentHintsUsed = 0;
    this.state.awaitingVerification = false;
    this.notifyStateChange();
  }

  completeCurrentChallenge(): void {
    if (this.state.currentChallenge) {
      this.state.currentChallenge.completed = true;
      this.state.currentChallenge.completedAt = new Date();
      this.state.challengeHistory.push(this.state.currentChallenge);
      this.state.currentChallenge = null;
      this.state.currentHintsUsed = 0;
      this.state.awaitingVerification = false;
      this.notifyStateChange();
    }
  }

  skipCurrentChallenge(): void {
    if (this.state.currentChallenge) {
      this.state.currentChallenge.completed = false;
      this.state.challengeHistory.push(this.state.currentChallenge);
      this.state.currentChallenge = null;
      this.state.currentHintsUsed = 0;
      this.state.awaitingVerification = false;
      this.notifyStateChange();
    }
  }

  useHint(): string | null {
    if (!this.state.currentChallenge) {return null;}
    if (this.state.currentHintsUsed >= MAX_HINTS) {return null;}

    const hint = this.state.currentChallenge.hints[this.state.currentHintsUsed];
    this.state.currentHintsUsed++;
    this.notifyStateChange();
    return hint;
  }

  setAwaitingVerification(awaiting: boolean): void {
    this.state.awaitingVerification = awaiting;
    this.notifyStateChange();
  }

  getCurrentChallenge(): Challenge | null {
    return this.state.currentChallenge ? { ...this.state.currentChallenge } : null;
  }

  getAvailableHints(): number {
    return MAX_HINTS - this.state.currentHintsUsed;
  }

  reset(): void {
    this.state = this.createInitialState();
    this.notifyStateChange();
  }

  onStateChanged(callback: (state: ChallengeState) => void): void {
    this.onStateChange = callback;
  }

  private notifyStateChange(): void {
    if (this.onStateChange) {
      this.onStateChange(this.getState());
    }
  }
}
