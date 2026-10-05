# Love Letter Offline

A local Pygame version of Love Letter for one human player and one to three AI opponents. It does not require a network connection or a game server.

## Requirements

- Python 3.12 or another version supported by Pygame 2.6.1
- A desktop environment capable of opening a Pygame window

## Run From Source

Run all commands from this directory:

```bash
cd Love_Letter_Base_offline
python -m pip install -r requirements.txt
python main.py
```

On systems where Python is named `python3`, use `python3` instead of `python`.

## Start A Game

1. Enter a player name and a room code. The room code is only a local game label in offline mode.
2. Select a total of two, three, or four players.
3. Click **START GAME**. One seat is controlled by you and every other seat is controlled by AI.
4. On your turn, click a card and then select a target or number when the card requires one.

Use the on-screen controls to pause the AI or change its speed. Press `Esc` during a game to return to the menu.

## Tests

Run the maintained game-rule test suite from this directory:

```bash
python -m unittest test_game.py
```

Run one test with its fully qualified name, for example:

```bash
python -m unittest test_game.GameRulesTest.testTwoPlayerSetupRemovesReserveAndThreeFaceUpCards
```

## Build Packages

Detailed packaging instructions are in [PACKAGING.md](PACKAGING.md).

### Windows

Build with Python 3.12 and PyInstaller:

```powershell
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean LoveLetterOffline.spec
```

The executable is created at `dist/LoveLetterOffline.exe`.

## Main Files

| File | Purpose |
| --- | --- |
| `main.py` | Offline game entry point and UI flow |
| `game.py` | Love Letter game rules and turn state |
| `ai.py` | AI player decisions |
| `gui.py` | Shared screens, controls, and visual effects |
| `card.py` | Card definitions and effects |
| `card_pile.py` | Deck creation and card drawing |
| `player.py` | Player state and hand management |
| `test_game.py` | Game-rule test suite |
| `images/` | Card and UI images |

`build/` and `dist/` are generated output directories. Make changes in the Python source or packaging configuration instead of editing generated files.
