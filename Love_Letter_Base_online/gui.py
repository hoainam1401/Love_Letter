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
pygame.display.set_caption("Love Letter - Online")

TITLE_FONT = pygame.font.Font(None, 112)
HEADING_FONT = pygame.font.Font(None, 56)
BUTTON_FONT = pygame.font.Font(None, 38)
TEXT_FONT = pygame.font.Font(None, 34)
SMALL_FONT = pygame.font.Font(None, 25)
TINY_FONT = pygame.font.Font(None, 20)


def _load_card_images():
    images = {}
    image_dir = os.path.join(os.path.dirname(__file__), "images")
    card_names = [
        "Guard",
        "Priest",
        "Baron",
        "Handmaid",
        "Prince",
        "King",
        "Countess",
        "Princess",
    ]

    for name in card_names + ["Back"]:
        path = os.path.join(image_dir, f"{name}.png")
        if os.path.exists(path):
            image = pygame.image.load(path)
            images[name] = pygame.transform.smoothscale(
                image, (CARD_WIDTH, CARD_HEIGHT)
            )
            continue

        placeholder = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        placeholder.fill(PANEL_DARK if name == "Back" else PANEL)
        pygame.draw.rect(placeholder, ROSE, placeholder.get_rect(), 3, 10)
        label = SMALL_FONT.render(name, True, WHITE if name == "Back" else INK)
        placeholder.blit(label, label.get_rect(center=placeholder.get_rect().center))
        images[name] = placeholder

    return images


CARD_IMAGES = _load_card_images()
SMALL_CARD_BACK = pygame.transform.smoothscale(CARD_IMAGES["Back"], (96, 134))

_crown_path = os.path.join(os.path.dirname(__file__), "images", "crown.png")
CROWN_IMAGE = (
    pygame.transform.smoothscale(pygame.image.load(_crown_path), (54, 54))
    if os.path.exists(_crown_path)
    else None
)


def _draw_shadowed_panel(rect, radius=18, shadow_offset=8):
    shadow_rect = rect.move(shadow_offset, shadow_offset)
    pygame.draw.rect(WIN, (205, 192, 183), shadow_rect, border_radius=radius)
    pygame.draw.rect(WIN, PANEL, rect, border_radius=radius)
    pygame.draw.rect(WIN, ROSE_LIGHT, rect, 2, border_radius=radius)


def _draw_centered(text, font, color, center):
    surface = font.render(text, True, color)
    WIN.blit(surface, surface.get_rect(center=center))


class Button:
    def __init__(self, rect, text, *, enabled=True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.enabled = enabled
        self.hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        return (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

    def draw(self):
        shadow_rect = self.rect.move(0, 5)
        pygame.draw.rect(WIN, ROSE_DARK, shadow_rect, border_radius=12)

        if not self.enabled:
            color = (174, 161, 166)
        elif self.hovered:
            color = (190, 67, 92)
        else:
            color = ROSE

        pygame.draw.rect(WIN, color, self.rect, border_radius=12)
        pygame.draw.rect(WIN, ROSE_DARK, self.rect, 2, border_radius=12)
        _draw_centered(self.text, BUTTON_FONT, WHITE, self.rect.center)


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

        if event.type == pygame.KEYDOWN:
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
        clip_rect = self.rect.inflate(-28, -8)
        previous_clip = WIN.get_clip()
        WIN.set_clip(clip_rect)
        WIN.blit(rendered, (self.rect.x + 18, self.rect.centery - rendered.get_height() // 2))
        WIN.set_clip(previous_clip)

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
        self.room_code = TextInput(
            (field_x, 510, field_width, 68),
            "Room code",
            max_length=12,
            uppercase=True,
        )
        self.login_button = Button((WIDTH // 2 - 135, 625, 270, 66), "ENTER ROOM")

    def handle_event(self, event):
        submit = self.username.handle_event(event)
        submit = self.room_code.handle_event(event) or submit
        submit = self.login_button.handle_event(event) or submit
        if not submit:
            return None
        return self.username.text.strip(), self.room_code.text.strip().upper()

    def draw(self, message="", busy=False):
        WIN.fill(BACKGROUND)

        for x, y, radius in ((120, 135, 90), (870, 170, 120), (120, 850, 130)):
            pygame.draw.circle(WIN, (239, 219, 213), (x, y), radius)
            pygame.draw.circle(WIN, ROSE_LIGHT, (x, y), radius, 2)

        panel = pygame.Rect(WIDTH // 2 - 305, 105, 610, 680)
        _draw_shadowed_panel(panel, 26, 10)

        pygame.draw.line(WIN, GOLD, (385, 245), (615, 245), 3)
        _draw_centered("LOVE", TITLE_FONT, ROSE_DARK, (WIDTH // 2, 177))
        _draw_centered("LETTER", HEADING_FONT, GOLD, (WIDTH // 2, 225))
        _draw_centered(
            "A private table is one code away",
            SMALL_FONT,
            MUTED,
            (WIDTH // 2, 292),
        )

        _draw_centered("PLAYER NAME", TINY_FONT, MUTED, (WIDTH // 2, 390))
        _draw_centered("ROOM CODE", TINY_FONT, MUTED, (WIDTH // 2, 490))
        self.username.draw()
        self.room_code.draw()

        self.login_button.enabled = not busy
        self.login_button.text = "CONNECTING..." if busy else "ENTER ROOM"
        self.login_button.draw()

        if message:
            color = RED if not busy else MUTED
            _draw_centered(message, SMALL_FONT, color, (WIDTH // 2, 735))

        pygame.display.update()


class LobbyScreen:
    def __init__(self):
        self.start_button = Button((WIDTH // 2 - 135, 715, 270, 66), "START GAME")
        self.leave_button = Button((40, 40, 125, 48), "LEAVE")

    def handle_event(self, event, can_start):
        self.start_button.enabled = can_start
        if self.start_button.handle_event(event):
            return "start"
        if self.leave_button.handle_event(event):
            return "leave"
        return None

    def draw(self, room_code, players, can_start, message=""):
        WIN.fill(BACKGROUND)
        self.leave_button.draw()

        _draw_centered("THE WAITING ROOM", HEADING_FONT, ROSE_DARK, (WIDTH // 2, 125))
        _draw_centered("ROOM CODE", TINY_FONT, MUTED, (WIDTH // 2, 190))

        code_rect = pygame.Rect(WIDTH // 2 - 145, 215, 290, 70)
        pygame.draw.rect(WIN, PANEL_DARK, code_rect, border_radius=12)
        _draw_centered(room_code, HEADING_FONT, WHITE, code_rect.center)

        panel = pygame.Rect(WIDTH // 2 - 300, 340, 600, 315)
        _draw_shadowed_panel(panel)
        _draw_centered(
            f"PLAYERS  {len(players)}/4", SMALL_FONT, MUTED, (WIDTH // 2, 380)
        )

        for index in range(4):
            row = pygame.Rect(panel.x + 42, panel.y + 72 + index * 56, panel.width - 84, 44)
            if index < len(players):
                pygame.draw.rect(WIN, (249, 236, 231), row, border_radius=9)
                marker = pygame.Rect(row.x + 12, row.y + 10, 24, 24)
                pygame.draw.circle(WIN, ROSE, marker.center, 12)
                name = players[index]
                if index == 0:
                    name += "  (host)"
                label = SMALL_FONT.render(name, True, INK)
            else:
                pygame.draw.rect(WIN, (239, 233, 227), row, 2, border_radius=9)
                label = SMALL_FONT.render("Waiting for player...", True, MUTED)
            WIN.blit(label, (row.x + 50, row.centery - label.get_height() // 2))

        self.start_button.enabled = can_start
        self.start_button.draw()
        hint = message or (
            "Start when 2-4 players have joined"
            if can_start
            else "Only the host can start with 2-4 players"
        )
        _draw_centered(hint, SMALL_FONT, MUTED, (WIDTH // 2, 820))
        pygame.display.update()


@dataclass(frozen=True)
class GameView:
    room_code: str
    names: list[str]
    statuses: list[str]
    tokens: list[int]
    hand: list[str]
    position: int
    current_player: int
    remaining_cards: int
    game_state: str
    winners: list[str]
    discard_piles: list[list[tuple[str, int]]]


def draw_game_screen(view, mouse_pos, valid_targets, viewing_discard_index=None):
    WIN.fill(GAME_BACKGROUND)
    card_rects = []
    player_rects = []
    number_buttons = []
    discard_buttons = []

    pygame.draw.rect(WIN, GAME_SHADOW, (0, 4, WIDTH, 90))
    pygame.draw.rect(WIN, GAME_PANEL, (0, 0, WIDTH, 88))
    pygame.draw.line(WIN, GAME_PINK, (0, 87), (WIDTH, 87), 4)
    title = HEADING_FONT.render("Love Letter", True, GAME_PINK)
    WIN.blit(title, (25, 19))
    room_text = SMALL_FONT.render(f"ROOM  {view.room_code}", True, GAME_CYAN)
    WIN.blit(room_text, room_text.get_rect(center=(WIDTH // 2, 44)))
    deck_text = TEXT_FONT.render(f"Deck: {view.remaining_cards}", True, GAME_CYAN)
    WIN.blit(deck_text, (WIDTH - deck_text.get_width() - 30, 29))

    deck_x = WIDTH // 2 - CARD_WIDTH // 2
    deck_y = HEIGHT // 2 - CARD_HEIGHT // 2
    if view.remaining_cards > 0:
        for index in range(min(4, view.remaining_cards)):
            offset = index * 4
            pygame.draw.rect(
                WIN,
                GAME_SHADOW,
                (deck_x + offset + 4, deck_y + offset + 4, CARD_WIDTH, CARD_HEIGHT),
                border_radius=10,
            )
            WIN.blit(CARD_IMAGES["Back"], (deck_x + offset, deck_y + offset))
            pygame.draw.rect(
                WIN,
                GAME_PINK,
                (deck_x + offset, deck_y + offset, CARD_WIDTH, CARD_HEIGHT),
                2,
                10,
            )
        _draw_centered("DECK", SMALL_FONT, GAME_PURPLE, (WIDTH // 2, deck_y + 195))

    positions = [
        (WIDTH // 2 - 340, HEIGHT - 300),
        (WIDTH - 250, HEIGHT // 2 - 150),
        (WIDTH // 2 - 100, 115),
        (50, HEIGHT // 2 - 150),
    ]
    for _ in range(max(0, view.position)):
        positions.insert(0, positions.pop())

    player_count = min(len(view.names), len(view.statuses), len(view.tokens), 4)
    for index in range(player_count):
        x, y = positions[index]
        rect = pygame.Rect(x, y, 200, 180)
        is_target = index in valid_targets
        hovered = rect.collidepoint(mouse_pos)

        if view.statuses[index] == "KO":
            fill, border = GAME_RED, GAME_MUTED
        elif index == view.current_player:
            fill, border = GAME_GREEN, GAME_YELLOW
        elif is_target:
            fill, border = GAME_ORANGE, GAME_YELLOW
        else:
            fill, border = GAME_PURPLE, GAME_PINK

        pygame.draw.rect(WIN, GAME_SHADOW, rect.move(5, 5), border_radius=13)
        pygame.draw.rect(WIN, fill, rect, border_radius=13)
        pygame.draw.rect(WIN, border, rect, 5 if hovered and is_target else 3, 13)
        if is_target:
            player_rects.append((index, rect))

        name = TEXT_FONT.render(view.names[index], True, GAME_TEXT)
        WIN.blit(name, name.get_rect(center=(rect.centerx, rect.y + 30)))
        status = view.statuses[index]
        if status == "No Protection":
            status = "Active"
        status_color = (
            GAME_RED
            if view.statuses[index] == "KO"
            else GAME_CYAN
            if view.statuses[index] == "Protected"
            else GAME_GREEN
        )
        status_text = SMALL_FONT.render(status, True, status_color)
        WIN.blit(status_text, status_text.get_rect(center=(rect.centerx, rect.y + 64)))
        token_text = SMALL_FONT.render(
            f"Tokens: {view.tokens[index]}", True, GAME_YELLOW
        )
        WIN.blit(token_text, token_text.get_rect(center=(rect.centerx, rect.y + 94)))

        button_x = rect.right + 8 if rect.x < 100 else rect.x - 58
        discard_rect = pygame.Rect(button_x, rect.y + 10, 50, 50)
        discard_buttons.append((index, discard_rect))
        discard_color = (
            GAME_ORANGE if discard_rect.collidepoint(mouse_pos) else GAME_PURPLE
        )
        pygame.draw.rect(WIN, GAME_SHADOW, discard_rect.move(2, 2), border_radius=8)
        pygame.draw.rect(WIN, discard_color, discard_rect, border_radius=8)
        pygame.draw.rect(WIN, GAME_PINK, discard_rect, 2, border_radius=8)
        _draw_centered(
            str(len(view.discard_piles[index])),
            SMALL_FONT,
            GAME_YELLOW,
            discard_rect.center,
        )

        if view.statuses[index] != "KO" and index != view.position:
            card_x = rect.centerx - SMALL_CARD_BACK.get_width() // 2
            card_y = rect.y + 112
            pygame.draw.rect(
                WIN,
                GAME_SHADOW,
                (card_x + 3, card_y + 3, 96, 134),
                border_radius=8,
            )
            WIN.blit(SMALL_CARD_BACK, (card_x, card_y))

    if view.hand:
        hand_y = HEIGHT - 275
        hand_panel = pygame.Rect(WIDTH // 2 - 165, hand_y - 38, 330, 225)
        pygame.draw.rect(WIN, GAME_SHADOW, hand_panel.move(5, 5), border_radius=14)
        pygame.draw.rect(WIN, GAME_PANEL, hand_panel, border_radius=14)
        pygame.draw.rect(WIN, GAME_PINK, hand_panel, 3, border_radius=14)
        _draw_centered("YOUR HAND", SMALL_FONT, GAME_PINK, (WIDTH // 2, hand_y - 17))

        total_width = len(view.hand) * CARD_WIDTH + (len(view.hand) - 1) * 20
        start_x = WIDTH // 2 - total_width // 2
        for index, card_name in enumerate(view.hand):
            x = start_x + index * (CARD_WIDTH + 20)
            rect = pygame.Rect(x, hand_y + 10, CARD_WIDTH, CARD_HEIGHT)
            card_rects.append(rect)
            hovered = rect.collidepoint(mouse_pos) and view.game_state == "WAITING_FOR_CARD"
            if hovered:
                pygame.draw.rect(WIN, GAME_YELLOW, rect.inflate(10, 10), 4, 13)
            pygame.draw.rect(WIN, GAME_SHADOW, rect.move(4, 4), border_radius=10)
            image = CARD_IMAGES.get(card_name, CARD_IMAGES["Back"])
            WIN.blit(image, rect)
            pygame.draw.rect(WIN, GAME_PINK, rect, 3, 10)
            caption = TINY_FONT.render(card_name, True, GAME_CYAN)
            WIN.blit(caption, caption.get_rect(center=(rect.centerx, rect.bottom + 12)))

    if (
        viewing_discard_index is not None
        and 0 <= viewing_discard_index < len(view.names)
    ):
        pile = view.discard_piles[viewing_discard_index]
        panel_rect = pygame.Rect(285, 325, 430, 155)
        pygame.draw.rect(WIN, GAME_SHADOW, panel_rect.move(4, 4), border_radius=10)
        pygame.draw.rect(WIN, GAME_PANEL, panel_rect, border_radius=10)
        pygame.draw.rect(WIN, GAME_CYAN, panel_rect, 3, border_radius=10)
        heading = SMALL_FONT.render(
            f"{view.names[viewing_discard_index]}'s discards", True, GAME_CYAN
        )
        WIN.blit(heading, (panel_rect.x + 14, panel_rect.y + 10))
        if not pile:
            empty = SMALL_FONT.render("No cards played yet", True, GAME_MUTED)
            WIN.blit(empty, (panel_rect.x + 14, panel_rect.y + 58))
        for card_index, (card_name, value) in enumerate(pile[-8:]):
            card_rect = pygame.Rect(
                panel_rect.x + 14 + card_index * 50, panel_rect.y + 48, 42, 72
            )
            pygame.draw.rect(WIN, GAME_BACKGROUND, card_rect, border_radius=5)
            pygame.draw.rect(WIN, GAME_PINK, card_rect, 2, border_radius=5)
            _draw_centered(
                str(value), SMALL_FONT, GAME_YELLOW, (card_rect.centerx, card_rect.y + 22)
            )
            _draw_centered(
                card_name[:5], TINY_FONT, GAME_TEXT, (card_rect.centerx, card_rect.y + 52)
            )

    if view.game_state == "WAITING_FOR_GUESS":
        button_width = 70
        spacing = 14
        total_width = 7 * button_width + 6 * spacing
        start_x = WIDTH // 2 - total_width // 2
        for number in range(2, 9):
            rect = pygame.Rect(
                start_x + (number - 2) * (button_width + spacing),
                HEIGHT // 2 - 25,
                button_width,
                70,
            )
            color = GAME_YELLOW if rect.collidepoint(mouse_pos) else GAME_PURPLE
            pygame.draw.rect(WIN, color, rect, border_radius=10)
            pygame.draw.rect(WIN, GAME_PINK, rect, 2, border_radius=10)
            _draw_centered(str(number), TEXT_FONT, GAME_TEXT, rect.center)
            number_buttons.append((number, rect))

    prompts = {
        "WAITING_FOR_CARD": ("Choose a card", GAME_GREEN),
        "WAITING_FOR_TARGET": ("Choose a player", GAME_ORANGE),
        "WAITING_FOR_GUESS": ("Guess their card (2-8)", GAME_CYAN),
        "WAITING_FOR_TURN": ("Waiting for your turn", GAME_TEXT),
        "GAME_ENDED": (
            "Winner: " + ", ".join(view.winners) if view.winners else "Round complete",
            GAME_YELLOW,
        ),
    }
    prompt, color = prompts.get(
        view.game_state, ("Waiting for the table", GAME_TEXT)
    )
    _draw_centered(prompt, TEXT_FONT, color, (WIDTH // 2, HEIGHT - 30))

    pygame.display.update()
    return card_rects, player_rects, number_buttons, discard_buttons


class GameEndScreen:
    def __init__(self):
        self.rematch_button = Button((WIDTH // 2 - 285, 770, 250, 66), "PLAY AGAIN")
        self.leave_button = Button((WIDTH // 2 + 35, 770, 250, 66), "LEAVE ROOM")

    def handle_event(self, event, can_rematch):
        self.rematch_button.enabled = can_rematch
        if self.rematch_button.handle_event(event):
            return "rematch"
        if self.leave_button.handle_event(event):
            return "leave"
        return None

    def draw(self, view, can_rematch):
        WIN.fill(GAME_BACKGROUND)
        _draw_centered("WINNER!", TITLE_FONT, GAME_YELLOW, (WIDTH // 2, 165))
        winner_text = " & ".join(view.winners) if view.winners else "No winner"
        winner_surface = HEADING_FONT.render(winner_text, True, GAME_PINK)
        winner_rect = winner_surface.get_rect(center=(WIDTH // 2, 260))
        WIN.blit(winner_surface, winner_rect)
        if CROWN_IMAGE is not None:
            WIN.blit(CROWN_IMAGE, (winner_rect.left - 68, winner_rect.centery - 27))
            WIN.blit(CROWN_IMAGE, (winner_rect.right + 14, winner_rect.centery - 27))
        _draw_centered(
            f"ROOM  {view.room_code}", SMALL_FONT, GAME_CYAN, (WIDTH // 2, 315)
        )

        score_panel = pygame.Rect(WIDTH // 2 - 285, 365, 570, 310)
        pygame.draw.rect(WIN, GAME_SHADOW, score_panel.move(6, 6), border_radius=14)
        pygame.draw.rect(WIN, GAME_PANEL, score_panel, border_radius=14)
        pygame.draw.rect(WIN, GAME_PINK, score_panel, 4, border_radius=14)
        _draw_centered("FINAL SCORES", TEXT_FONT, GAME_CYAN, (WIDTH // 2, 405))
        for index, (name, tokens) in enumerate(zip(view.names, view.tokens)):
            color = GAME_YELLOW if name in view.winners else GAME_TEXT
            score = SMALL_FONT.render(f"{name}: {tokens} tokens", True, color)
            WIN.blit(score, score.get_rect(center=(WIDTH // 2, 465 + index * 46)))

        self.rematch_button.enabled = can_rematch
        self.rematch_button.draw()
        self.leave_button.draw()
        if not can_rematch:
            _draw_centered(
                "Waiting for the host to start another round",
                SMALL_FONT,
                GAME_MUTED,
                (WIDTH // 2, 860),
            )
        pygame.display.update()
