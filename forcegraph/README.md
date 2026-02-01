# Code Quest

Gamified code challenges powered by AI to make exploring your codebase fun and engaging!

## Features

- **AI-Generated Challenges**: OpenAI GPT-4 generates context-aware challenges tailored to your codebase
- **Navigation Tasks**: Find specific functions, classes, or code patterns
- **Modification Tasks**: Make targeted code changes to improve or refactor
- **Rich Gamification**:
  - Points system with streak multipliers
  - Level progression with unlockable difficulty tiers
  - Celebration animations on success
  - Hint system with strategic trade-offs
- **Auto-Advance**: Challenges automatically progress as you complete them
- **Real-time Verification**: Automatically detects when you've completed a challenge

## Requirements

- Visual Studio Code 1.108.1 or higher
- OpenAI API key (set as environment variable `OPENAI_API_KEY`)

## Setup

1. Install the extension from the VS Code Marketplace
2. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here
   ```
3. Reload VS Code
4. Open a workspace with code
5. Click the "Code Quest" icon in the activity bar
6. Click "Start Challenge" to begin!

## Extension Settings

- `forcegraph.openaiApiKey`: OpenAI API key for generating challenges (set via environment variable `OPENAI_API_KEY`)
- `forcegraph.autoAdvance`: Automatically advance to next challenge after completion (default: `true`)
- `forcegraph.startDifficulty`: Starting difficulty level - `easy`, `medium`, or `hard` (default: `medium`)

## How It Works

1. Click "Start Challenge" in the sidebar
2. AI analyzes your workspace and generates a challenge
3. Navigate to the target location or make the required code change
4. The extension automatically detects when you've completed the challenge
5. Earn points, build your streak, and level up!
6. Challenges auto-advance to keep you engaged

## Point System

- **Correct Answer**: +100 points (+2x for streak of 3+)
- **Use Hint**: -10 points (2 hints available per challenge)
- **Skip Challenge**: -25 points
- **Level Up**: Every 500 points

## Challenge Types

### Navigation Challenges
Find specific elements in your codebase:
- Functions with certain behavior
- Classes with specific properties
- Code patterns or anti-patterns
- Exported symbols

### Modification Challenges
Make targeted changes:
- Add error handling
- Refactor code
- Fix bugs
- Improve performance

## Keyboard Shortcuts

Open the Command Palette (Ctrl/Cmd + Shift + P) and use:
- `forcegraph.startChallenge`: Start a new challenge
- `forcegraph.submitAnswer`: Submit your answer
- `forcegraph.showHint`: Get a hint (-10 points)
- `forcegraph.skipChallenge`: Skip to next challenge (-25 points)
- `forcegraph.resetGame`: Reset your game progress

## File Exclusions

The extension automatically ignores:
- `node_modules`, `dist`, `out`, `build`
- Test files (`*.test.*`, `*.spec.*`)
- Git directory (`.git`)
- VS Code settings (`.vscode`)
- Coverage reports, type definitions, and other generated files

## Known Issues

- First challenge generation may take a few seconds as the workspace is analyzed
- Modification challenges require manual submission if auto-detection fails
- Ensure your OpenAI API key has sufficient credits

## Release Notes

### 0.0.1

Initial release of Code Quest:
- AI-generated navigation and modification challenges
- Gamified point system with streaks and levels
- Rich interactive UI with celebrations
- Hint system and challenge skipping
- Auto-advance between challenges

---

**Enjoy your code adventure!** 🎯🚀
