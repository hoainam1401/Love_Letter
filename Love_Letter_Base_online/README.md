# Love Letter Online

A two-to-four-player Pygame version of Love Letter using a central Python TCP server. Players join private rooms with a shared alphanumeric room code.

The first player creates the room and becomes its host. Only the host can start a game or request a rematch.

## Architecture

The main playable online game consists of:

- `server.py`: authoritative game server and room manager
- `main.py`: Pygame network client
- `game.py`, `card.py`, `card_pile.py`, and `player.py`: server-side game rules
- `gui.py`: online screens plus shared presentation loaded from `../Love_Letter_Base_offline/gui.py`

Keep `Love_Letter_Base_online/` and `Love_Letter_Base_offline/` next to each other in the repository. The online client will not load its shared GUI if the offline folder is missing or moved.

## Requirements

- Python 3.12 or another version supported by Pygame 2.6.1
- TCP connectivity from every player to the server on port `21011`
- The full repository checkout, including the sibling offline folder

Players using the packaged Windows EXE do not need Python or a repository checkout.

## Windows EXE For Players

The online client can be distributed as a single `LoveLetterOnline.exe` file. It does not open a terminal window.

### Download From GitHub Actions

1. Open the repository's **Actions** tab.
2. Select **Build online game**.
3. Choose **Run workflow**.
4. Download the `LoveLetterOnline-Windows` artifact after the workflow finishes.
5. Extract the artifact and run `LoveLetterOnline.exe`.

GitHub stores the artifact for 30 days.

### Connect Without A Terminal

1. Double-click `LoveLetterOnline.exe`.
2. Enter the public server IP or DNS name in **SERVER ADDRESS**, for example `game.example.com:21011`.
3. Enter a player name and room code.
4. Click **CREATE ROOM** or **JOIN ROOM**.

The EXE is the game client only. A reachable `server.py` process must still be running on a VPS, Tailscale network, or port-forwarded host.

### Build The EXE Locally

Run this on Windows with Python 3.12:

```powershell
cd Love_Letter_Base_online
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean LoveLetterOnline.spec
```

The executable is created at `dist/LoveLetterOnline.exe`.

## Install

Run from this directory on the server and on every player's computer:

```bash
cd Love_Letter_Base_online
python -m pip install -r requirements.txt
```

On systems where Python is named `python3`, use `python3` instead of `python`.

## Quick Start On One Computer

Start the server in one terminal:

```bash
python server.py
```

Start two clients in separate terminals:

```bash
python main.py
```

The client defaults to `127.0.0.1:21011`, so no address configuration is needed when the server and clients run on the same computer.

## Play On A Local Network

Start the server on the host computer:

```bash
python server.py
```

Find the host computer's LAN address. On macOS this is commonly:

```bash
ipconfig getifaddr en0
```

Players can type `192.168.1.85:21011` into the **SERVER ADDRESS** field. When running from source, they can alternatively set the address from the terminal:

```bash
LOVE_LETTER_HOST=192.168.1.85 python main.py
```

PowerShell uses this syntax:

```powershell
$env:LOVE_LETTER_HOST = "192.168.1.85"
python main.py
```

Replace `192.168.1.85` with the actual host address. All devices must be able to reach TCP port `21011`, and the host firewall must allow incoming Python connections.

## Play Across The Internet

The server must have an address reachable by every player. There are three common options.

### Public VPS

Run `server.py` on a VPS and allow inbound TCP port `21011` in both the provider's firewall and the operating-system firewall. Players enter the VPS address or DNS name in **SERVER ADDRESS**, or source users can run:

```bash
LOVE_LETTER_HOST=game.example.com python main.py
```

### Tailscale

Install Tailscale on the server and each player's computer, add everyone to the same private network, and find the server's Tailscale address:

```bash
tailscale ip -4
```

Players enter the returned `100.x.x.x:21011` address in **SERVER ADDRESS**, or source users can run:

```bash
LOVE_LETTER_HOST=100.x.x.x python main.py
```

### Router Port Forwarding

Forward TCP port `21011` from the router to the server computer, allow that port through the firewall, and connect clients to the router's public IP. This may not work when the internet provider uses CGNAT. Exposing the current raw TCP server publicly also provides no transport encryption or user authentication, so a VPS firewall or private Tailscale network is preferable.

## Keep The Server Running With tmux

On a Linux VPS:

```bash
tmux new -s love-letter
python3 server.py
```

Detach with `Ctrl+B`, then `D`. Reattach later with:

```bash
tmux attach -t love-letter
```

Restart `server.py` after updating its source because an already-running process does not load new code automatically.

## Create And Join A Room

1. The first player enters a name and room code, then clicks **CREATE ROOM**.
2. Other players enter their names and the exact same room code, then click **JOIN ROOM**.
3. Wait until at least two names appear under **CONNECTED PLAYERS**.
4. The player marked **(HOST)** clicks **START GAME**.

Room codes may contain only letters and numbers and are limited to 12 characters. A room supports two to four players. A game cannot be joined after it has started.

If the host leaves, the room closes. If another player leaves during a game, the remaining table returns to the lobby.

## Configuration

The server address can be entered directly on the login screen. When running from source, the client also reads these optional environment variables to set the initial value:

| Variable | Default | Purpose |
| --- | --- | --- |
| `LOVE_LETTER_HOST` | `127.0.0.1` | Server IP address or DNS name |
| `LOVE_LETTER_PORT` | `21011` | Server TCP port |

If a different port is required, start the server with a small code/configuration change because `server.py` currently starts on port `21011`. All clients must use the same port.

## Troubleshooting

### The client cannot connect

- Confirm `server.py` is running and prints `Server is listening on 0.0.0.0:21011...`.
- Confirm the client uses the server's address, not its own address.
- Open TCP port `21011` in the server firewall and VPS security group.
- Do not use `127.0.0.1` unless the server is on the same computer as the client.

### The start button is missing

- At least two players must be listed in the room.
- Only the player who clicked **CREATE ROOM** can start.
- The room creator is marked **(HOST)**.
- Restart an old server process after pulling or changing code.

### Players see different rooms

Use the same server address, port, and room code on every client. Room codes are case-insensitive because the client and server convert them to uppercase.

## Main Files

| Path | Purpose |
| --- | --- |
| `main.py` | Online Pygame client |
| `server.py` | TCP room and game server |
| `gui.py` | Network lobby UI and offline GUI adapter |
| `LoveLetterOnline.spec` | PyInstaller configuration for the Windows client EXE |
| `game.py` | Authoritative game rules |
| `images/` | Card and UI images |
