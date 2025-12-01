import pygame  # type: ignore
import sys
from game import GameInstance

FPS = 60
WIDTH = 1000
HEIGHT = 800

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

# Fonts
TITLE_FONT = pygame.font.Font(None, 72)
BUTTON_FONT = pygame.font.Font(None, 48)
TEXT_FONT = pygame.font.Font(None, 36)
SMALL_FONT = pygame.font.Font(None, 24)


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
    WIN.fill(WHITE)

    # Title
    title = TEXT_FONT.render("Love Letter - Game in Progress", True, BLACK)
    WIN.blit(title, (20, 20))

    # Game info
    remaining = SMALL_FONT.render(
        f"Cards remaining: {game_instance.remainingCount()}", True, BLACK
    )
    WIN.blit(remaining, (20, 70))

    current = SMALL_FONT.render(
        f"Current player: {game_instance.currPlayer.name}", True, RED
    )
    WIN.blit(current, (20, 100))

    # Draw players in a circle-like layout
    player_positions = [
        (WIDTH // 2 - 200, HEIGHT - 200),  # Bottom left (main player)
        (100, HEIGHT // 2 - 100),  # Left
        (WIDTH // 2 - 100, 150),  # Top
        (WIDTH - 250, HEIGHT // 2 - 100),  # Right
    ]

    for i, player in enumerate(game_instance.playerList):
        x, y = player_positions[i]

        # Player box
        box_rect = pygame.Rect(x, y, 200, 150)
        color = GREEN if player == game_instance.currPlayer else GRAY
        if player.isKO:
            color = RED

        pygame.draw.rect(WIN, color, box_rect)
        pygame.draw.rect(WIN, BLACK, box_rect, 3)

        # Player name
        name_surface = TEXT_FONT.render(player.name, True, BLACK)
        name_rect = name_surface.get_rect(center=(x + 100, y + 30))
        WIN.blit(name_surface, name_rect)

        # Status
        status = (
            "KNOCKED OUT"
            if player.isKO
            else "Protected" if player.hasHandmaid else "Active"
        )
        status_surface = SMALL_FONT.render(status, True, BLACK)
        status_rect = status_surface.get_rect(center=(x + 100, y + 60))
        WIN.blit(status_surface, status_rect)

        # Tokens
        tokens = SMALL_FONT.render(f"Tokens: {player.winningTokenCount}", True, BLACK)
        tokens_rect = tokens.get_rect(center=(x + 100, y + 90))
        WIN.blit(tokens, tokens_rect)

        # Card count
        cards = SMALL_FONT.render(f"Cards: {len(player.hand)}", True, BLACK)
        cards_rect = cards.get_rect(center=(x + 100, y + 120))
        WIN.blit(cards, cards_rect)

    # Draw current player's hand at bottom
    if len(game_instance.currPlayer.hand) > 0:
        hand_y = HEIGHT - 50
        hand_text = SMALL_FONT.render("Your hand: ", True, BLACK)
        WIN.blit(hand_text, (20, hand_y))

        x_offset = 150
        for card in game_instance.currPlayer.hand:
            card_text = SMALL_FONT.render(f"{card.name} ({card.val})", True, BLUE)
            WIN.blit(card_text, (x_offset, hand_y))
            x_offset += 150

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
