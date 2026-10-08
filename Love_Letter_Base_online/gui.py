import importlib.util
from pathlib import Path
import sys

if getattr(sys, "frozen", False):
    _source = Path(sys._MEIPASS) / "shared_gui" / "gui.py"
else:
    _source = (
        Path(__file__).resolve().parent.parent / "Love_Letter_Base_offline" / "gui.py"
    )
_spec = importlib.util.spec_from_file_location("love_letter_offline_gui", _source)
_gui = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _gui
_spec.loader.exec_module(_gui)

for _name in dir(_gui):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_gui, _name)

pygame.display.set_caption("Love Letter - Online")


class LoginScreen:
    def __init__(self, defaultServer="127.0.0.1:21011"):
        fieldWidth = 470
        fieldX = WIDTH // 2 - fieldWidth // 2
        self.serverAddress = TextInput(
            (fieldX, 350, fieldWidth, 68), "Server address", max_length=100
        )
        self.serverAddress.text = defaultServer
        self.username = TextInput(
            (fieldX, 460, fieldWidth, 68), "Username", max_length=20
        )
        self.roomCode = TextInput(
            (fieldX, 570, fieldWidth, 68),
            "Room code",
            max_length=12,
            uppercase=True,
        )
        self.createButton = Button((WIDTH // 2 - 235, 690, 220, 66), "CREATE ROOM")
        self.joinButton = Button((WIDTH // 2 + 15, 690, 220, 66), "JOIN ROOM")

    def handle_event(self, event):
        submit = self.serverAddress.handle_event(event)
        submit = self.username.handle_event(event) or submit
        submit = self.roomCode.handle_event(event) or submit
        if self.createButton.handle_event(event):
            return (
                "create",
                self.username.text.strip(),
                self.roomCode.text.strip().upper(),
                self.serverAddress.text.strip(),
            )
        if self.joinButton.handle_event(event) or submit:
            return (
                "join",
                self.username.text.strip(),
                self.roomCode.text.strip().upper(),
                self.serverAddress.text.strip(),
            )
        return None

    def draw(self, message=""):
        WIN.fill(BACKGROUND)
        for x, y, radius in ((120, 135, 90), (870, 170, 120), (120, 850, 130)):
            pygame.draw.circle(WIN, (239, 219, 213), (x, y), radius)
            pygame.draw.circle(WIN, ROSE_LIGHT, (x, y), radius, 2)
        panel = pygame.Rect(WIDTH // 2 - 305, 65, 610, 770)
        _draw_panel(panel, 26)
        _center_text("LOVE", TITLE_FONT, ROSE_DARK, (WIDTH // 2, 137))
        _center_text("LETTER", HEADING_FONT, GOLD, (WIDTH // 2, 185))
        pygame.draw.line(WIN, GOLD, (385, 205), (615, 205), 3)
        _center_text(
            "Create a table or join by room code", SMALL_FONT, MUTED, (WIDTH // 2, 252)
        )
        _center_text("SERVER ADDRESS", TINY_FONT, MUTED, (WIDTH // 2, 330))
        _center_text("PLAYER NAME", TINY_FONT, MUTED, (WIDTH // 2, 440))
        _center_text("ROOM CODE", TINY_FONT, MUTED, (WIDTH // 2, 550))
        self.serverAddress.draw()
        self.username.draw()
        self.roomCode.draw()
        self.createButton.draw()
        self.joinButton.draw()
        if message:
            _center_text(message, SMALL_FONT, RED, (WIDTH // 2, 795))
        pygame.display.update()


class LobbyScreen:
    def __init__(self):
        self.startButton = Button((WIDTH // 2 - 135, 690, 270, 66), "START GAME")
        self.backButton = Button((40, 40, 125, 48), "LEAVE")

    def handle_event(self, event, canStart):
        if self.backButton.handle_event(event):
            return "back"
        if canStart and self.startButton.handle_event(event):
            return "start"
        return None

    def draw(self, username, roomCode, names, canStart, message=""):
        WIN.fill(BACKGROUND)
        self.backButton.draw()
        _center_text("ONLINE TABLE", HEADING_FONT, ROSE_DARK, (WIDTH // 2, 160))
        _center_text(f"ROOM  {roomCode}", SMALL_FONT, GOLD, (WIDTH // 2, 215))
        _center_text(f"Signed in as {username}", SMALL_FONT, MUTED, (WIDTH // 2, 260))
        panel = pygame.Rect(WIDTH // 2 - 270, 310, 540, 310)
        _draw_panel(panel)
        _center_text("CONNECTED PLAYERS", TEXT_FONT, INK, (WIDTH // 2, 350))
        for index, name in enumerate(names):
            suffix = " (HOST)" if index == 0 else ""
            _center_text(
                f"{index + 1}. {name}{suffix}",
                TEXT_FONT,
                ROSE_DARK,
                (WIDTH // 2, 405 + index * 48),
            )
        if not names:
            _center_text("Connecting...", TEXT_FONT, MUTED, (WIDTH // 2, 455))
        if canStart:
            self.startButton.draw()
        else:
            _center_text(
                "Waiting for the host to start", SMALL_FONT, MUTED, (WIDTH // 2, 720)
            )
        if message:
            _center_text(message, SMALL_FONT, RED, (WIDTH // 2, 790))
        pygame.display.update()


def draw_game_screen(*args, **kwargs):
    kwargs["onlineMode"] = True
    return _gui.draw_game_screen(*args, **kwargs)
