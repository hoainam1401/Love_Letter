import os
from dataclasses import dataclass

import pygame


WIDTH = 1000
HEIGHT = 1000
FPS = 60

INK = (38, 27, 47)
BACKGROUND = (245, 237, 224)
PANEL = (255, 252, 245)
PANEL_DARK = (55, 42, 67)
MUTED = (126, 112, 127)
ROSE = (164, 54, 79)
ROSE_DARK = (112, 34, 57)
ROSE_LIGHT = (232, 183, 185)
GOLD = (207, 157, 68)
GREEN = (66, 139, 105)
RED = (181, 62, 68)
WHITE = (255, 255, 255)
SHADOW = (49, 31, 47)

GAME_BACKGROUND = (40, 42, 54)
GAME_PANEL = (68, 71, 90)
GAME_TEXT = (248, 248, 242)
GAME_MUTED = (98, 114, 164)
GAME_CYAN = (139, 233, 253)
GAME_GREEN = (80, 250, 123)
GAME_ORANGE = (255, 184, 108)
GAME_PINK = (255, 121, 198)
GAME_PURPLE = (189, 147, 249)
GAME_RED = (255, 85, 85)
GAME_YELLOW = (241, 250, 140)
GAME_SHADOW = (0, 0, 0)

CARD_WIDTH = 120
CARD_HEIGHT = 168

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Love Letter - Offline")

TITLE_FONT = pygame.font.Font(None, 112)
HEADING_FONT = pygame.font.Font(None, 56)
BUTTON_FONT = pygame.font.Font(None, 38)
TEXT_FONT = pygame.font.Font(None, 34)
SMALL_FONT = pygame.font.Font(None, 25)
TINY_FONT = pygame.font.Font(None, 20)


def _load_card_images():
    images = {}
    image_dir = os.path.join(os.path.dirname(__file__), "images")
    names = [
        "Guard",
        "Priest",
        "Baron",
        "Handmaid",
        "Prince",
        "King",
        "Countess",
        "Princess",
        "Back",
    ]
    for name in names:
        path = os.path.join(image_dir, f"{name}.png")
        if os.path.exists(path):
            image = pygame.image.load(path)
            images[name] = pygame.transform.smoothscale(
                image, (CARD_WIDTH, CARD_HEIGHT)
            )
        else:
            surface = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            surface.fill(PANEL_DARK if name == "Back" else PANEL)
            pygame.draw.rect(surface, ROSE, surface.get_rect(), 3, 10)
            label = SMALL_FONT.render(name, True, WHITE if name == "Back" else INK)
            surface.blit(label, label.get_rect(center=surface.get_rect().center))
            images[name] = surface
    return images


CARD_IMAGES = _load_card_images()
SMALL_CARD_BACK = pygame.transform.smoothscale(CARD_IMAGES["Back"], (96, 134))

_crownPath = os.path.join(os.path.dirname(__file__), "images", "crown.png")
CROWN_IMAGE = (
    pygame.transform.smoothscale(pygame.image.load(_crownPath), (54, 54))
    if os.path.exists(_crownPath)
    else None
)


def _center_text(text, font, color, center):
    surface = font.render(text, True, color)
    WIN.blit(surface, surface.get_rect(center=center))


def _draw_panel(rect, radius=18):
    pygame.draw.rect(WIN, (205, 192, 183), rect.move(8, 8), border_radius=radius)
    pygame.draw.rect(WIN, PANEL, rect, border_radius=radius)
    pygame.draw.rect(WIN, ROSE_LIGHT, rect, 2, border_radius=radius)


class Button:
    def __init__(self, rect, text):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self):
        pygame.draw.rect(WIN, ROSE_DARK, self.rect.move(0, 5), border_radius=12)
        color = (190, 67, 92) if self.hovered else ROSE
        pygame.draw.rect(WIN, color, self.rect, border_radius=12)
        pygame.draw.rect(WIN, ROSE_DARK, self.rect, 2, border_radius=12)
        _center_text(self.text, BUTTON_FONT, WHITE, self.rect.center)


class TextInput:
    def __init__(self, rect, placeholder, *, max_length=24, uppercase=False):
        self.rect = pygame.Rect(rect)
        self.placeholder = placeholder
        self.max_length = max_length
        self.uppercase = uppercase
        self.text = ""
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                pygame.key.start_text_input()
            return False
        if not self.active:
            return False
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return True
        elif event.unicode and event.unicode.isprintable():
            value = event.unicode.upper() if self.uppercase else event.unicode
            self.text = (self.text + value)[: self.max_length]
        return False

    def draw(self):
        border = ROSE if self.active else ROSE_LIGHT
        pygame.draw.rect(WIN, WHITE, self.rect, border_radius=12)
        pygame.draw.rect(WIN, border, self.rect, 3, border_radius=12)
        display_text = self.text or self.placeholder
        color = INK if self.text else MUTED
        rendered = TEXT_FONT.render(display_text, True, color)
        WIN.blit(rendered, (self.rect.x + 18, self.rect.centery - rendered.get_height() // 2))
        if self.active and pygame.time.get_ticks() % 1000 < 500:
            cursor_width = rendered.get_width() if self.text else 0
            cursor_x = self.rect.x + 18 + cursor_width
            pygame.draw.line(
                WIN,
                INK,
                (cursor_x, self.rect.y + 18),
                (cursor_x, self.rect.bottom - 18),
                2,
            )


class LoginScreen:
    def __init__(self):
        field_width = 470
        field_x = WIDTH // 2 - field_width // 2
        self.username = TextInput(
            (field_x, 410, field_width, 68), "Username", max_length=20
        )
        self.roomCode = TextInput(
            (field_x, 510, field_width, 68),
            "Room code",
            max_length=12,
            uppercase=True,
        )
        self.playButton = Button((WIDTH // 2 - 135, 625, 270, 66), "CREATE ROOM")

    def handle_event(self, event):
        submit = self.username.handle_event(event)
        submit = self.roomCode.handle_event(event) or submit
        submit = self.playButton.handle_event(event) or submit
        if submit:
            return self.username.text.strip(), self.roomCode.text.strip().upper()
        return None

    def draw(self, message=""):
        WIN.fill(BACKGROUND)
        for x, y, radius in ((120, 135, 90), (870, 170, 120), (120, 850, 130)):
            pygame.draw.circle(WIN, (239, 219, 213), (x, y), radius)
            pygame.draw.circle(WIN, ROSE_LIGHT, (x, y), radius, 2)

        panel = pygame.Rect(WIDTH // 2 - 305, 105, 610, 680)
        _draw_panel(panel, 26)
        _center_text("LOVE", TITLE_FONT, ROSE_DARK, (WIDTH // 2, 177))
        _center_text("LETTER", HEADING_FONT, GOLD, (WIDTH // 2, 225))
        pygame.draw.line(WIN, GOLD, (385, 245), (615, 245), 3)
        _center_text(
            "Create a private table against the AI",
            SMALL_FONT,
            MUTED,
            (WIDTH // 2, 292),
        )
        _center_text("PLAYER NAME", TINY_FONT, MUTED, (WIDTH // 2, 390))
        _center_text("ROOM CODE", TINY_FONT, MUTED, (WIDTH // 2, 490))
        self.username.draw()
        self.roomCode.draw()
        self.playButton.draw()
        if message:
            _center_text(message, SMALL_FONT, RED, (WIDTH // 2, 735))
        pygame.display.update()


class PlayerSelectionScreen:
    def __init__(self):
        self.selectedCount = 2
        self.countButtons = {
            count: Button((WIDTH // 2 - 210 + (count - 2) * 150, 430, 120, 70), str(count))
            for count in range(2, 5)
        }
        self.startButton = Button((WIDTH // 2 - 135, 590, 270, 66), "START GAME")
        self.backButton = Button((40, 40, 125, 48), "BACK")

    def handle_event(self, event):
        if self.backButton.handle_event(event):
            return "back"
        for count, button in self.countButtons.items():
            if button.handle_event(event):
                self.selectedCount = count
        if self.startButton.handle_event(event):
            return self.selectedCount
        return None

    def draw(self, username, roomCode):
        WIN.fill(BACKGROUND)
        self.backButton.draw()
        _center_text("BUILD YOUR TABLE", HEADING_FONT, ROSE_DARK, (WIDTH // 2, 180))
        _center_text(f"ROOM  {roomCode}", SMALL_FONT, GOLD, (WIDTH // 2, 235))
        _center_text(
            f"{username}, choose the total number of players",
            TEXT_FONT,
            INK,
            (WIDTH // 2, 320),
        )
        _center_text(
            "Empty seats will be controlled by AI players",
            SMALL_FONT,
            MUTED,
            (WIDTH // 2, 365),
        )

        for count, button in self.countButtons.items():
            button.draw()
            if count == self.selectedCount:
                pygame.draw.rect(WIN, GOLD, button.rect.inflate(12, 12), 4, 16)

        self.startButton.draw()
        aiCount = self.selectedCount - 1
        _center_text(
            f"1 human + {aiCount} AI player{'s' if aiCount > 1 else ''}",
            SMALL_FONT,
            MUTED,
            (WIDTH // 2, 710),
        )
        pygame.display.update()


@dataclass(frozen=True)
class GameView:
    roomCode: str
    names: list[str]
    statuses: list[str]
    tokens: list[int]
    humanHand: list[str]
    currentPlayer: int
    remainingCards: int
    gameState: str
    winners: list[str]
    discardPiles: list[list[tuple[str, int]]]
    notifications: list[str]


def draw_game_screen(view, mousePos, validTargets, viewingDiscardIndex=None):
    WIN.fill(GAME_BACKGROUND)
    cardRects = []
    playerRects = []
    numberButtons = []
    discardButtons = []

    pygame.draw.rect(WIN, GAME_SHADOW, (0, 4, WIDTH, 90))
    pygame.draw.rect(WIN, GAME_PANEL, (0, 0, WIDTH, 88))
    pygame.draw.line(WIN, GAME_PINK, (0, 87), (WIDTH, 87), 4)
    title = HEADING_FONT.render("Love Letter", True, GAME_PINK)
    WIN.blit(title, (25, 19))
    room = SMALL_FONT.render(f"ROOM  {view.roomCode}", True, GAME_CYAN)
    WIN.blit(room, room.get_rect(center=(WIDTH // 2, 44)))
    deck = TEXT_FONT.render(f"Deck: {view.remainingCards}", True, GAME_CYAN)
    WIN.blit(deck, (WIDTH - deck.get_width() - 30, 29))

    noticeRect = pygame.Rect(WIDTH // 2 - 245, 100, 490, 88)
    pygame.draw.rect(WIN, GAME_SHADOW, noticeRect.move(4, 4), border_radius=10)
    pygame.draw.rect(WIN, GAME_PANEL, noticeRect, border_radius=10)
    pygame.draw.rect(WIN, GAME_CYAN, noticeRect, 2, border_radius=10)
    noticeTitle = TINY_FONT.render("GAME LOG", True, GAME_CYAN)
    WIN.blit(noticeTitle, (noticeRect.x + 12, noticeRect.y + 8))
    for lineIndex, notification in enumerate(view.notifications[-3:]):
        text = notification if len(notification) <= 76 else notification[:73] + "..."
        rendered = TINY_FONT.render(text, True, GAME_TEXT)
        WIN.blit(rendered, (noticeRect.x + 12, noticeRect.y + 29 + lineIndex * 18))

    deckX = WIDTH // 2 - CARD_WIDTH // 2
    deckY = 445
    if view.remainingCards > 0:
        for index in range(min(4, view.remainingCards)):
            offset = index * 4
            pygame.draw.rect(
                WIN,
                GAME_SHADOW,
                (deckX + offset + 4, deckY + offset + 4, CARD_WIDTH, CARD_HEIGHT),
                border_radius=10,
            )
            WIN.blit(CARD_IMAGES["Back"], (deckX + offset, deckY + offset))
            pygame.draw.rect(
                WIN,
                GAME_PINK,
                (deckX + offset, deckY + offset, CARD_WIDTH, CARD_HEIGHT),
                3,
                10,
            )
        _center_text("DECK", SMALL_FONT, GAME_PURPLE, (WIDTH // 2, deckY + 194))

    positions = [
        (WIDTH // 2 - 100, 650),
        (WIDTH - 250, 380),
        (WIDTH // 2 - 100, 195),
        (50, 380),
    ]
    for index, name in enumerate(view.names[:4]):
        x, y = positions[index]
        rect = pygame.Rect(x, y, 200, 180)
        status = view.statuses[index]
        isTarget = index in validTargets
        if status == "KO":
            fill, border = GAME_RED, GAME_MUTED
        elif index == view.currentPlayer:
            fill, border = GAME_GREEN, GAME_YELLOW
        elif isTarget:
            fill, border = GAME_ORANGE, GAME_YELLOW
        else:
            fill, border = GAME_PURPLE, GAME_PINK

        pygame.draw.rect(WIN, GAME_SHADOW, rect.move(5, 5), border_radius=10)
        pygame.draw.rect(WIN, fill, rect, border_radius=13)
        pygame.draw.rect(
            WIN,
            border,
            rect,
            5 if isTarget and rect.collidepoint(mousePos) else 3,
            13,
        )
        if isTarget:
            playerRects.append((index, rect))

        _center_text(name, TEXT_FONT, GAME_TEXT, (rect.centerx, rect.y + 28))
        label = "Active" if status == "No Protection" else status
        statusColor = (
            GAME_RED
            if status == "KO"
            else GAME_CYAN if status == "Protected" else GAME_GREEN
        )
        _center_text(label, SMALL_FONT, statusColor, (rect.centerx, rect.y + 61))
        _center_text(
            f"Tokens: {view.tokens[index]}",
            SMALL_FONT,
            GAME_YELLOW,
            (rect.centerx, rect.y + 96),
        )

        buttonX = rect.right + 8 if rect.x < 100 else rect.x - 58
        discardRect = pygame.Rect(buttonX, rect.y + 10, 50, 50)
        discardButtons.append((index, discardRect))
        discardColor = GAME_ORANGE if discardRect.collidepoint(mousePos) else GAME_PURPLE
        pygame.draw.rect(WIN, GAME_SHADOW, discardRect.move(2, 2), border_radius=8)
        pygame.draw.rect(WIN, discardColor, discardRect, border_radius=8)
        pygame.draw.rect(WIN, GAME_PINK, discardRect, 2, border_radius=8)
        _center_text(
            str(len(view.discardPiles[index])),
            SMALL_FONT,
            GAME_YELLOW,
            discardRect.center,
        )

        if index == 0:
            totalWidth = len(view.humanHand) * CARD_WIDTH + max(
                0, len(view.humanHand) - 1
            ) * 18
            startX = rect.centerx - totalWidth // 2
            for cardIndex, cardName in enumerate(view.humanHand):
                cardRect = pygame.Rect(
                    startX + cardIndex * (CARD_WIDTH + 18),
                    rect.y + 112,
                    CARD_WIDTH,
                    CARD_HEIGHT,
                )
                cardRects.append(cardRect)
                if (
                    cardRect.collidepoint(mousePos)
                    and view.gameState == "WAITING_FOR_CARD"
                ):
                    pygame.draw.rect(WIN, GAME_YELLOW, cardRect.inflate(10, 10), 4, 13)
                pygame.draw.rect(WIN, GAME_SHADOW, cardRect.move(4, 4), border_radius=10)
                WIN.blit(CARD_IMAGES.get(cardName, CARD_IMAGES["Back"]), cardRect)
                pygame.draw.rect(WIN, GAME_PINK, cardRect, 3, 10)
                caption = TINY_FONT.render(cardName, True, GAME_CYAN)
                captionRect = caption.get_rect(center=(cardRect.centerx, cardRect.bottom + 12))
                WIN.blit(caption, captionRect)
        elif status != "KO":
            cardX = rect.centerx - SMALL_CARD_BACK.get_width() // 2
            cardY = rect.y + 112
            pygame.draw.rect(
                WIN,
                GAME_SHADOW,
                (cardX + 3, cardY + 3, 96, 134),
                border_radius=8,
            )
            WIN.blit(
                SMALL_CARD_BACK,
                (cardX, cardY),
            )

    if viewingDiscardIndex is not None and 0 <= viewingDiscardIndex < len(view.names):
        pile = view.discardPiles[viewingDiscardIndex]
        panelRect = pygame.Rect(285, 325, 430, 155)
        pygame.draw.rect(WIN, GAME_SHADOW, panelRect.move(4, 4), border_radius=10)
        pygame.draw.rect(WIN, GAME_PANEL, panelRect, border_radius=10)
        pygame.draw.rect(WIN, GAME_CYAN, panelRect, 3, border_radius=10)
        heading = SMALL_FONT.render(
            f"{view.names[viewingDiscardIndex]}'s discards", True, GAME_CYAN
        )
        WIN.blit(heading, (panelRect.x + 14, panelRect.y + 10))
        if not pile:
            empty = SMALL_FONT.render("No cards played yet", True, GAME_MUTED)
            WIN.blit(empty, (panelRect.x + 14, panelRect.y + 58))
        for cardIndex, (cardName, value) in enumerate(pile[-8:]):
            cardRect = pygame.Rect(panelRect.x + 14 + cardIndex * 50, panelRect.y + 48, 42, 72)
            pygame.draw.rect(WIN, GAME_BACKGROUND, cardRect, border_radius=5)
            pygame.draw.rect(WIN, GAME_PINK, cardRect, 2, border_radius=5)
            _center_text(str(value), SMALL_FONT, GAME_YELLOW, (cardRect.centerx, cardRect.y + 22))
            shortName = cardName[:5]
            _center_text(shortName, TINY_FONT, GAME_TEXT, (cardRect.centerx, cardRect.y + 52))

    if view.gameState == "WAITING_FOR_GUESS":
        buttonWidth = 70
        spacing = 14
        totalWidth = 7 * buttonWidth + 6 * spacing
        startX = WIDTH // 2 - totalWidth // 2
        for number in range(2, 9):
            rect = pygame.Rect(
                startX + (number - 2) * (buttonWidth + spacing),
                HEIGHT // 2 - 20,
                buttonWidth,
                70,
            )
            color = GAME_YELLOW if rect.collidepoint(mousePos) else GAME_PURPLE
            pygame.draw.rect(WIN, color, rect, border_radius=10)
            pygame.draw.rect(WIN, GAME_PINK, rect, 2, border_radius=10)
            _center_text(str(number), TEXT_FONT, GAME_TEXT, rect.center)
            numberButtons.append((number, rect))

    prompts = {
        "WAITING_FOR_CARD": ("Choose a card", GAME_GREEN),
        "WAITING_FOR_TARGET": ("Choose a player", GAME_ORANGE),
        "WAITING_FOR_GUESS": ("Guess the AI card (2-8)", GAME_CYAN),
        "AI_TURN": ("AI is thinking...", GAME_TEXT),
    }
    prompt, color = prompts.get(view.gameState, ("Waiting...", GAME_TEXT))
    _center_text(prompt, TEXT_FONT, color, (WIDTH // 2, HEIGHT - 30))

    hint = SMALL_FONT.render("ESC: leave room", True, GAME_MUTED)
    WIN.blit(hint, (20, HEIGHT - 30))
    pygame.display.update()
    return cardRects, playerRects, numberButtons, discardButtons


class GameEndScreen:
    def __init__(self):
        self.playAgainButton = Button((WIDTH // 2 - 285, 770, 250, 66), "PLAY AGAIN")
        self.menuButton = Button((WIDTH // 2 + 35, 770, 250, 66), "MAIN MENU")

    def handle_event(self, event):
        if self.playAgainButton.handle_event(event):
            return "play_again"
        if self.menuButton.handle_event(event):
            return "menu"
        return None

    def draw(self, view):
        WIN.fill(GAME_BACKGROUND)
        for index in range(24):
            x = (index * 83 + 41) % WIDTH
            y = (index * 137 + 79) % HEIGHT
            pygame.draw.circle(WIN, GAME_YELLOW, (x, y), 2 + index % 3)

        _center_text("ROUND COMPLETE", SMALL_FONT, GAME_CYAN, (WIDTH // 2, 125))
        _center_text("WINNER!", TITLE_FONT, GAME_YELLOW, (WIDTH // 2, 205))
        winnerText = " & ".join(view.winners) if view.winners else "No winner"
        winnerSurface = HEADING_FONT.render(winnerText, True, GAME_PINK)
        winnerRect = winnerSurface.get_rect(center=(WIDTH // 2, 292))
        WIN.blit(winnerSurface, winnerRect)
        if CROWN_IMAGE is not None:
            WIN.blit(CROWN_IMAGE, (winnerRect.left - 68, winnerRect.centery - 27))
            WIN.blit(CROWN_IMAGE, (winnerRect.right + 14, winnerRect.centery - 27))
        _center_text(
            f"ROOM  {view.roomCode}", TINY_FONT, GAME_MUTED, (WIDTH // 2, 340)
        )

        scorePanel = pygame.Rect(WIDTH // 2 - 285, 385, 570, 310)
        pygame.draw.rect(WIN, GAME_SHADOW, scorePanel.move(6, 6), border_radius=14)
        pygame.draw.rect(WIN, GAME_PANEL, scorePanel, border_radius=14)
        pygame.draw.rect(WIN, GAME_PINK, scorePanel, 4, border_radius=14)
        _center_text("FINAL SCORES", TEXT_FONT, GAME_CYAN, (WIDTH // 2, 425))
        for index, (name, tokens) in enumerate(zip(view.names, view.tokens)):
            rowY = 480 + index * 48
            color = GAME_YELLOW if name in view.winners else GAME_TEXT
            scoreText = SMALL_FONT.render(
                f"{name}: {tokens} token{'s' if tokens != 1 else ''}", True, color
            )
            WIN.blit(scoreText, scoreText.get_rect(center=(WIDTH // 2, rowY)))

        self.playAgainButton.draw()
        self.menuButton.draw()
        pygame.display.update()
