import pygame 
import sys
import os
from game import GameInstance

FPS = 60
# WIDTH = 1800
WIDTH = 800
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
LIGHT_BROWN = (68, 71, 90)
DARK_BROWN = (40, 42, 54)
BLUE = (189, 147, 249)

# Fonts
TITLE_FONT = pygame.font.Font(None, 72)
BUTTON_FONT = pygame.font.Font(None, 48)
TEXT_FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)

# Card dimensions
CARD_WIDTH = 100
CARD_HEIGHT = 140


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
            surf.fill(CURRENT_LINE)
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

# PERFORMANCE: Pre-create small card back for player boxes (avoid scaling every frame)
SMALL_CARD_BACK = pygame.transform.scale(CARD_IMAGES["Back"], (80, 112))


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = CURRENT_LINE if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, PINK, self.rect, 3)

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

    # Title
    title = TITLE_FONT.render("Love Letter", True, PINK)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    WIN.blit(title, title_rect)

    # Subtitle
    subtitle = TEXT_FONT.render("Select Number of Players (2-4)", True, FOREGROUND)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
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


def draw_game_screen(game_instance, mouse_pos=(0, 0)):
    WIN.fill(BACKGROUND)

    # Track clickable card rectangles
    card_rects = []
    # Track clickable player rectangles
    player_rects = []
    # Track number buttons
    number_buttons = []

    # Title bar
    title_bar = pygame.Rect(0, 0, WIDTH, 80)
    pygame.draw.rect(WIN, CURRENT_LINE, title_bar, border_radius=0)
    pygame.draw.rect(WIN, PINK, pygame.Rect(0, 0, WIDTH, 80), 2, border_radius=0)
    title = TEXT_FONT.render("Love Letter", True, PINK)
    WIN.blit(title, (20, 25))

    # Game info
    remaining_text = SMALL_FONT.render(
        f"Cards in deck: {game_instance.remainingCount()}", True, FOREGROUND
    )
    WIN.blit(remaining_text, (WIDTH - 200, 30))

    # Draw deck (card back) in center of screen
    deck_x = WIDTH // 2 - CARD_WIDTH // 2
    deck_y = HEIGHT // 2 - CARD_HEIGHT // 2  # Centered vertically

    # Draw multiple card backs stacked to show deck
    if game_instance.remainingCount() > 0:
        for i in range(min(3, game_instance.remainingCount())):
            offset = i * 3
            WIN.blit(CARD_IMAGES["Back"], (deck_x + offset, deck_y + offset))

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
        # old UI
        x, y = player_positions[i]

        # player = game_instance.playerList[playerPos]
        x, y = player_positions[
            (i - game_instance.currPlayerIndex) % game_instance.playerCount
        ]

        # Player info box
        box_width = 200
        box_height = 180
        box_rect = pygame.Rect(x, y, box_width, box_height)

        # NEW: Check if this player can be targeted
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
        elif player == game_instance.currPlayer:
            box_color = GREEN
        elif is_valid_target:
            # Highlight valid targets with orange
            box_color = ORANGE
        else:
            box_color = GRAY

        pygame.draw.rect(WIN, box_color, box_rect, border_radius=8)

        # Add hover effect
        if is_hovering and is_valid_target:
            pygame.draw.rect(WIN, YELLOW, box_rect, 4, border_radius=8)
        else:
            pygame.draw.rect(WIN, PINK, box_rect, 2, border_radius=8)

        # Player name
        name_surface = TEXT_FONT.render(player.name, True, FOREGROUND)
        name_rect = name_surface.get_rect(center=(x + box_width // 2, y + 25))
        WIN.blit(name_surface, name_rect)

        # Status
        status = (
            "KNOCKED OUT"
            if player.isKO
            else "Protected" if player.isProtected else "Active"
        )
        status_surface = SMALL_FONT.render(status, True, FOREGROUND)
        status_rect = status_surface.get_rect(center=(x + box_width // 2, y + 55))
        WIN.blit(status_surface, status_rect)

        # Tokens
        tokens = SMALL_FONT.render(
            f"Tokens: {player.winningTokenCount}", True, FOREGROUND
        )
        tokens_rect = tokens.get_rect(center=(x + box_width // 2, y + 85))
        WIN.blit(tokens, tokens_rect)

        # Show card back if player has cards (but not the current player)
        if len(player.hand) > 0 and player != game_instance.currPlayer:
            card_x = x + (box_width - 80) // 2
            card_y = y + 110
            # PERFORMANCE: Use pre-scaled image instead of scaling every frame
            WIN.blit(SMALL_CARD_BACK, (card_x, card_y))

    # Draw current player's hand at bottom center with actual card images
    if len(game_instance.currPlayer.hand) > 0:
        hand_y = HEIGHT - 250

        # Background for hand area - sized for 2 cards
        hand_bg_width = 280
        hand_bg_height = 150
        hand_bg = pygame.Rect(
            WIDTH // 2 - hand_bg_width // 2, hand_y - 20, hand_bg_width, hand_bg_height
        )
        pygame.draw.rect(WIN, CURRENT_LINE, hand_bg, border_radius=10)
        pygame.draw.rect(WIN, PURPLE, hand_bg, 2, border_radius=10)

        hand_label = TEXT_FONT.render("Your Hand", True, PINK)
        WIN.blit(hand_label, (WIDTH // 2 - 70, hand_y - 15))

        # Draw cards with images
        total_cards = len(game_instance.currPlayer.hand)
        start_x = WIDTH // 2 - (total_cards * (CARD_WIDTH + 20) - 20) // 2

        for idx, card in enumerate(game_instance.currPlayer.hand):
            card_x = start_x + idx * (CARD_WIDTH + 20)
            card_y = hand_y + 20

            # Create a rect for this card and store it
            card_rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
            card_rects.append(card_rect)

            # Check if mouse is hovering
            is_hovering = card_rect.collidepoint(mouse_pos)

            # Draw highlight if hovering and clickable
            can_click = True
            if hasattr(game_instance, "gameState"):
                can_click = game_instance.gameState == "WAITING_FOR_CARD"

            if is_hovering and can_click:
                # Draw a glow effect
                highlight_rect = card_rect.inflate(10, 10)  # Slightly bigger
                pygame.draw.rect(WIN, YELLOW, highlight_rect, 3, border_radius=10)

            # Draw card image
            WIN.blit(CARD_IMAGES[card.name], (card_x, card_y))

            # Draw card border with rounded corners
            border_color = PINK
            pygame.draw.rect(WIN, border_color, card_rect, 2, border_radius=8)

            # Draw card name below
            card_name = SMALL_FONT.render(f"{card.name} ({card.val})", True, CYAN)
            card_name_rect = card_name.get_rect(
                center=(card_x + CARD_WIDTH // 2, card_y + CARD_HEIGHT + 15)
            )
            WIN.blit(card_name, card_name_rect)

    # Draw number buttons if waiting for guess
    if hasattr(game_instance, "gameState"):
        if game_instance.gameState == "WAITING_FOR_GUESS":
            button_width = 60
            button_height = 60
            button_spacing = 10
            total_width = 7 * button_width + 6 * button_spacing
            start_x = WIDTH // 2 - total_width // 2
            button_y = HEIGHT // 2

            for num in range(2, 9):  # 2 through 8
                button_x = start_x + (num - 2) * (button_width + button_spacing)
                button_rect = pygame.Rect(
                    button_x, button_y, button_width, button_height
                )

                # Check if hovering
                is_hovering = button_rect.collidepoint(mouse_pos)

                # Draw button
                button_color = CYAN if is_hovering else PURPLE
                pygame.draw.rect(WIN, button_color, button_rect, border_radius=8)
                pygame.draw.rect(WIN, PINK, button_rect, 2, border_radius=8)

                # Draw number
                num_text = TEXT_FONT.render(str(num), True, FOREGROUND)
                num_rect = num_text.get_rect(center=button_rect.center)
                WIN.blit(num_text, num_rect)

                # Store for click detection
                number_buttons.append((num, button_rect))

    if hasattr(game_instance, "gameState"):
        if game_instance.gameState == "WAITING_FOR_CARD":
            prompt = TEXT_FONT.render("Select a card to play", True, YELLOW)
        elif game_instance.gameState == "WAITING_FOR_TARGET":
            prompt = TEXT_FONT.render("Select a target player", True, YELLOW)
        elif game_instance.gameState == "WAITING_FOR_GUESS":
            prompt = TEXT_FONT.render("Guess opponent's card (2-8)", True, YELLOW)
        else:
            prompt = TEXT_FONT.render("", True, YELLOW)
    else:
        # Fallback if gameState not implemented yet
        prompt = TEXT_FONT.render("Select a card to play", True, YELLOW)

    prompt_rect = prompt.get_rect(center=(WIDTH // 2, HEIGHT - 40))
    WIN.blit(prompt, prompt_rect)

    # Instructions
    instruction = SMALL_FONT.render("Press ESC to return to menu", True, COMMENT)
    WIN.blit(instruction, (20, HEIGHT - 30))

    pygame.display.update()

    # Return all clickable rectangles
    return card_rects, player_rects, number_buttons


def main(nameList=[]):
    run = True
    clock = pygame.time.Clock()

    # Game states
    STATE_MENU = 0
    STATE_GAME = 1

    state = STATE_MENU
    selected_player_count = 0
    game_instance = None

    # Store clickable elements
    card_rects = []
    player_rects = []
    number_buttons = []

    # Track mouse position
    mouse_pos = (0, 0)

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
                    if not nameList:
                        player_names = [
                            f"Player {i+1}" for i in range(selected_player_count)
                        ]
                    else:
                        player_names = nameList
                    try:
                        game_instance = GameInstance(player_names)
                        state = STATE_GAME
                    except ValueError as e:
                        print(f"Error creating game: {e}")

        elif state == STATE_GAME:
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

            # FIXED: Draw AFTER processing events, only once per frame
            if game_instance:
                card_rects, player_rects, number_buttons = draw_game_screen(
                    game_instance, mouse_pos
                )

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    pass
