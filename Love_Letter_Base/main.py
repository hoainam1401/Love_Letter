import pygame  # type: ignore
import sys
import os
from game import GameInstance

FPS = 60
WIDTH = 1200
HEIGHT = 900

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Love Letter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BLUE = (100, 150, 255)
GREEN = (100, 200, 100)
RED = (200, 100, 100)
LIGHT_BROWN = (210, 180, 140)
DARK_BROWN = (101, 67, 33)

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
            surf.fill(WHITE)
            pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
            font = pygame.font.Font(None, 20)
            text = font.render(name, True, BLACK)
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
        surf.fill(DARK_BROWN)
        pygame.draw.rect(surf, BLACK, surf.get_rect(), 2)
        card_images["Back"] = surf

    return card_images


CARD_IMAGES = load_card_images()


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surface):
        color = DARK_GRAY if self.hover else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)

        text_surface = BUTTON_FONT.render(self.text, True, WHITE)
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
    WIN.fill(WHITE)

    # Title
    title = TITLE_FONT.render("Love Letter", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    WIN.blit(title, title_rect)

    # Subtitle
    subtitle = TEXT_FONT.render("Select Number of Players (2-4)", True, DARK_GRAY)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
    WIN.blit(subtitle, subtitle_rect)

    # Player count buttons
    buttons = []
    for i in range(2, 5):
        x = WIDTH // 2 - 100
        y = 280 + (i - 2) * 100
        color = GREEN if i == selected_count else BLUE
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


def draw_game_screen(game_instance):
    WIN.fill(LIGHT_BROWN)

    # Title bar
    title_bar = pygame.Rect(0, 0, WIDTH, 80)
    pygame.draw.rect(WIN, DARK_BROWN, title_bar)
    title = TEXT_FONT.render("Love Letter", True, WHITE)
    WIN.blit(title, (20, 25))

    # Game info
    remaining_text = SMALL_FONT.render(
        f"Cards in deck: {game_instance.remainingCount()}", True, WHITE
    )
    WIN.blit(remaining_text, (WIDTH - 200, 30))

    # Draw deck (card back) in center-top area
    deck_x = WIDTH // 2 - CARD_WIDTH // 2
    deck_y = 120

    # Draw multiple card backs stacked to show deck
    if game_instance.remainingCount() > 0:
        for i in range(min(3, game_instance.remainingCount())):
            offset = i * 3
            WIN.blit(CARD_IMAGES["Back"], (deck_x + offset, deck_y + offset))

        deck_label = SMALL_FONT.render("DECK", True, BLACK)
        deck_label_rect = deck_label.get_rect(
            center=(deck_x + CARD_WIDTH // 2, deck_y + CARD_HEIGHT + 20)
        )
        WIN.blit(deck_label, deck_label_rect)

    # Draw players in a layout
    player_positions = [
        (WIDTH // 2 - 320, HEIGHT - 250),  # Bottom left (player 1)
        (50, HEIGHT // 2 - 150),  # Left (player 2)
        (WIDTH // 2 - 100, 100),  # Top (player 3)
        (WIDTH - 250, HEIGHT // 2 - 150),  # Right (player 4)
    ]

    for i, player in enumerate(game_instance.playerList):
        x, y = player_positions[i]

        # Player info box
        box_width = 200
        box_height = 180
        box_rect = pygame.Rect(x, y, box_width, box_height)

        # Color based on state
        if player.isKO:
            box_color = RED
        elif player == game_instance.currPlayer:
            box_color = GREEN
        else:
            box_color = GRAY

        pygame.draw.rect(WIN, box_color, box_rect)
        pygame.draw.rect(WIN, BLACK, box_rect, 3)

        # Player name
        name_surface = TEXT_FONT.render(player.name, True, BLACK)
        name_rect = name_surface.get_rect(center=(x + box_width // 2, y + 25))
        WIN.blit(name_surface, name_rect)

        # Status
        status = (
            "KNOCKED OUT"
            if player.isKO
            else "Protected" if player.hasHandmaid else "Active"
        )
        status_surface = SMALL_FONT.render(status, True, BLACK)
        status_rect = status_surface.get_rect(center=(x + box_width // 2, y + 55))
        WIN.blit(status_surface, status_rect)

        # Tokens
        tokens = SMALL_FONT.render(f"Tokens: {player.winningTokenCount}", True, BLACK)
        tokens_rect = tokens.get_rect(center=(x + box_width // 2, y + 85))
        WIN.blit(tokens, tokens_rect)

        # Show card back if player has cards (but not the current player)
        if len(player.hand) > 0 and player != game_instance.currPlayer:
            card_x = x + (box_width - 80) // 2
            card_y = y + 110
            small_card = pygame.transform.scale(CARD_IMAGES["Back"], (80, 112))
            WIN.blit(small_card, (card_x, card_y))

    # Draw current player's hand at bottom center with actual card images
    if len(game_instance.currPlayer.hand) > 0:
        hand_y = HEIGHT - 180

        # Background for hand area
        hand_bg = pygame.Rect(WIDTH // 2 - 300, hand_y - 20, 600, 170)
        pygame.draw.rect(WIN, WHITE, hand_bg)
        pygame.draw.rect(WIN, BLACK, hand_bg, 3)

        hand_label = TEXT_FONT.render("Your Hand", True, BLACK)
        WIN.blit(hand_label, (WIDTH // 2 - 70, hand_y - 15))

        # Draw cards with images
        total_cards = len(game_instance.currPlayer.hand)
        start_x = WIDTH // 2 - (total_cards * (CARD_WIDTH + 20) - 20) // 2

        for idx, card in enumerate(game_instance.currPlayer.hand):
            card_x = start_x + idx * (CARD_WIDTH + 20)
            card_y = hand_y + 20

            # Draw card image
            WIN.blit(CARD_IMAGES[card.name], (card_x, card_y))

            # Draw card name below
            card_name = SMALL_FONT.render(f"{card.name} ({card.val})", True, BLACK)
            card_name_rect = card_name.get_rect(
                center=(card_x + CARD_WIDTH // 2, card_y + CARD_HEIGHT + 15)
            )
            WIN.blit(card_name, card_name_rect)

    # Instructions
    instruction = SMALL_FONT.render("Press ESC to return to menu", True, BLACK)
    WIN.blit(instruction, (20, HEIGHT - 30))

    pygame.display.update()


def main():
    run = True
    clock = pygame.time.Clock()

    # Game states
    STATE_MENU = 0
    STATE_GAME = 1

    state = STATE_MENU
    selected_player_count = 0
    game_instance = None

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
            if game_instance:
                draw_game_screen(game_instance)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to menu
                        state = STATE_MENU
                        selected_player_count = 0
                        game_instance = None

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
