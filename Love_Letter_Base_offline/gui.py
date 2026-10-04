import math
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
GAME_LOG_RECT = pygame.Rect(20, HEIGHT - 300, 260, 260)
END_GAME_LOG_RECT = pygame.Rect(500, 385, 420, 310)
PLAYER_POSITIONS = [
    (WIDTH // 2 - 100, 650),
    (WIDTH - 250, 380),
    (WIDTH // 2 - 100, 195),
    (50, 380),
]

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


def _wrap_text(text, font, maxWidth):
    lines = []
    currentLine = ""
    for word in text.split():
        candidate = f"{currentLine} {word}".strip()
        if currentLine and font.size(candidate)[0] > maxWidth:
            lines.append(currentLine)
            currentLine = word
        else:
            currentLine = candidate
    lines.append(currentLine or " ")
    return lines


class GameLog:
    def __init__(self, rect):
        self.rect = pygame.Rect(rect)
        self.scrollOffset = 0
        self.lineCount = 0

    def reset(self):
        self.scrollOffset = 0
        self.lineCount = 0

    def _lines(self, notifications):
        maxWidth = self.rect.width - 38
        lines = []
        for notification in notifications:
            lines.extend(_wrap_text(notification, TINY_FONT, maxWidth))
        return lines

    def handle_event(self, event, notifications, mousePos):
        if event.type != pygame.MOUSEWHEEL or not self.rect.collidepoint(mousePos):
            return
        lines = self._lines(notifications)
        visibleLines = max(1, (self.rect.height - 31) // 18)
        maxOffset = max(0, len(lines) - visibleLines)
        self.scrollOffset = max(
            0, min(maxOffset, self.scrollOffset + event.y * 3)
        )

    def draw(self, notifications):
        pygame.draw.rect(WIN, GAME_SHADOW, self.rect.move(4, 4), border_radius=10)
        pygame.draw.rect(WIN, GAME_PANEL, self.rect, border_radius=10)
        pygame.draw.rect(WIN, GAME_CYAN, self.rect, 2, border_radius=10)

        title = TINY_FONT.render("GAME LOG", True, GAME_CYAN)
        WIN.blit(title, (self.rect.x + 12, self.rect.y + 8))

        lines = self._lines(notifications)
        if self.scrollOffset and len(lines) > self.lineCount:
            self.scrollOffset += len(lines) - self.lineCount
        self.lineCount = len(lines)

        visibleLines = max(1, (self.rect.height - 31) // 18)
        maxOffset = max(0, len(lines) - visibleLines)
        self.scrollOffset = max(0, min(maxOffset, self.scrollOffset))
        endIndex = len(lines) - self.scrollOffset
        startIndex = max(0, endIndex - visibleLines)
        for lineIndex, text in enumerate(lines[startIndex:endIndex]):
            rendered = TINY_FONT.render(text, True, GAME_TEXT)
            WIN.blit(
                rendered,
                (self.rect.x + 12, self.rect.y + 29 + lineIndex * 18),
            )

        if maxOffset:
            track = pygame.Rect(self.rect.right - 13, self.rect.y + 29, 5, self.rect.height - 38)
            pygame.draw.rect(WIN, GAME_MUTED, track, border_radius=3)
            thumbHeight = max(12, track.height * visibleLines // len(lines))
            thumbTravel = track.height - thumbHeight
            thumbY = track.y + thumbTravel * (maxOffset - self.scrollOffset) // maxOffset
            pygame.draw.rect(
                WIN,
                GAME_CYAN,
                (track.x, thumbY, track.width, thumbHeight),
                border_radius=3,
            )


class GameEffects:
    DURATIONS = {"SLOW": 1050, "NORMAL": 760, "FAST": 380}
    DURATION_MULTIPLIERS = {
        "Guard": 1.25,
        "Priest": 1.8,
        "Baron": 1.8,
        "Prince": 1.85,
        "King": 1.8,
        "Princess": 1.4,
    }

    def __init__(self):
        self.active = None
        self.startedAt = 0
        self.durationMs = self.DURATIONS["NORMAL"]
        self.queue = []

    def reset(self):
        self.active = None
        self.startedAt = 0
        self.durationMs = self.DURATIONS["NORMAL"]
        self.queue = []

    def trigger(self, event, speed="NORMAL"):
        baseDuration = self.DURATIONS.get(speed, self.DURATIONS["NORMAL"])
        multiplier = self.DURATION_MULTIPLIERS.get(event["cardName"], 1.0)
        queuedEvent = (event, int(baseDuration * multiplier))
        if self.active is None:
            self.active, self.durationMs = queuedEvent
            self.startedAt = pygame.time.get_ticks()
        else:
            self.queue.append(queuedEvent)

    def _advance(self):
        if self.active is None:
            return
        if pygame.time.get_ticks() - self.startedAt < self.durationMs:
            return
        if self.queue:
            self.active, self.durationMs = self.queue.pop(0)
            self.startedAt = pygame.time.get_ticks()
        else:
            self.active = None

    def isBusy(self):
        self._advance()
        return self.active is not None

    def currentCardName(self):
        self._advance()
        return self.active["cardName"] if self.active is not None else None

    def _progress(self):
        if self.active is None:
            return 1.0
        return min(
            1.0,
            (pygame.time.get_ticks() - self.startedAt) / self.durationMs,
        )

    def playerOffset(self, playerIndex):
        self._advance()
        if self.active is None or self.active.get("impactIndex") != playerIndex:
            return 0, 0
        progress = self._progress()
        if progress < 0.38 or progress > 0.92:
            return 0, 0
        strength = 1.0 - abs(progress - 0.65) / 0.27
        offset = int(math.sin(progress * 85) * 10 * strength)
        return offset, 0

    def targetFlash(self, playerIndex):
        self._advance()
        if self.active is None or self.active.get("impactIndex") != playerIndex:
            return None
        progress = self._progress()
        if not 0.32 <= progress <= 0.9:
            return None
        pulse = int(100 + 155 * abs(math.sin(progress * 28)))
        if self.active.get("knockedOut"):
            return (*GAME_RED, pulse)
        return (*GAME_YELLOW, pulse)

    def _playerCenter(self, playerIndex):
        return pygame.Rect(*PLAYER_POSITIONS[playerIndex], 200, 180).center

    def _lerp(self, start, end, progress):
        eased = 1 - (1 - max(0.0, min(1.0, progress))) ** 3
        return (
            start[0] + (end[0] - start[0]) * eased,
            start[1] + (end[1] - start[1]) * eased,
        )

    def _drawCard(self, cardName, center, scale=1.0, alpha=255, angle=0):
        image = CARD_IMAGES.get(cardName, CARD_IMAGES["Back"])
        transformed = pygame.transform.rotozoom(image, angle, scale)
        transformed.set_alpha(max(0, min(255, alpha)))
        rect = transformed.get_rect(center=(int(center[0]), int(center[1])))
        WIN.blit(transformed, rect)
        border = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            border,
            (*GAME_PINK, max(0, min(255, alpha))),
            border.get_rect(),
            3,
            border_radius=10,
        )
        WIN.blit(border, rect)
        return rect

    def _drawKnockout(self, progress):
        if not self.active.get("knockedOut") or progress < 0.5:
            return
        fadeIn = min(1.0, (progress - 0.5) / 0.16)
        for playerIndex in self.active.get("knockedOutIndexes", []):
            center = self._playerCenter(playerIndex)
            radius = int(48 + 20 * fadeIn)
            overlay = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                overlay,
                (*GAME_RED, int(185 * fadeIn)),
                (radius, radius),
                radius,
            )
            lineWidth = max(3, int(8 * fadeIn))
            pygame.draw.line(
                overlay,
                (*GAME_TEXT, int(255 * fadeIn)),
                (radius - 25, radius - 25),
                (radius + 25, radius + 25),
                lineWidth,
            )
            pygame.draw.line(
                overlay,
                (*GAME_TEXT, int(255 * fadeIn)),
                (radius + 25, radius - 25),
                (radius - 25, radius + 25),
                lineWidth,
            )
            WIN.blit(overlay, overlay.get_rect(center=center))
            label = TEXT_FONT.render("KNOCKED OUT", True, GAME_RED)
            label.set_alpha(int(255 * fadeIn))
            WIN.blit(label, label.get_rect(center=(center[0], center[1] + 112)))

    def _drawGuard(self, progress, destination):
        guess = self.active.get("guess")
        if guess is None or progress < 0.36:
            return
        reveal = min(1.0, (progress - 0.36) / 0.16)
        radius = int(28 + 16 * reveal)
        badge = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(badge, (*GAME_YELLOW, 235), (radius, radius), radius)
        pygame.draw.circle(badge, GAME_PINK, (radius, radius), radius, 4)
        number = HEADING_FONT.render(str(guess), True, GAME_BACKGROUND)
        badge.blit(number, number.get_rect(center=(radius, radius)))
        WIN.blit(
            badge,
            badge.get_rect(center=(destination[0], destination[1] - 125)),
        )
        _center_text(
            f"GUESS: {guess}",
            SMALL_FONT,
            GAME_YELLOW,
            (destination[0], destination[1] - 176),
        )

    def _drawHandReveal(self, progress, destination):
        revealCard = self.active.get("revealCard")
        if revealCard is None or progress < 0.38:
            return
        flip = min(1.0, (progress - 0.38) / 0.48)
        imageName = "Back" if flip < 0.5 else revealCard
        widthScale = max(0.04, abs(1 - flip * 2))
        image = pygame.transform.smoothscale(
            CARD_IMAGES[imageName],
            (max(2, int(CARD_WIDTH * widthScale)), CARD_HEIGHT),
        )
        rect = image.get_rect(center=destination)
        WIN.blit(image, rect)
        pygame.draw.rect(WIN, GAME_CYAN, rect, 4, border_radius=10)
        if flip >= 0.5:
            _center_text(
                f"REVEALED: {revealCard.upper()}",
                SMALL_FONT,
                GAME_CYAN,
                (destination[0], destination[1] - 112),
            )

    def _drawBaron(self, progress):
        if not self.active.get("showComparison") or progress < 0.32:
            return
        actorValue = self.active.get("actorValue")
        targetValue = self.active.get("targetValue")
        if actorValue is None or targetValue is None:
            return

        reveal = min(1.0, (progress - 0.32) / 0.22)
        alpha = int(245 * reveal)
        panel = pygame.Surface((540, 300), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (*GAME_BACKGROUND, alpha),
            panel.get_rect(),
            border_radius=18,
        )
        pygame.draw.rect(
            panel,
            (*GAME_CYAN, alpha),
            panel.get_rect(),
            4,
            border_radius=18,
        )
        WIN.blit(panel, panel.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        cardScale = 0.55 + 0.15 * reveal
        self._drawCard(
            self.active.get("heldCard") or "Back",
            (WIDTH // 2 - 175, HEIGHT // 2),
            cardScale,
            alpha,
            -5 * (1 - reveal),
        )
        self._drawCard(
            self.active.get("targetCard") or "Back",
            (WIDTH // 2 + 175, HEIGHT // 2),
            cardScale,
            alpha,
            5 * (1 - reveal),
        )
        _center_text(
            "HAND COMPARISON",
            SMALL_FONT,
            GAME_CYAN,
            (WIDTH // 2, HEIGHT // 2 - 118),
        )

        if progress < 0.5:
            return
        if actorValue < targetValue:
            operator = "<"
        elif actorValue > targetValue:
            operator = ">"
        else:
            operator = "="
        humanValue = (
            actorValue if self.active["actorIndex"] == 0 else targetValue
        )
        opponentValue = (
            targetValue if self.active["actorIndex"] == 0 else actorValue
        )
        if humanValue > opponentValue:
            operatorColor = GAME_GREEN
        elif humanValue < opponentValue:
            operatorColor = GAME_RED
        else:
            operatorColor = GAME_YELLOW
        expression = HEADING_FONT.render(
            f"{actorValue} {operator} {targetValue}", True, operatorColor
        )
        expression.set_alpha(min(255, int((progress - 0.5) / 0.14 * 255)))
        WIN.blit(expression, expression.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

        actorLabel = "YOUR HAND" if self.active["actorIndex"] == 0 else "OPPONENT"
        targetLabel = "YOUR HAND" if self.active.get("targetIndex") == 0 else "OPPONENT"
        _center_text(
            actorLabel,
            TINY_FONT,
            GAME_TEXT,
            (WIDTH // 2 - 175, HEIGHT // 2 + 112),
        )
        _center_text(
            targetLabel,
            TINY_FONT,
            GAME_TEXT,
            (WIDTH // 2 + 175, HEIGHT // 2 + 112),
        )

    def _drawPrince(self, progress, destination):
        discardedCard = self.active.get("discardedCard")
        if discardedCard is not None and progress >= 0.34:
            discardProgress = min(1.0, (progress - 0.34) / 0.34)
            discardCenter = (
                destination[0] + discardProgress * 85,
                destination[1] + discardProgress * 120,
            )
            self._drawCard(
                discardedCard,
                discardCenter,
                0.72,
                int(255 * (1 - discardProgress)),
                -35 * discardProgress,
            )

        drawnCard = self.active.get("drawnCard")
        if drawnCard is not None and progress >= 0.56:
            drawProgress = min(1.0, (progress - 0.56) / 0.35)
            drawCenter = self._lerp((WIDTH // 2, 525), destination, drawProgress)
            visibleCard = drawnCard if self.active.get("targetIndex") == 0 else "Back"
            self._drawCard(visibleCard, drawCenter, 0.72, 255, 8 * (1 - drawProgress))
            _center_text(
                "DRAW NEW CARD",
                SMALL_FONT,
                GAME_CYAN,
                (destination[0], destination[1] - 112),
            )

    def _drawKing(self, progress, actorCenter, destination):
        if progress < 0.4:
            return
        swapProgress = min(1.0, (progress - 0.4) / 0.46)
        showFaces = self.active.get("showSwapFaces")
        actorCard = self.active.get("heldCard") if showFaces else "Back"
        targetCard = self.active.get("targetCard") if showFaces else "Back"
        actorToTarget = self._lerp(actorCenter, destination, swapProgress)
        targetToActor = self._lerp(destination, actorCenter, swapProgress)
        arc = math.sin(swapProgress * math.pi) * 72
        self._drawCard(
            actorCard or "Back",
            (actorToTarget[0], actorToTarget[1] - arc),
            0.62,
            255,
            15 * (1 - swapProgress),
        )
        self._drawCard(
            targetCard or "Back",
            (targetToActor[0], targetToActor[1] + arc),
            0.62,
            255,
            -15 * (1 - swapProgress),
        )
        _center_text("SWAP", TEXT_FONT, GAME_YELLOW, (WIDTH // 2, HEIGHT // 2))

    def draw(self):
        if not self.isBusy():
            return

        progress = self._progress()
        actorIndex = self.active["actorIndex"]
        targetIndex = self.active.get("targetIndex")
        actorCenter = self._playerCenter(actorIndex)
        destination = (
            self._playerCenter(targetIndex)
            if targetIndex is not None
            else (WIDTH // 2, HEIGHT // 2)
        )

        travelProgress = min(1.0, progress / 0.34)
        cardCenter = self._lerp(actorCenter, destination, travelProgress)
        if progress < 0.7:
            alpha = 255
        else:
            alpha = int(255 * (1 - (progress - 0.7) / 0.3))
        scale = 0.72 + 0.35 * min(1.0, travelProgress)
        angle = (1 - travelProgress) * 14 * (-1 if actorIndex % 2 else 1)
        cardRect = self._drawCard(
            self.active["cardName"], cardCenter, scale, alpha, angle
        )

        label = TEXT_FONT.render(self.active["cardName"].upper(), True, GAME_YELLOW)
        label.set_alpha(max(0, alpha))
        WIN.blit(label, label.get_rect(center=(cardRect.centerx, cardRect.bottom + 24)))

        cardName = self.active["cardName"]
        if cardName == "Guard":
            self._drawGuard(progress, destination)
        elif cardName == "Priest":
            self._drawHandReveal(progress, destination)
        elif cardName == "Baron":
            self._drawBaron(progress)
        elif cardName == "Prince":
            self._drawPrince(progress, destination)
        elif cardName == "King" and targetIndex is not None:
            self._drawKing(progress, actorCenter, destination)

        self._drawKnockout(progress)


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
            wasActive = self.active
            self.active = self.rect.collidepoint(event.pos)
            if self.active:
                pygame.key.start_text_input()
            elif wasActive:
                pygame.key.stop_text_input()
            return False
        if not self.active:
            return False
        if event.type == pygame.TEXTINPUT:
            value = event.text.upper() if self.uppercase else event.text
            self.text = (self.text + value)[: self.max_length]
            return False
        if event.type != pygame.KEYDOWN:
            return False
        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return True
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
    selectedCardIndex: int
    winners: list[str]
    discardPiles: list[list[tuple[str, int]]]
    finalHands: list[list[str]]
    notifications: list[str]


def draw_game_screen(
    view,
    mousePos,
    validTargets,
    gameLog,
    aiPaused,
    aiSpeed,
    gameEffects,
    viewingDiscardIndex=None,
):
    WIN.fill(GAME_BACKGROUND)
    cardRects = []
    playerRects = []
    numberButtons = []
    discardButtons = []
    aiControlButtons = []

    pygame.draw.rect(WIN, GAME_SHADOW, (0, 4, WIDTH, 90))
    pygame.draw.rect(WIN, GAME_PANEL, (0, 0, WIDTH, 88))
    pygame.draw.line(WIN, GAME_PINK, (0, 87), (WIDTH, 87), 4)
    title = HEADING_FONT.render("Love Letter", True, GAME_PINK)
    WIN.blit(title, (25, 19))
    room = SMALL_FONT.render(f"ROOM  {view.roomCode}", True, GAME_CYAN)
    WIN.blit(room, room.get_rect(center=(WIDTH // 2, 44)))
    deck = TEXT_FONT.render(f"Deck: {view.remainingCards}", True, GAME_CYAN)
    WIN.blit(deck, (WIDTH - deck.get_width() - 30, 29))

    gameLog.draw(view.notifications)

    pauseRect = pygame.Rect(770, 105, 200, 34)
    pauseColor = GAME_GREEN if aiPaused else GAME_PURPLE
    pygame.draw.rect(WIN, pauseColor, pauseRect, border_radius=8)
    pygame.draw.rect(WIN, GAME_PINK, pauseRect, 2, border_radius=8)
    _center_text(
        "RESUME AI" if aiPaused else "PAUSE AI",
        TINY_FONT,
        GAME_TEXT,
        pauseRect.center,
    )
    aiControlButtons.append(("pause", None, pauseRect))

    for index, speed in enumerate(("SLOW", "NORMAL", "FAST")):
        speedRect = pygame.Rect(770 + index * 68, 148, 64, 30)
        speedColor = GAME_CYAN if speed == aiSpeed else GAME_PANEL
        pygame.draw.rect(WIN, speedColor, speedRect, border_radius=7)
        pygame.draw.rect(WIN, GAME_PINK, speedRect, 2, border_radius=7)
        _center_text(
            speed,
            TINY_FONT,
            GAME_BACKGROUND if speed == aiSpeed else GAME_TEXT,
            speedRect.center,
        )
        aiControlButtons.append(("speed", speed, speedRect))

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

    for index, name in enumerate(view.names[:4]):
        x, y = PLAYER_POSITIONS[index]
        offsetX, offsetY = gameEffects.playerOffset(index)
        x += offsetX
        y += offsetY
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

        if status == "Protected":
            pulse = (math.sin(pygame.time.get_ticks() / 180) + 1) / 2
            for ring in range(3):
                shieldSize = 16 + ring * 10 + pulse * 5
                shieldRect = rect.inflate(shieldSize, shieldSize)
                shieldColor = (
                    min(255, GAME_CYAN[0] + ring * 15),
                    min(255, GAME_CYAN[1] + ring * 5),
                    255,
                )
                pygame.draw.ellipse(WIN, shieldColor, shieldRect, 3)

        pygame.draw.rect(WIN, GAME_SHADOW, rect.move(5, 5), border_radius=10)
        pygame.draw.rect(WIN, fill, rect, border_radius=13)
        pygame.draw.rect(
            WIN,
            border,
            rect,
            5 if isTarget and rect.collidepoint(mousePos) else 3,
            13,
        )
        flashColor = gameEffects.targetFlash(index)
        if flashColor is not None:
            flash = pygame.Surface(rect.size, pygame.SRCALPHA)
            flash.fill(flashColor)
            WIN.blit(flash, rect)
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
                hoverRect = cardRect.inflate(22, 38).move(0, -10)
                if (
                    hoverRect.collidepoint(mousePos)
                    and view.gameState == "WAITING_FOR_CARD"
                    and not gameEffects.isBusy()
                ):
                    hovered = True
                else:
                    hovered = False
                selected = cardIndex == view.selectedCardIndex
                lift = 18 if hovered else 10 if selected else 0
                scale = 1.08 if hovered else 1.04 if selected else 1.0
                angle = (
                    max(-7, min(7, (mousePos[0] - cardRect.centerx) / 10))
                    if hovered
                    else 0
                )
                image = CARD_IMAGES.get(cardName, CARD_IMAGES["Back"])
                transformed = pygame.transform.rotozoom(image, -angle, scale)
                displayRect = transformed.get_rect(
                    center=(cardRect.centerx, cardRect.centery - lift)
                )
                cardRects.append(displayRect)
                pygame.draw.rect(
                    WIN,
                    GAME_SHADOW,
                    displayRect.move(5, 6),
                    border_radius=12,
                )
                if hovered or selected:
                    glowSize = 8 + int(
                        3 * (math.sin(pygame.time.get_ticks() / 120) + 1)
                    )
                    pygame.draw.rect(
                        WIN,
                        GAME_YELLOW,
                        displayRect.inflate(glowSize, glowSize),
                        4,
                        14,
                    )
                WIN.blit(transformed, displayRect)
                pygame.draw.rect(WIN, GAME_PINK, displayRect, 3, 10)
                caption = TINY_FONT.render(cardName, True, GAME_CYAN)
                captionRect = caption.get_rect(
                    center=(displayRect.centerx, displayRect.bottom + 12)
                )
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
        "AI_TURN": (
            "AI paused" if aiPaused else "AI is thinking...",
            GAME_ORANGE if aiPaused else GAME_TEXT,
        ),
    }
    activeCardName = gameEffects.currentCardName()
    if activeCardName is not None:
        prompt, color = (f"{activeCardName} played!", GAME_YELLOW)
    else:
        prompt, color = prompts.get(view.gameState, ("Waiting...", GAME_TEXT))
    _center_text(prompt, TEXT_FONT, color, (WIDTH // 2, HEIGHT - 30))

    hint = SMALL_FONT.render("ESC: leave room", True, GAME_MUTED)
    WIN.blit(hint, (20, HEIGHT - 30))
    gameEffects.draw()
    pygame.display.update()
    return cardRects, playerRects, numberButtons, discardButtons, aiControlButtons


class GameEndScreen:
    def __init__(self):
        self.playAgainButton = Button((WIDTH // 2 - 285, 770, 250, 66), "PLAY AGAIN")
        self.menuButton = Button((WIDTH // 2 + 35, 770, 250, 66), "MAIN MENU")
        self.gameLog = GameLog(END_GAME_LOG_RECT)
        self.startedAt = None

    def handle_event(self, event, view, mousePos):
        self.gameLog.handle_event(event, view.notifications, mousePos)
        if self.playAgainButton.handle_event(event):
            return "play_again"
        if self.menuButton.handle_event(event):
            return "menu"
        return None

    def reset(self):
        self.gameLog.reset()
        self.startedAt = None

    def start(self, view):
        self.gameLog.reset()
        self.startedAt = pygame.time.get_ticks()

    def draw(self, view):
        if self.startedAt is None:
            self.start(view)
        elapsed = pygame.time.get_ticks() - self.startedAt
        revealStart = 350
        revealInterval = 400
        revealDuration = 300
        tokenStart = revealStart + len(view.names) * revealInterval + 300
        tokenDuration = 750

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

        scorePanel = pygame.Rect(80, 385, 390, 310)
        pygame.draw.rect(WIN, GAME_SHADOW, scorePanel.move(6, 6), border_radius=14)
        pygame.draw.rect(WIN, GAME_PANEL, scorePanel, border_radius=14)
        pygame.draw.rect(WIN, GAME_PINK, scorePanel, 4, border_radius=14)
        _center_text("FINAL SCORES", TEXT_FONT, GAME_CYAN, (scorePanel.centerx, 425))
        for index, (name, tokens) in enumerate(zip(view.names, view.tokens)):
            rowY = 468 + index * 53
            color = GAME_YELLOW if name in view.winners else GAME_TEXT
            tokenDelay = tokenStart + index * 120
            tokenAwarded = elapsed >= tokenDelay + tokenDuration
            displayedTokens = (
                tokens - 1
                if name in view.winners and not tokenAwarded and tokens > 0
                else tokens
            )
            scoreText = SMALL_FONT.render(
                f"{name}: {displayedTokens} token{'s' if displayedTokens != 1 else ''}",
                True,
                color,
            )
            WIN.blit(
                scoreText,
                scoreText.get_rect(center=(scorePanel.x + 160, rowY)),
            )

            hand = view.finalHands[index][0] if view.finalHands[index] else None
            if hand is None and view.discardPiles[index]:
                hand = view.discardPiles[index][-1][0]
            playerRevealAt = revealStart + index * revealInterval
            revealProgress = max(
                0.0,
                min(1.0, (elapsed - playerRevealAt) / revealDuration),
            )
            if revealProgress < 0.5:
                cardImage = CARD_IMAGES["Back"]
            else:
                cardImage = CARD_IMAGES.get(hand, CARD_IMAGES["Back"])
            flipWidth = max(2, int(38 * abs(1 - revealProgress * 2)))
            miniCard = pygame.transform.smoothscale(cardImage, (flipWidth, 53))
            miniRect = miniCard.get_rect(center=(scorePanel.right - 45, rowY + 4))
            WIN.blit(miniCard, miniRect)
            pygame.draw.rect(WIN, GAME_PINK, miniRect, 2, border_radius=4)

            handLabel = hand if revealProgress >= 1 and hand else "Hidden"
            handText = TINY_FONT.render(f"Final: {handLabel}", True, GAME_MUTED)
            WIN.blit(
                handText,
                handText.get_rect(center=(scorePanel.x + 160, rowY + 21)),
            )

            if name in view.winners and tokenDelay <= elapsed < tokenDelay + tokenDuration:
                progress = (elapsed - tokenDelay) / tokenDuration
                eased = 1 - (1 - progress) ** 3
                startX, startY = WIDTH // 2, 315
                endX, endY = scorePanel.x + 32, rowY
                tokenX = int(startX + (endX - startX) * eased)
                tokenY = int(
                    startY
                    + (endY - startY) * eased
                    - math.sin(progress * math.pi) * 80
                )
                radius = 18 + int(math.sin(progress * math.pi) * 5)
                pygame.draw.circle(WIN, GAME_SHADOW, (tokenX + 3, tokenY + 4), radius)
                pygame.draw.circle(WIN, GAME_YELLOW, (tokenX, tokenY), radius)
                pygame.draw.circle(WIN, GOLD, (tokenX, tokenY), radius, 4)
                _center_text("T", SMALL_FONT, GAME_BACKGROUND, (tokenX, tokenY))

        self.gameLog.draw(view.notifications)

        self.playAgainButton.draw()
        self.menuButton.draw()
        pygame.display.update()
