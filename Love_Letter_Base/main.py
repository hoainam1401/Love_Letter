import pygame  # type: ignore
import sys
import os
import random
from game import GameInstance

FPS = 60
WIDTH = 1000
HEIGHT = 1000

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Love Letter")

# Colors
BACKGROUND = (40, 42, 54)
CURRENT_LINE = (68, 71, 90)
FOREGROUND = (248, 248, 242)
COMMENT = (98, 114, 164)
CYAN = (139, 233, 253)
GREEN = (80, 250, 123)
ORANGE = (255, 184, 108)
PINK = (255, 121, 198)
PURPLE = (189, 147, 249)
RED = (255, 85, 85)
YELLOW = (241, 250, 140)
WHITE = (248, 248, 242)
BLACK = (40, 42, 54)
GRAY = (68, 71, 90)
DARK_GRAY = (98, 114, 164)
BLUE = (189, 147, 249)
# Additional colors
CARD_BG = CURRENT_LINE
CARD_BORDER = PINK
GOLD = YELLOW
LIME = GREEN
SHADOW = (0, 0, 0, 128)  # Semi-transparent shadow

# Fonts
TITLE_FONT = pygame.font.Font(None, 96)  # Larger, bolder title
BUTTON_FONT = pygame.font.Font(None, 56)  # Larger buttons
TEXT_FONT = pygame.font.Font(None, 42)  # Larger text
SMALL_FONT = pygame.font.Font(None, 28)  # Larger small text

# Card dimensions - slightly larger for better visibility
CARD_WIDTH = 120
CARD_HEIGHT = 168


SHADOW_BLACK = (0, 0, 0)  # Pure black for shadows


def draw_text_with_shadow(surface, text, font, color, x, y, shadow_offset=3):
    """Draw text with a shadow for depth"""
    # Draw shadow
    shadow_text = font.render(text, True, SHADOW_BLACK)
    surface.blit(shadow_text, (x + shadow_offset, y + shadow_offset))
    # Draw main text
    main_text = font.render(text, True, color)
    surface.blit(main_text, (x, y))
    return main_text.get_rect(topleft=(x, y))


def draw_card_with_border(surface, card_img, x, y, border_color=None, glow=False):
    """Draw a card with thick Balatro-style border and optional glow"""
    if border_color is None:
        border_color = CARD_BORDER

    # Draw shadow first
    shadow_rect = pygame.Rect(x + 4, y + 4, CARD_WIDTH, CARD_HEIGHT)
    shadow_surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
    shadow_surf.set_alpha(100)
    shadow_surf.fill(SHADOW_BLACK)
    surface.blit(shadow_surf, shadow_rect)

    # Draw glow effect if enabled
    if glow:
        for i in range(3):
            glow_rect = pygame.Rect(
                x - 2 - i, y - 2 - i, CARD_WIDTH + 4 + i * 2, CARD_HEIGHT + 4 + i * 2
            )
            glow_alpha = 100 - i * 30
            pygame.draw.rect(surface, GOLD, glow_rect, 2, border_radius=12)

    # Draw thick border (multiple layers for thickness)
    for i in range(4):
        border_rect = pygame.Rect(x - i, y - i, CARD_WIDTH + i * 2, CARD_HEIGHT + i * 2)
        pygame.draw.rect(surface, border_color, border_rect, 1, border_radius=10)

    # Draw card image
    surface.blit(card_img, (x, y))


def draw_box_with_border(
    surface, rect, bg_color, border_color, border_width=4, shadow=True
):
    """Draw a box with thick border and shadow for Balatro style"""
    if shadow:
        # Draw shadow
        shadow_rect = rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        shadow_surf = pygame.Surface((shadow_rect.width, shadow_rect.height))
        shadow_surf.set_alpha(120)
        shadow_surf.fill(SHADOW_BLACK)
        surface.blit(shadow_surf, shadow_rect)

    # Draw background
    pygame.draw.rect(surface, bg_color, rect, border_radius=8)

    # Draw thick border (multiple layers)
    for i in range(border_width):
        border_rect = rect.inflate(-i * 2, -i * 2)
        pygame.draw.rect(surface, border_color, border_rect, 1, border_radius=8)


# Load card images
def load_card_images():
    card_images = {}
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

    for name in card_names:
        img_path = f"images/{name}.png"
        if os.path.exists(img_path):
            img = pygame.image.load(img_path)
            card_images[name] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
        else:
            # Create a placeholder if image doesn't exist
            surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
            surf.fill(CARD_BG)
            pygame.draw.rect(surf, PINK, surf.get_rect(), border_radius=10)
            font = pygame.font.Font(None, 20)
            text = font.render(name, True, FOREGROUND)
            text_rect = text.get_rect(center=(CARD_WIDTH // 2, CARD_HEIGHT // 2))
            surf.blit(text, text_rect)
            card_images[name] = surf

    # Load card back
    back_path = "images/Back.png"
    if os.path.exists(back_path):
        card_images["Back"] = pygame.transform.scale(
            pygame.image.load(back_path), (CARD_WIDTH, CARD_HEIGHT)
        )
    else:
        surf = pygame.Surface((CARD_WIDTH, CARD_HEIGHT))
        surf.fill(PURPLE)
        pygame.draw.rect(surf, PINK, surf.get_rect(), 3)
        card_images["Back"] = surf

    return card_images


CARD_IMAGES = load_card_images()

# Pre-create small card back for player boxes (avoid scaling every frame)
SMALL_CARD_BACK = pygame.transform.scale(CARD_IMAGES["Back"], (96, 134))


# Load crown image for winner screen
def load_crown_image():
    crown_path = "images/crown.png"
    if os.path.exists(crown_path):
        crown_img = pygame.image.load(crown_path)
        return pygame.transform.scale(crown_img, (50, 50))  # Scale to appropriate size
    else:
        # Create a placeholder if crown doesn't exist
        surf = pygame.Surface((50, 50))
        surf.fill(GOLD)
        font = pygame.font.Font(None, 40)
        text = font.render("♕", True, BLACK)
        text_rect = text.get_rect(center=(25, 25))
        surf.blit(text, text_rect)
        return surf


CROWN_IMAGE = load_crown_image()


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = self.color if not self.hover else YELLOW

        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(surface, SHADOW_BLACK, shadow_rect, border_radius=10)

        # Draw button background
        pygame.draw.rect(surface, color, self.rect, border_radius=10)

        # Draw thick pink border
        for i in range(4):
            border_rect = self.rect.inflate(-i * 2, -i * 2)
            border_color = YELLOW if self.hover else PINK
            pygame.draw.rect(surface, border_color, border_rect, 2, border_radius=10)

        # Draw text with shadow
        shadow_text = BUTTON_FONT.render(self.text, True, SHADOW_BLACK)
        text_rect = shadow_text.get_rect(center=self.rect.center)
        surface.blit(shadow_text, (text_rect.x + 3, text_rect.y + 3))

        text_surface = BUTTON_FONT.render(self.text, True, FOREGROUND)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


def draw_player_selection_screen(selected_count):
    WIN.fill(BACKGROUND)
    title_text = "Love Letter"
    # Draw multiple shadow layers for depth
    for i in range(3, 0, -1):
        shadow = TITLE_FONT.render(title_text, True, SHADOW_BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH // 2 + i * 2, 100 + i * 2))
        WIN.blit(shadow, shadow_rect)

    # Draw title with pink
    title = TITLE_FONT.render(title_text, True, PINK)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    WIN.blit(title, title_rect)

    # Subtitle
    subtitle = TEXT_FONT.render("Select Number of Players (2-4)", True, FOREGROUND)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
    # Draw subtitle shadow
    shadow_sub = TEXT_FONT.render("Select Number of Players (2-4)", True, SHADOW_BLACK)
    WIN.blit(shadow_sub, (subtitle_rect.x + 2, subtitle_rect.y + 2))
    WIN.blit(subtitle, subtitle_rect)

    # Player count buttons
    buttons = []
    for i in range(2, 5):
        x = WIDTH // 2 - 100
        y = 280 + (i - 2) * 100
        color = GREEN if i == selected_count else PURPLE
        buttons.append(Button(x, y, 200, 70, f"{i} Players", color))

    for button in buttons:
        button.draw(WIN)

    # Start button (only if a selection is made)
    start_button = None
    if selected_count > 0:
        start_button = Button(WIDTH // 2 - 100, 600, 200, 70, "START", GREEN)
        start_button.draw(WIN)

    pygame.display.update()
    return buttons, start_button


def draw_game_end_screen(winners, player_list):
    """Draw the game end screen with winner announcement and options"""
    WIN.fill(BACKGROUND)

    # Safety check
    if not winners:
        winners = ["No Winner"]

    # Animated background effect (optional sparkles/stars)
    for i in range(20):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(2, 6)
        alpha = random.randint(100, 255)
        star_surf = pygame.Surface((size, size))
        star_surf.set_alpha(alpha)
        star_surf.fill(YELLOW)
        WIN.blit(star_surf, (x, y))

    # Large "WINNER!" text in Balatro style
    winner_text = "WINNER!"
    # Draw multiple shadow layers for depth
    for i in range(5, 0, -1):
        shadow = TITLE_FONT.render(winner_text, True, SHADOW_BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH // 2 + i * 3, 150 + i * 3))
        WIN.blit(shadow, shadow_rect)

    # Draw main text with gold color
    winner_surface = TITLE_FONT.render(winner_text, True, GOLD)
    winner_rect = winner_surface.get_rect(center=(WIDTH // 2, 150))
    WIN.blit(winner_surface, winner_rect)

    # Draw glow effect around winner text
    for i in range(3):
        glow_rect = winner_rect.inflate(20 + i * 10, 20 + i * 10)
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height))
        glow_surf.set_alpha(30 - i * 10)
        glow_surf.fill(GOLD)
        WIN.blit(glow_surf, glow_rect)

    # Display winner names
    y_offset = 280
    for winner_name in winners:
        # Shadow
        name_shadow = BUTTON_FONT.render(winner_name, True, SHADOW_BLACK)
        name_rect = name_shadow.get_rect(center=(WIDTH // 2 + 3, y_offset + 3))
        WIN.blit(name_shadow, name_rect)

        # Main text
        name_surface = BUTTON_FONT.render(winner_name, True, PINK)
        name_rect = name_surface.get_rect(center=(WIDTH // 2, y_offset))
        WIN.blit(name_surface, name_rect)

        # Draw crown images next to winner name
        # Left crown
        crown_left_x = name_rect.left - 60
        crown_left_y = y_offset - 25  # Center vertically with text
        WIN.blit(CROWN_IMAGE, (crown_left_x, crown_left_y))

        # Right crown
        crown_right_x = name_rect.right + 10
        crown_right_y = y_offset - 25  # Center vertically with text
        WIN.blit(CROWN_IMAGE, (crown_right_x, crown_right_y))

        y_offset += 70

    # Final scores box
    score_box_y = y_offset + 20
    score_box_width = 600
    score_box_height = 200
    score_box = pygame.Rect(
        WIDTH // 2 - score_box_width // 2,
        score_box_y,
        score_box_width,
        score_box_height,
    )

    # Draw score box with shadow
    draw_box_with_border(WIN, score_box, CURRENT_LINE, PINK, 4, shadow=True)

    # Score title
    score_title = TEXT_FONT.render("Final Scores", True, CYAN)
    score_title_rect = score_title.get_rect(center=(WIDTH // 2, score_box_y + 30))
    WIN.blit(score_title, score_title_rect)

    # Display all player scores
    score_y = score_box_y + 70
    for player in player_list:
        player_score_text = f"{player.name}: {player.winningTokenCount} tokens"
        score_surface = SMALL_FONT.render(player_score_text, True, FOREGROUND)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, score_y))
        WIN.blit(score_surface, score_rect)
        score_y += 35

    # Buttons
    restart_button = Button(
        WIDTH // 2 - 250, HEIGHT - 150, 200, 70, "PLAY AGAIN", GREEN
    )
    menu_button = Button(WIDTH // 2 + 50, HEIGHT - 150, 200, 70, "MAIN MENU", PURPLE)

    restart_button.draw(WIN)
    menu_button.draw(WIN)

    pygame.display.update()

    return restart_button, menu_button


def draw_game_screen(game_instance, mouse_pos=(0, 0), viewing_discard_idx=None):
    WIN.fill(BACKGROUND)

    # Track clickable card rectangles
    card_rects = []
    # Track clickable player rectangles
    player_rects = []
    # Track discard buttons
    discard_buttons = []
    # Track number buttons
    number_buttons = []

    title_bar = pygame.Rect(0, 0, WIDTH, 90)
    # Draw shadow/depth
    pygame.draw.rect(WIN, SHADOW_BLACK, pygame.Rect(0, 4, WIDTH, 90))
    pygame.draw.rect(WIN, CURRENT_LINE, title_bar, border_radius=0)
    # Draw thick pink bottom border
    pygame.draw.rect(WIN, PINK, pygame.Rect(0, 86, WIDTH, 4))

    # Title with shadow
    title_shadow = TEXT_FONT.render("Love Letter", True, SHADOW_BLACK)
    WIN.blit(title_shadow, (23, 28))
    title = TEXT_FONT.render("Love Letter", True, PINK)
    WIN.blit(title, (20, 25))

    # Game info with shadow
    remaining_text_str = f"Deck: {game_instance.remainingCount()}"
    remaining_shadow = SMALL_FONT.render(remaining_text_str, True, SHADOW_BLACK)
    WIN.blit(remaining_shadow, (WIDTH - 148, 33))
    remaining_text = SMALL_FONT.render(remaining_text_str, True, CYAN)
    WIN.blit(remaining_text, (WIDTH - 150, 30))

    # Draw deck (card back) in center
    deck_x = WIDTH // 2 - CARD_WIDTH // 2
    deck_y = HEIGHT // 2 - CARD_HEIGHT // 2

    if game_instance.remainingCount() > 0:
        # Draw stacked cards with shadows for depth
        for i in range(min(4, game_instance.remainingCount())):
            offset = i * 4
            # Shadow for each card
            shadow_rect = pygame.Rect(
                deck_x + offset + 3, deck_y + offset + 3, CARD_WIDTH, CARD_HEIGHT
            )
            pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=8)
            # Card
            WIN.blit(CARD_IMAGES["Back"], (deck_x + offset, deck_y + offset))
            # Pink border for each card
            card_rect = pygame.Rect(
                deck_x + offset, deck_y + offset, CARD_WIDTH, CARD_HEIGHT
            )
            pygame.draw.rect(WIN, PINK, card_rect, 3, border_radius=8)

        # Deck label with shadow
        deck_label_shadow = SMALL_FONT.render("DECK", True, SHADOW_BLACK)
        deck_label_rect = deck_label_shadow.get_rect(
            center=(deck_x + CARD_WIDTH // 2 + 2, deck_y + CARD_HEIGHT + 22)
        )
        WIN.blit(deck_label_shadow, deck_label_rect)

        deck_label = SMALL_FONT.render("DECK", True, PURPLE)
        deck_label_rect = deck_label.get_rect(
            center=(deck_x + CARD_WIDTH // 2, deck_y + CARD_HEIGHT + 20)
        )
        WIN.blit(deck_label, deck_label_rect)

    # Draw players in a layout
    player_positions = [
        (WIDTH // 2 - 340, HEIGHT - 300),  # Bottom left (player 1)
        (WIDTH - 250, HEIGHT // 2 - 150),  # Right (player 2)
        (WIDTH // 2 - 100, 100),  # Top (player 3)
        (50, HEIGHT // 2 - 150),  # Left (player 4)
    ]

    for i, player in enumerate(game_instance.playerList):
        # Use fixed positions (no rotation)
        x, y = player_positions[i]

        # Player info box
        box_width = 200
        box_height = 180
        box_rect = pygame.Rect(x, y, box_width, box_height)

        # Check if this player can be targeted
        is_valid_target = False
        if hasattr(game_instance, "gameState") and hasattr(
            game_instance, "isValidTarget"
        ):
            if game_instance.gameState == "WAITING_FOR_TARGET":
                is_valid_target = game_instance.isValidTarget(i)
                if is_valid_target:
                    player_rects.append((i, box_rect))

        # Check if hovering over this player
        is_hovering = box_rect.collidepoint(mouse_pos)

        # Color based on state
        if player.isKO:
            box_color = RED
            border_color = DARK_GRAY
        elif player == game_instance.currPlayer:
            box_color = GREEN
            border_color = YELLOW
        elif is_valid_target:
            box_color = ORANGE
            border_color = YELLOW
        else:
            box_color = PURPLE
            border_color = PINK

        # Draw shadow
        shadow_rect = box_rect.copy()
        shadow_rect.x += 4
        shadow_rect.y += 4
        pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=10)

        # Draw box background
        pygame.draw.rect(WIN, box_color, box_rect, border_radius=10)

        # Draw thick border (animated on hover)
        border_width = 5 if is_hovering and is_valid_target else 3
        for i in range(border_width):
            border_rect = box_rect.inflate(-i * 2, -i * 2)
            pygame.draw.rect(WIN, border_color, border_rect, 2, border_radius=10)

        # Player name with shadow
        name_shadow = TEXT_FONT.render(player.name, True, SHADOW_BLACK)
        name_rect = name_shadow.get_rect(center=(x + box_width // 2 + 2, y + 27))
        WIN.blit(name_shadow, name_rect)

        name_surface = TEXT_FONT.render(player.name, True, FOREGROUND)
        name_rect = name_surface.get_rect(center=(x + box_width // 2, y + 25))
        WIN.blit(name_surface, name_rect)

        # Status with appropriate color
        status = (
            "KNOCKED OUT"
            if player.isKO
            else "Protected" if player.isProtected else "Active"
        )
        status_color = RED if player.isKO else CYAN if player.isProtected else GREEN

        status_shadow = SMALL_FONT.render(status, True, SHADOW_BLACK)
        status_rect = status_shadow.get_rect(center=(x + box_width // 2 + 2, y + 57))
        WIN.blit(status_shadow, status_rect)

        status_surface = SMALL_FONT.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(x + box_width // 2, y + 55))
        WIN.blit(status_surface, status_rect)

        # Tokens with yellow color
        tokens_str = f"Tokens: {player.winningTokenCount}"
        tokens_shadow = SMALL_FONT.render(tokens_str, True, SHADOW_BLACK)
        tokens_rect = tokens_shadow.get_rect(center=(x + box_width // 2 + 2, y + 87))
        WIN.blit(tokens_shadow, tokens_rect)

        tokens = SMALL_FONT.render(tokens_str, True, YELLOW)
        tokens_rect = tokens.get_rect(center=(x + box_width // 2, y + 85))
        WIN.blit(tokens, tokens_rect)

        # Show card back if player has cards (but not the current player)
        if len(player.hand) > 0 and player != game_instance.currPlayer:
            card_x = x + (box_width - 96) // 2
            card_y = y + 110
            # Draw shadow for card
            shadow_rect = pygame.Rect(card_x + 3, card_y + 3, 96, 134)
            pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=8)
            # Use pre-scaled image instead of scaling every frame
            WIN.blit(SMALL_CARD_BACK, (card_x, card_y))
            # Draw pink border on card
            card_rect = pygame.Rect(card_x, card_y, 96, 134)
            pygame.draw.rect(WIN, PINK, card_rect, 2, border_radius=8)

        # Draw small discard button to the left of player box
        button_width = 50
        button_height = 50
        button_x = x - button_width - 10  # Position to the left
        button_y = y + 10
        button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        discard_buttons.append((i, button_rect))

        # Check if hovering
        is_button_hovering = button_rect.collidepoint(mouse_pos)
        button_color = ORANGE if is_button_hovering else PURPLE

        # Draw button shadow
        shadow_rect = button_rect.copy()
        shadow_rect.x += 2
        shadow_rect.y += 2
        pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=8)

        # Draw button background
        pygame.draw.rect(WIN, button_color, button_rect, border_radius=8)

        # Draw button border
        pygame.draw.rect(WIN, PINK, button_rect, 2, border_radius=8)

        # Button text - show count
        discard_count = len(player.discardPile)
        count_font = pygame.font.Font(None, 32)
        count_text = count_font.render(str(discard_count), True, YELLOW)
        count_rect = count_text.get_rect(center=button_rect.center)
        WIN.blit(count_text, count_rect)

        # Label below count
        label_font = pygame.font.Font(None, 14)
        label_text = label_font.render("Cards", True, FOREGROUND)
        label_rect = label_text.get_rect(
            center=(button_rect.centerx, button_rect.centery + 15)
        )
        WIN.blit(label_text, label_rect)

        # If this player's discard is being viewed, show expanded discard pile
        if viewing_discard_idx == i and len(player.discardPile) > 0:
            # Draw expanded discard box below the button
            discard_box_width = 220
            discard_box_height = 180
            discard_x = button_x - 10
            discard_y = button_y + button_height + 10
            discard_rect = pygame.Rect(
                discard_x, discard_y, discard_box_width, discard_box_height
            )

            # Draw shadow
            shadow_rect = discard_rect.copy()
            shadow_rect.x += 3
            shadow_rect.y += 3
            pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=8)

            # Draw background
            pygame.draw.rect(WIN, CURRENT_LINE, discard_rect, border_radius=8)

            # Draw border
            for j in range(2):
                border_rect = discard_rect.inflate(-j * 2, -j * 2)
                pygame.draw.rect(WIN, CYAN, border_rect, 2, border_radius=8)

            # Title
            title_text = f"{player.name}'s Discard Pile"
            title_surface = pygame.font.Font(None, 22).render(title_text, True, CYAN)
            WIN.blit(title_surface, (discard_x + 10, discard_y + 8))

            # Draw cards in grid
            mini_card_width = 35
            mini_card_height = 50
            cards_per_row = 5
            card_spacing = 5
            start_x = discard_x + 10
            start_y = discard_y + 35

            for idx, card in enumerate(player.discardPile[-10:]):  # Show last 10
                row = idx // cards_per_row
                col = idx % cards_per_row

                mini_x = start_x + col * (mini_card_width + card_spacing)
                mini_y = start_y + row * (mini_card_height + card_spacing + 12)

                # Draw mini card
                mini_rect = pygame.Rect(
                    mini_x, mini_y, mini_card_width, mini_card_height
                )
                pygame.draw.rect(WIN, CARD_BG, mini_rect, border_radius=4)
                pygame.draw.rect(WIN, PINK, mini_rect, 1, border_radius=4)

                # Card value
                val_font = pygame.font.Font(None, 28)
                val_surface = val_font.render(str(card.val), True, YELLOW)
                val_rect = val_surface.get_rect(
                    center=(mini_x + mini_card_width // 2, mini_y + 18)
                )
                WIN.blit(val_surface, val_rect)

                # Card name
                name_abbrev = card.name[:3] if len(card.name) > 3 else card.name
                name_font = pygame.font.Font(None, 16)
                name_surface = name_font.render(name_abbrev, True, FOREGROUND)
                name_rect = name_surface.get_rect(
                    center=(mini_x + mini_card_width // 2, mini_y + 38)
                )
                WIN.blit(name_surface, name_rect)

            # Show count if more than 10
            if len(player.discardPile) > 10:
                more_text = pygame.font.Font(None, 18).render(
                    f"+{len(player.discardPile) - 10} more", True, COMMENT
                )
                WIN.blit(more_text, (discard_x + 140, discard_y + 155))

    # Draw current player's hand at bottom center with actual card images
    if len(game_instance.currPlayer.hand) > 0:
        hand_y = HEIGHT - 290

        # Background for hand area with shadow - sized for 2 larger cards
        hand_bg_width = 320
        hand_bg_height = 220
        hand_bg = pygame.Rect(
            WIDTH // 2 - hand_bg_width // 2, hand_y - 30, hand_bg_width, hand_bg_height
        )
        # Draw shadow
        shadow_bg = hand_bg.copy()
        shadow_bg.x += 4
        shadow_bg.y += 4
        pygame.draw.rect(WIN, SHADOW_BLACK, shadow_bg, border_radius=12)

        # Draw background
        pygame.draw.rect(WIN, CURRENT_LINE, hand_bg, border_radius=12)
        # Draw thick pink border
        for i in range(3):
            border_rect = hand_bg.inflate(-i * 2, -i * 2)
            pygame.draw.rect(WIN, PINK, border_rect, 2, border_radius=12)

        # Hand label with shadow
        hand_label_shadow = TEXT_FONT.render("Your Hand", True, SHADOW_BLACK)
        WIN.blit(hand_label_shadow, (WIDTH // 2 - 78, hand_y - 22))
        hand_label = TEXT_FONT.render("Your Hand", True, PINK)
        WIN.blit(hand_label, (WIDTH // 2 - 80, hand_y - 25))

        # Draw cards effects
        total_cards = len(game_instance.currPlayer.hand)
        start_x = WIDTH // 2 - (total_cards * (CARD_WIDTH + 20) - 20) // 2

        for idx, card in enumerate(game_instance.currPlayer.hand):
            card_x = start_x + idx * (CARD_WIDTH + 20)
            card_y = hand_y + 10

            # Create a rect for this card and store it
            card_rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
            card_rects.append(card_rect)

            # Check if mouse is hovering
            is_hovering = card_rect.collidepoint(mouse_pos)

            # Draw highlight if hovering and clickable
            can_click = True
            if hasattr(game_instance, "gameState"):
                can_click = game_instance.gameState == "WAITING_FOR_CARD"

            # Draw shadow
            shadow_rect = pygame.Rect(card_x + 4, card_y + 4, CARD_WIDTH, CARD_HEIGHT)
            pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=10)

            # Draw glow effect if hovering and clickable
            if is_hovering and can_click:
                for i in range(3):
                    glow_rect = card_rect.inflate(8 - i * 2, 8 - i * 2)
                    glow_color = YELLOW if i % 2 == 0 else PINK
                    pygame.draw.rect(WIN, glow_color, glow_rect, 2, border_radius=12)

            # Draw card image
            WIN.blit(CARD_IMAGES[card.name], (card_x, card_y))

            # Draw thick pink border
            border_color = YELLOW if is_hovering and can_click else PINK
            for i in range(3):
                border_rect = card_rect.inflate(-i * 2, -i * 2)
                pygame.draw.rect(WIN, border_color, border_rect, 2, border_radius=10)

            # Draw card name below with shadow
            card_name_str = f"{card.name} ({card.val})"
            card_name_shadow = SMALL_FONT.render(card_name_str, True, SHADOW_BLACK)
            card_name_rect = card_name_shadow.get_rect(
                center=(card_x + CARD_WIDTH // 2 + 2, card_y + CARD_HEIGHT + 17)
            )
            WIN.blit(card_name_shadow, card_name_rect)

            card_name = SMALL_FONT.render(card_name_str, True, CYAN)
            card_name_rect = card_name.get_rect(
                center=(card_x + CARD_WIDTH // 2, card_y + CARD_HEIGHT + 15)
            )
            WIN.blit(card_name, card_name_rect)

    # Draw number buttons if waiting for guess
    if hasattr(game_instance, "gameState"):
        if game_instance.gameState == "WAITING_FOR_GUESS":
            button_width = 70
            button_height = 70
            button_spacing = 15
            total_width = 7 * button_width + 6 * button_spacing
            start_x = WIDTH // 2 - total_width // 2
            button_y = HEIGHT // 2 - 20

            for num in range(2, 9):  # 2 through 8
                button_x = start_x + (num - 2) * (button_width + button_spacing)
                button_rect = pygame.Rect(
                    button_x, button_y, button_width, button_height
                )

                # Check if hovering
                is_hovering = button_rect.collidepoint(mouse_pos)

                # Draw shadow
                shadow_rect = button_rect.copy()
                shadow_rect.x += 3
                shadow_rect.y += 3
                pygame.draw.rect(WIN, SHADOW_BLACK, shadow_rect, border_radius=10)

                # Draw button background
                button_color = YELLOW if is_hovering else PURPLE
                pygame.draw.rect(WIN, button_color, button_rect, border_radius=10)

                # Draw thick border
                border_color = YELLOW if is_hovering else PINK
                for i in range(3):
                    border_r = button_rect.inflate(-i * 2, -i * 2)
                    pygame.draw.rect(WIN, border_color, border_r, 2, border_radius=10)

                # Draw number with shadow
                num_shadow = TEXT_FONT.render(str(num), True, SHADOW_BLACK)
                num_rect = num_shadow.get_rect(
                    center=(button_rect.centerx + 2, button_rect.centery + 2)
                )
                WIN.blit(num_shadow, num_rect)

                num_text = TEXT_FONT.render(str(num), True, FOREGROUND)
                num_rect = num_text.get_rect(center=button_rect.center)
                WIN.blit(num_text, num_rect)

                # Store for click detection
                number_buttons.append((num, button_rect))

    # Draw prompts emphasis
    if hasattr(game_instance, "gameState"):
        if game_instance.gameState == "WAITING_FOR_CARD":
            prompt_text = "Select a card to play"
            prompt_color = GREEN
        elif game_instance.gameState == "WAITING_FOR_TARGET":
            prompt_text = "Select a target player"
            prompt_color = ORANGE
        elif game_instance.gameState == "WAITING_FOR_GUESS":
            prompt_text = "Guess opponent's card (2-8)"
            prompt_color = CYAN
        else:
            prompt_text = ""
            prompt_color = FOREGROUND
    else:
        prompt_text = "Select a card to play"
        prompt_color = GREEN

    if prompt_text:
        # Draw prompt with shadow and border
        prompt_shadow = TEXT_FONT.render(prompt_text, True, SHADOW_BLACK)
        prompt_rect = prompt_shadow.get_rect(center=(WIDTH // 2 + 3, HEIGHT - 33))
        WIN.blit(prompt_shadow, prompt_rect)

        prompt = TEXT_FONT.render(prompt_text, True, prompt_color)
        prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT - 35))
        WIN.blit(prompt, prompt_rect)

    instruction = SMALL_FONT.render("Press ESC to return to menu", True, COMMENT)
    WIN.blit(instruction, (20, HEIGHT - 30))

    pygame.display.update()

    # Return all clickable rectangles
    return card_rects, player_rects, number_buttons, discard_buttons


def main():
    run = True
    clock = pygame.time.Clock()

    # Game states
    STATE_MENU = 0
    STATE_GAME = 1
    STATE_GAME_END = 2

    state = STATE_MENU
    selected_player_count = 0
    game_instance = None

    # Store clickable elements
    card_rects = []
    player_rects = []
    number_buttons = []
    discard_buttons = []

    # Track mouse position
    mouse_pos = (0, 0)

    # Track which player's discard is being viewed
    viewing_discard_idx = None

    while run:
        clock.tick(FPS)

        if state == STATE_MENU:
            buttons, start_button = draw_player_selection_screen(selected_player_count)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                # Check player count buttons
                for i, button in enumerate(buttons):
                    if button.handle_event(event):
                        selected_player_count = i + 2

                # Check start button
                if start_button and start_button.handle_event(event):
                    # Create game with player names
                    player_names = [
                        f"Player {i+1}" for i in range(selected_player_count)
                    ]
                    try:
                        game_instance = GameInstance(player_names)
                        state = STATE_GAME
                    except ValueError as e:
                        print(f"Error creating game: {e}")

        elif state == STATE_GAME:
            # Check if game ended
            if game_instance and game_instance.gameState == "GAME_ENDED":
                print(f"Game ended! Winners: {game_instance.winners}")
                state = STATE_GAME_END
                continue

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to menu
                        state = STATE_MENU
                        selected_player_count = 0
                        game_instance = None

                # Track mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos

                # Handle mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos

                    # Check if clicked on a card
                    if game_instance and len(card_rects) > 0:
                        for idx, rect in enumerate(card_rects):
                            if rect.collidepoint(mouse_pos):
                                print(
                                    f"Clicked card {idx}: {game_instance.currPlayer.hand[idx].name}"
                                )
                                game_instance.selectCard(
                                    idx
                                )  # Actually call the method
                                break  # Only handle one click

                    # Check if clicked on a player
                    if game_instance and len(player_rects) > 0:
                        for player_idx, rect in player_rects:
                            if rect.collidepoint(mouse_pos):
                                print(
                                    f"Clicked player {player_idx}: {game_instance.playerList[player_idx].name}"
                                )
                                game_instance.selectTarget(
                                    player_idx
                                )  # Actually call the method!
                                break

                    # Check if clicked on a number button
                    if game_instance and len(number_buttons) > 0:
                        for num, rect in number_buttons:
                            if rect.collidepoint(mouse_pos):
                                print(f"Guessed number: {num}")
                                game_instance.selectGuess(
                                    num
                                )  # Actually call the method!
                                break

                    # Check if clicked on a discard button
                    if game_instance and len(discard_buttons) > 0:
                        for player_idx, rect in discard_buttons:
                            if rect.collidepoint(mouse_pos):
                                # Toggle discard view
                                if viewing_discard_idx == player_idx:
                                    viewing_discard_idx = None
                                else:
                                    viewing_discard_idx = player_idx
                                print(f"Toggled discard view for player {player_idx}")
                                break

            # FIXED: Draw AFTER processing events, only once per frame
            if game_instance:
                card_rects, player_rects, number_buttons, discard_buttons = (
                    draw_game_screen(game_instance, mouse_pos, viewing_discard_idx)
                )

        elif state == STATE_GAME_END:
            print(
                f"Entered STATE_GAME_END, game_instance exists: {game_instance is not None}"
            )
            if game_instance:
                print(f"Drawing game end screen with winners: {game_instance.winners}")
                try:
                    restart_button, menu_button = draw_game_end_screen(
                        game_instance.winners, game_instance.playerList
                    )

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            run = False

                        # Check restart button
                        if restart_button.handle_event(event):
                            print("Restart button clicked!")
                            # Restart with same player count
                            if game_instance:  # Type guard
                                game_instance.resetTable()
                                state = STATE_GAME

                        # Check menu button
                        if menu_button.handle_event(event):
                            print("Menu button clicked!")
                            state = STATE_MENU
                            selected_player_count = 0
                            game_instance = None
                except Exception as e:
                    print(f"Error in game end screen: {e}")
                    import traceback

                    traceback.print_exc()
                    # Fall back to menu
                    state = STATE_MENU
                    selected_player_count = 0
                    game_instance = None
            else:
                print("Game instance is None in STATE_GAME_END!")
                state = STATE_MENU

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
