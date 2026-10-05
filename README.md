# Love Letter

A Pygame implementation of Love Letter with two ways to play:

- **Offline:** play against one to three AI opponents.
- **Online:** play with two to four people in private rooms.

Windows players can use the packaged `.exe` files without installing Python or opening a terminal.

## Play Offline On Windows

1. Open the repository's **Actions** tab on GitHub.
2. Select **Build offline game**.
3. Open a successful workflow run or choose **Run workflow** to create a new build.
4. Download the `LoveLetterOffline-Windows` artifact.
5. Extract the downloaded ZIP file.
6. Double-click `LoveLetterOffline.exe`.
7. Enter a player name, choose two to four total players, and click **START GAME**.

The other seats are controlled by AI. No internet connection or game server is required.

See the [offline game guide](Love_Letter_Base_offline/README.md) for source installation, tests, and local EXE build instructions.

## Play Online On Windows

### What Players Need

Players only need `LoveLetterOnline.exe` and the address of a running Love Letter server.

1. Open the repository's **Actions** tab on GitHub.
2. Select **Build online game**.
3. Open a successful workflow run or choose **Run workflow** to create a new build.
4. Download the `LoveLetterOnline-Windows` artifact.
5. Extract the downloaded ZIP file.
6. Double-click `LoveLetterOnline.exe`.
7. Enter the server address, such as `game.example.com:21011`.
8. Enter a player name and room code.

The first player clicks **CREATE ROOM**. Other players use the same server address and room code, then click **JOIN ROOM**. When at least two players are listed, the player marked **(HOST)** clicks **START GAME**.

### Start The Online Server

One person must run the server on a computer reachable by every player. A public VPS or a private Tailscale network is recommended for players on different internet connections.

```bash
cd Love_Letter_Base_online
python -m pip install -r requirements.txt
python server.py
```

The server listens on TCP port `21011`. Keep it running while people play and allow that port through the server firewall.

See the [online game guide](Love_Letter_Base_online/README.md) for LAN, VPS, Tailscale, port forwarding, `tmux`, troubleshooting, and local EXE build instructions.

## Run From Source

Install Python and clone the repository:

```bash
git clone https://github.com/hoainam1401/Love_Letter.git
cd Love_Letter
```

### Offline Game

```bash
cd Love_Letter_Base_offline
python -m pip install -r requirements.txt
python main.py
```

### Online Game

Start the server:

```bash
cd Love_Letter_Base_online
python -m pip install -r requirements.txt
python server.py
```

Start each client from another terminal:

```bash
cd Love_Letter_Base_online
python main.py
```

Enter the server address in the game window. The default `127.0.0.1:21011` works only when the client and server are on the same computer.

## Project Structure

| Path | Purpose |
| --- | --- |
| [`Love_Letter_Base_offline/`](Love_Letter_Base_offline/README.md) | Local Pygame game with AI and Windows packaging |
| [`Love_Letter_Base_online/`](Love_Letter_Base_online/README.md) | Socket-based Pygame client/server and Windows client packaging |
| `Love_Letter_Base/` | Separate legacy Pygame/socket implementation |

## Development Checks

Run the offline game-rule tests:

```bash
cd Love_Letter_Base_offline
python -m unittest test_game.py
```

## License

This project is for educational purposes.
