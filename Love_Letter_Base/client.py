import json
import socket
import threading
import pygame
import sys
import os

client: socket.socket
handName: list[str] = []
posInList = -1
currIndex = -1
gameState = "WAITING_FOR_TURN"
selectedCardIndex = -1
selectedTargetIndex = -1
selectedGuess = -1
nameList: list[str] = []
playerStatus: list[str] = []
hasCountess = 0
hasPrince = 0
hasKing = 0
remainingCount = -1
winningTokenCountList: list[int] = []
state = ""
gameStarted = False
valid = 0
STATE_MENU = 0
STATE_GAME = 1


# --------- NETWORK LOGIC ---------------
def connect():
    global client
    nickname = input("Please enter a nickname: ")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("25.14.115.139", 21011))  # lan ip of host
    print("You have connected to the server")

    # receive data from server
    def receive():
        client.sendall(nickname.encode())
        while True:
            try:
                global state, nameList, currIndex, playerStatus, hasCountess, hasPrince, hasKing, remainingCount, gameState, handName, posInList, gameStarted, valid, winningTokenCountList
                if not gameStarted:
                    # client.sendall("game started".encode())
                    pass
                data = client.recv(1024).decode()
                dataDict = json.loads(data)
                print(dataDict)
                posInList = int(dataDict["posInList"])
                nameList = dataDict["nameList"]
                currIndex = int(dataDict["currIndex"])
                playerStatus = dataDict["playerStatus"]
                hasCountess = int(dataDict["hasCountess"])
                hasKing = int(dataDict["hasKing"])
                hasPrince = int(dataDict["hasPrince"])
                remainingCount = int(dataDict["remainingCount"])
                gameState = dataDict["gameState"]
                print(f"Current state after receiving is: {gameState}")
                handName = dataDict["handName"]
                winningTokenCountList = dataDict["winningTokenCountList"]
                state = STATE_GAME
                valid = 0
            except Exception as e:
                print(f"An error occurred: {e}")
                client.close()
                break

    receive_thread = threading.Thread(target=receive)
    receive_thread.start()


def sendToServer():
    global gameState, client
    client.sendall(b"data")
    data = json.dumps(
        {
            "selectedCardIndex": selectedCardIndex,
            "selectedTargetIndex": selectedTargetIndex,
            "selectedGuess": selectedGuess,
            "valid": valid,
        }
    ).encode()
    client.sendall(data)
    print(data)
    print("Done packing")
    gameState = "WAITING_FOR_TURN"


# -------------- GAME ROUND LOGIC ---------------
# game runs based on user inputs in terminal
def cardNeedsTarget(cardName: str) -> bool:
    """Check if a card requires selecting a target player"""
    target_cards = [
        "Assassin",
        "Jester",
        "Priest",
        "Baron",
        "Sycophant",
        "Prince",
        "King",
        "Dowager Queen",
    ]
    return cardName in target_cards


def cardNeedsTwoTargets(cardName: str) -> bool:
    """Check if a card requires selecting 2 target players"""
    two_target_cards = ["Cardinal", "Baroness"]
    return cardName in two_target_cards


def cardNeedsGuess(cardName: str) -> bool:
    """Check if a card requires guessing a number"""
    return cardName in ["Guard", "Bishop"]


# check if card can target self
def cardSelfAllowed() -> bool:
    return handName[selectedCardIndex] in [
        "Cardinal",
        "Baroness",
        "Sycophant",
        "Prince",
    ]


def isValidTarget(playerIndex: int) -> bool:
    """Check if a player can be targeted"""
    if (
        playerIndex < 0
        or playerIndex >= len(nameList)
        or playerStatus[playerIndex] == "KO"
        or playerStatus[playerIndex] == "Protected"
    ):
        return False
    if playerIndex == posInList:
        return cardSelfAllowed()
    return True


# -------------- DURING PLAYER TURN ---------------
def selectCard(cardIndex: int):
    """Called when player clicks a card in their hand"""
    global gameState, selectedCardIndex, selectedTargetIndex, selectedGuess, handName, valid
    print(f"Game state while trying to select a card = {gameState}")
    if gameState != "WAITING_FOR_CARD":
        print("Not waiting for card selection!")
        return
    if (
        cardIndex < 0
        or cardIndex >= len(handName)
        or (
            hasCountess > 0
            and (hasPrince > 0 or hasKing > 0)
            and (handName[cardIndex] != "Countess")
        )
    ):
        print("Invalid card index!")
        return

    # Store the selection
    selectedCardIndex = cardIndex
    cardName = handName[cardIndex]
    valid = 0
    for i in range(len(nameList)):
        if isValidTarget(i):
            valid += 1
    # Card doesn't need any info or no valid target, play it immediately
    if (not cardNeedsGuess(cardName) and not cardNeedsTarget(cardName)) or valid == 0:
        # send data that you want to execute
        sendToServer()
    else:
        gameState = "WAITING_FOR_TARGET"
        print(f"Card {cardName} needs a target. Select a player.")


def selectTarget(playerIndex: int):
    """Called when player clicks a target player"""
    global gameState, selectedCardIndex, selectedTargetIndex, selectedGuess
    if gameState != "WAITING_FOR_TARGET":
        print("Not waiting for target selection!")
        return

    if not isValidTarget(playerIndex):
        print("Invalid target!")
        return

    # Store the selection
    selectedTargetIndex = playerIndex

    # Check if we also need a guess
    card = handName[selectedCardIndex]
    if cardNeedsGuess(card):
        gameState = "WAITING_FOR_GUESS"
        print("Now guess a number (2-8)")
    else:
        # We have everything we need
        sendToServer()


def selectGuess(guessNum: int):
    """Called when player clicks a number button"""
    global gameState, selectedCardIndex, selectedTargetIndex, selectedGuess
    if gameState != "WAITING_FOR_GUESS":
        print("Not waiting for guess!")
        return

    if guessNum < 2 or guessNum > 8:
        print("Invalid guess! Must be 2-8")
        return

    # Store the selection
    selectedGuess = guessNum

    # Now we have everything
    sendToServer()


# ------------- GAME UI ------------
FPS = 60
WIDTH = 1000
HEIGHT = 1000

pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Love Letter - Multiplayer")

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
SHADOW_BLACK = (0, 0, 0)  # Pure black for shadows

# Fonts
TITLE_FONT = pygame.font.Font(None, 96)  # Larger, bolder title
BUTTON_FONT = pygame.font.Font(None, 56)  # Larger buttons
TEXT_FONT = pygame.font.Font(None, 42)  # Larger text
SMALL_FONT = pygame.font.Font(None, 28)  # Larger small text

# Card dimensions - slightly larger for better visibility
CARD_WIDTH = 120
CARD_HEIGHT = 168


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

# Pre-create small card back for player boxes (avoid scaling every frame)
SMALL_CARD_BACK = pygame.transform.scale(CARD_IMAGES["Back"], (96, 134))


def draw_text_with_shadow(surface, text, font, color, x, y, shadow_offset=3):
    """Draw text with a shadow for depth"""
    # Draw shadow
    shadow_text = font.render(text, True, SHADOW_BLACK)
    surface.blit(shadow_text, (x + shadow_offset, y + shadow_offset))
    # Draw main text
    main_text = font.render(text, True, color)
    surface.blit(main_text, (x, y))
    return main_text.get_rect(topleft=(x, y))


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

    # Title with shadow
    title_text = "Love Letter - Multiplayer"
    # Draw multiple shadow layers for depth
    for i in range(3, 0, -1):
        shadow = TITLE_FONT.render(title_text, True, SHADOW_BLACK)
        shadow_rect = shadow.get_rect(center=(WIDTH // 2 + i * 2, 100 + i * 2))
        WIN.blit(shadow, shadow_rect)

    # Draw title with pink
    title = TITLE_FONT.render(title_text, True, PINK)
    title_rect = title.get_rect(center=(WIDTH // 2, 100))
    WIN.blit(title, title_rect)

    # Subtitle with shadow
    subtitle = TEXT_FONT.render("Waiting for host to start game...", True, FOREGROUND)
    subtitle_rect = subtitle.get_rect(center=(WIDTH // 2, 200))
    # Draw subtitle shadow
    shadow_sub = TEXT_FONT.render("Waiting for host to start game...", True, SHADOW_BLACK)
    WIN.blit(shadow_sub, (subtitle_rect.x + 2, subtitle_rect.y + 2))
    WIN.blit(subtitle, subtitle_rect)

    # Players info
    players_text = TEXT_FONT.render(f"Players in lobby: {len(nameList)}", True, CYAN)
    players_rect = players_text.get_rect(center=(WIDTH // 2, 300))
    shadow_players = TEXT_FONT.render(f"Players in lobby: {len(nameList)}", True, SHADOW_BLACK)
    WIN.blit(shadow_players, (players_rect.x + 2, players_rect.y + 2))
    WIN.blit(players_text, players_rect)

    # Start button (only if a selection is made)
    start_button = Button(WIDTH // 2 - 100, 600, 200, 70, "START", GREEN)
    start_button.draw(WIN)

    pygame.display.update()
    return start_button


def draw_game_screen(mouse_pos=(0, 0)):
    WIN.fill(BACKGROUND)
    # Track clickable card rectangles
    card_rects = []
    # Track clickable player rectangles
    player_rects = []
    # Track number buttons
    number_buttons = []

    global remainingCount, handName, posInList, winningTokenCountList

    # Title bar with shadow
    title_bar = pygame.Rect(0, 0, WIDTH, 90)
    # Draw shadow/depth
    pygame.draw.rect(WIN, SHADOW_BLACK, pygame.Rect(0, 4, WIDTH, 90))
    pygame.draw.rect(WIN, CURRENT_LINE, title_bar, border_radius=0)
    # Draw thick pink bottom border
    pygame.draw.rect(WIN, PINK, pygame.Rect(0, 86, WIDTH, 4))

    # Title with shadow
    title_shadow = TEXT_FONT.render("Love Letter - Multiplayer", True, SHADOW_BLACK)
    WIN.blit(title_shadow, (23, 28))
    title = TEXT_FONT.render("Love Letter - Multiplayer", True, PINK)
    WIN.blit(title, (20, 25))

    # Game info with shadow
    remaining_text_str = f"Deck: {remainingCount}"
    remaining_shadow = SMALL_FONT.render(remaining_text_str, True, SHADOW_BLACK)
    WIN.blit(remaining_shadow, (WIDTH - 148, 33))
    remaining_text = SMALL_FONT.render(remaining_text_str, True, CYAN)
    WIN.blit(remaining_text, (WIDTH - 150, 30))

    # Draw deck (card back) in center of screen
    deck_x = WIDTH // 2 - CARD_WIDTH // 2
    deck_y = HEIGHT // 2 - CARD_HEIGHT // 2

    # Draw multiple card backs stacked to show deck with shadows
    if remainingCount > 0:
        for i in range(min(4, remainingCount)):
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
    for i in range(posInList):
        player_positions.insert(0, player_positions.pop())

    for i in range(len(nameList)):
        x, y = player_positions[i]

        # Player info box
        box_width = 200
        box_height = 180
        box_rect = pygame.Rect(x, y, box_width, box_height)

        # Check if this player can be targeted
        is_valid_target = False
        if gameState == "WAITING_FOR_TARGET":
            is_valid_target = isValidTarget(i)
            if is_valid_target:
                player_rects.append((i, box_rect))

        # Check if hovering over this player
        is_hovering = box_rect.collidepoint(mouse_pos)
        
        # Color based on state
        if playerStatus[i] == "KO":
            box_color = RED
            border_color = DARK_GRAY
        elif i == currIndex:
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
        for j in range(border_width):
            border_rect = box_rect.inflate(-j * 2, -j * 2)
            pygame.draw.rect(WIN, border_color, border_rect, 2, border_radius=10)

        # Player name with shadow
        name_shadow = TEXT_FONT.render(nameList[i], True, SHADOW_BLACK)
        name_rect = name_shadow.get_rect(center=(x + box_width // 2 + 2, y + 27))
        WIN.blit(name_shadow, name_rect)

        name_surface = TEXT_FONT.render(nameList[i], True, FOREGROUND)
        name_rect = name_surface.get_rect(center=(x + box_width // 2, y + 25))
        WIN.blit(name_surface, name_rect)

        # Status with appropriate color
        status = (
            "KNOCKED OUT"
            if playerStatus[i] == "KO"
            else "Protected" if playerStatus[i] == "Protected" else "Active"
        )
        status_color = RED if playerStatus[i] == "KO" else CYAN if playerStatus[i] == "Protected" else GREEN

        status_shadow = SMALL_FONT.render(status, True, SHADOW_BLACK)
        status_rect = status_shadow.get_rect(center=(x + box_width // 2 + 2, y + 57))
        WIN.blit(status_shadow, status_rect)

        status_surface = SMALL_FONT.render(status, True, status_color)
        status_rect = status_surface.get_rect(center=(x + box_width // 2, y + 55))
        WIN.blit(status_surface, status_rect)

        # Tokens with yellow color
        tokens_str = f"Tokens: {winningTokenCountList[i]}"
        tokens_shadow = SMALL_FONT.render(tokens_str, True, SHADOW_BLACK)
        tokens_rect = tokens_shadow.get_rect(center=(x + box_width // 2 + 2, y + 87))
        WIN.blit(tokens_shadow, tokens_rect)

        tokens = SMALL_FONT.render(tokens_str, True, YELLOW)
        tokens_rect = tokens.get_rect(center=(x + box_width // 2, y + 85))
        WIN.blit(tokens, tokens_rect)

        # Show card back if player has cards (but not the current player)
        if playerStatus[i] != "KO" and i != posInList:
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
    player_rects.sort(key=lambda tup: tup[0])

    # Draw current player's hand at bottom center with actual card images
    if len(handName) > 0:
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

        # Draw cards with images
        total_cards = len(handName)
        start_x = WIDTH // 2 - (total_cards * (CARD_WIDTH + 20) - 20) // 2

        for idx, cardName in enumerate(handName):
            card_x = start_x + idx * (CARD_WIDTH + 20)
            card_y = hand_y + 10

            # Create a rect for this card and store it
            card_rect = pygame.Rect(card_x, card_y, CARD_WIDTH, CARD_HEIGHT)
            card_rects.append(card_rect)

            # Check if mouse is hovering
            is_hovering = card_rect.collidepoint(mouse_pos)

            # Draw highlight if hovering and clickable
            can_click = True
            can_click = gameState == "WAITING_FOR_CARD"

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
            WIN.blit(CARD_IMAGES[cardName], (card_x, card_y))

            # Draw thick pink border
            border_color = YELLOW if is_hovering and can_click else PINK
            for i in range(3):
                border_rect = card_rect.inflate(-i * 2, -i * 2)
                pygame.draw.rect(WIN, border_color, border_rect, 2, border_radius=10)

            # Draw card name below with shadow
            card_name_str = f"{cardName}"
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
    if gameState == "WAITING_FOR_GUESS":
        button_width = 70
        button_height = 70
        button_spacing = 15
        total_width = 7 * button_width + 6 * button_spacing
        start_x = WIDTH // 2 - total_width // 2
        button_y = HEIGHT // 2 - 20

        for num in range(2, 9):  # 2 through 8
            button_x = start_x + (num - 2) * (button_width + button_spacing)
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

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

    # Draw prompts with emphasis
    if gameState == "WAITING_FOR_CARD":
        prompt_text = "Select a card to play"
        prompt_color = GREEN
    elif gameState == "WAITING_FOR_TARGET":
        prompt_text = "Select a target player"
        prompt_color = ORANGE
    elif gameState == "WAITING_FOR_GUESS":
        prompt_text = "Guess opponent's card (2-8)"
        prompt_color = CYAN
    else:
        prompt_text = "Waiting for your turn..."
        prompt_color = FOREGROUND

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
    return card_rects, player_rects, number_buttons


def main():
    run = True
    clock = pygame.time.Clock()

    # Game states
    global state, gameState, handName
    state = STATE_MENU
    selected_player_count = 0

    # Store clickable elements
    card_rects = []
    player_rects = []
    number_buttons = []

    # Track mouse position
    mouse_pos = (0, 0)

    while run:
        clock.tick(FPS)

        if state == STATE_MENU:
            start_button = draw_player_selection_screen(selected_player_count)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                # Check start button
                if start_button and start_button.handle_event(event):
                    client.sendall("message".encode())
                    client.sendall("start".encode())

        elif state == STATE_GAME:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # Return to menu
                        state = STATE_MENU
                        selected_player_count = 0

                # Track mouse motion
                elif event.type == pygame.MOUSEMOTION:
                    mouse_pos = event.pos

                # Handle mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    # Check if clicked on a card
                    if len(card_rects) > 0:
                        for idx, rect in enumerate(card_rects):
                            if rect.collidepoint(mouse_pos):
                                print(f"Clicked card {idx}: {handName[idx]}")
                                selectCard(idx)
                                # reset selection
                                selectedCardIndex = -1
                                selectedTargetIndex = -1
                                selectedGuess = -1
                                break  # Only handle one click

                    # Check if clicked on a player
                    if len(player_rects) > 0:
                        for player_idx, rect in player_rects:
                            if rect.collidepoint(mouse_pos):
                                print(
                                    f"Clicked player {player_idx}: {nameList[player_idx]}"
                                )
                                selectTarget(player_idx)
                                # reset selection
                                selectedCardIndex = -1
                                selectedTargetIndex = -1
                                selectedGuess = -1
                                break

                    # Check if clicked on a number button
                    if len(number_buttons) > 0:
                        for num, rect in number_buttons:
                            if rect.collidepoint(mouse_pos):
                                print(f"Guessed number: {num}")
                                selectGuess(num)
                                # reset selection
                                selectedCardIndex = -1
                                selectedTargetIndex = -1
                                selectedGuess = -1
                                break
            card_rects, player_rects, number_buttons = draw_game_screen(mouse_pos)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    connect()
    main()
