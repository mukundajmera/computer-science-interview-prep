# Connect Four — Follow-Up Questions

## 1. How to support custom board sizes?
Inject `rows`/`cols` in constructors and keep directional win logic generic.

## 2. How to add undo/redo?
Store immutable `Move` records and reverse only the latest mutation.

## 3. How to add AI difficulty levels?
Expose `BotMoveStrategy` interface with easy/medium/hard implementations.

## 4. How to support concurrent game sessions?
Add `GameSession` wrapper keyed by session id and keep each game isolated.

## 5. How to persist and replay games?
Persist move history and rebuild board by replaying events.
