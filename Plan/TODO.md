# Love Letter Game Development - TODO & Learning Plan

## 📋 Project Overview
**Goal:** Build a digital version of the Love Letter card game using Python and Pygame  
**Team Size:** 2 people  
**Timeline:** 4-6 weeks (flexible based on experience level)  
**Difficulty:** Beginner to Intermediate

---

## 🎓 Learning Prerequisites

### Phase 0: Foundation Knowledge (Week 1)

#### Python Fundamentals (Required for both team members)
- [ ] Variables, data types, and operators
- [ ] Control flow (if/else, loops)
- [ ] Functions and parameters
- [ ] Lists, dictionaries, and tuples
- [ ] Classes and Object-Oriented Programming (OOP)
  - [ ] Classes and objects
  - [ ] Attributes and methods
  - [ ] Inheritance
  - [ ] Encapsulation
- [ ] File I/O (for saving game state)
- [ ] Error handling (try/except)

**Resources:**
- Python Official Tutorial: https://docs.python.org/3/tutorial/
- Automate the Boring Stuff: https://automatetheboringstuff.com/
- Real Python Tutorials: https://realpython.com/  

#### Pygame Basics (Required for both team members)
- [ ] Installing Pygame (`pip install pygame`)
- [ ] Understanding the game loop
- [ ] Creating a window
- [ ] Drawing shapes and images
- [ ] Handling events (mouse, keyboard)
- [ ] Working with surfaces and blitting
- [ ] Using sprite groups
- [ ] Loading and playing sounds
- [ ] Text rendering with fonts
- [ ] Collision detection
- [ ] Frame rate control (Clock)

**Resources:**
- Pygame Documentation: https://www.pygame.org/docs/
- Pygame Tutorial (Real Python): https://realpython.com/pygame-a-primer/
- Tech With Tim Pygame Series: YouTube
- Clear Code Pygame Tutorials: YouTube

#### Game Design Concepts
- [ ] Game state management
  - [ ] Menu state
  - [ ] Playing state
  - [ ] Pause state
  - [ ] Game over state
- [ ] Game loop architecture
  - [ ] Input handling
  - [ ] Update logic
  - [ ] Rendering
- [ ] Turn-based game mechanics
- [ ] UI/UX for card games
  - [ ] Card layout and arrangement
  - [ ] Visual feedback
  - [ ] Player information display
- [ ] AI basics (for computer opponents)
  - [ ] Random decision making
  - [ ] Simple strategy patterns

**Resources:**
- Game Programming Patterns: https://gameprogrammingpatterns.com/
- Extra Credits (YouTube): Game Design series
- GDC Talks on card game design

#### Love Letter Game Rules (CRITICAL - Both team members)
- [ ] Understand all 8 card types and their effects:
  - [ ] Guard (5 cards, value 1): Guess opponent's card
  - [ ] Priest (2 cards, value 2): Look at opponent's hand
  - [ ] Baron (2 cards, value 3): Compare hands, lower loses
  - [ ] Handmaid (2 cards, value 4): Protection until next turn
  - [ ] Prince (2 cards, value 5): Force discard and draw
  - [ ] King (1 card, value 6): Trade hands with opponent
  - [ ] Countess (1 card, value 7): Must discard if holding King/Prince
  - [ ] Princess (1 card, value 8): Lose if discarded
- [ ] Game flow and turn structure
- [ ] Win conditions (last player standing or highest card)
- [ ] Round and game scoring
- [ ] 2-4 player rules

**Resources:**
- Official rulebook (PDF available online)
- Board Game Arena (play online to learn)
- YouTube playthrough videos

---

## 👥 Team Division of Labor

### Person 1: Game Logic Lead
**Focus:** Backend/Core mechanics

#### Responsibilities:
- Game rules implementation
- Card system and effects
- Player management
- Game state machine
- Win condition logic
- AI opponent (basic)

### Person 2: UI/Graphics Lead
**Focus:** Frontend/Visual experience

#### Responsibilities:
- Pygame rendering system
- Card graphics and animations
- User interface design
- Input handling (mouse/keyboard)
- Sound effects integration
- Visual feedback and polish

**Note:** Both team members should understand both parts, but have primary ownership of their area.

---

## 📅 Development Timeline (6 Weeks)

### Week 1: Learning & Setup
**Both Team Members:**
- [ ] Complete Python OOP fundamentals
- [ ] Complete Pygame basics tutorials
- [ ] Play Love Letter (physically or digitally) 5+ times
- [ ] Set up development environment
  - [ ] Install Python 3.8+
  - [ ] Install Pygame
  - [ ] Set up Git repository
  - [ ] Choose code editor (VS Code recommended)
- [ ] Create project structure
- [ ] Set up version control (Git)
- [ ] Define coding standards and file organization

**Deliverable:** Project setup complete, team understands the game

---

### Week 2: Core Game Logic (Person 1 Lead)
**Person 1 Tasks:**
- [ ] Create Card class
  - [ ] Card types enum
  - [ ] Card value and name
  - [ ] Card effect method stub
- [ ] Create Deck class
  - [ ] Initialize 16 cards (correct distribution)
  - [ ] Shuffle method
  - [ ] Draw method
  - [ ] Remove set-aside card
- [ ] Create Player class
  - [ ] Hand (1-2 cards)
  - [ ] Discarded cards list
  - [ ] Protection status
  - [ ] Eliminated status
  - [ ] Score tracking
- [ ] Create basic Game class
  - [ ] Initialize players
  - [ ] Start round
  - [ ] Manage turn order
  - [ ] Check win conditions

**Person 2 Tasks:**
- [ ] Create basic Pygame window (800x600)
- [ ] Implement game loop structure
- [ ] Set up constants file (colors, sizes, positions)
- [ ] Create placeholder graphics
  - [ ] Card back design
  - [ ] Card front template
- [ ] Research card game UI layouts

**Collaboration:**
- [ ] Daily check-ins (15 minutes)
- [ ] Code review session (end of week)
- [ ] Document class interfaces

**Deliverable:** Game logic works in console (no graphics), basic window renders

---

### Week 3: Card Effects & Basic UI (Shared Work)
**Person 1 Tasks:**
- [ ] Implement all 8 card effects
  - [ ] Guard effect (requires target + guess)
  - [ ] Priest effect (reveal card)
  - [ ] Baron effect (comparison)
  - [ ] Handmaid effect (set protection)
  - [ ] Prince effect (requires target)
  - [ ] King effect (requires target)
  - [ ] Countess effect (passive)
  - [ ] Princess effect (auto-lose)
- [ ] Add effect validation
- [ ] Handle edge cases (all players protected, etc.)
- [ ] Write unit tests for each card

**Person 2 Tasks:**
- [ ] Draw cards on screen
  - [ ] Card positioning system
  - [ ] Card sprite class
  - [ ] Card flip animation
- [ ] Display player hands
- [ ] Show discard pile
- [ ] Create text rendering system
  - [ ] Player names
  - [ ] Game messages
  - [ ] Card information
- [ ] Add mouse hover effects on cards

**Collaboration:**
- [ ] Integrate game logic with UI
- [ ] Test card playing visually
- [ ] Pair programming session for integration

**Deliverable:** All cards functional, cards visible and clickable on screen

---

### Week 4: Player Interaction & Game Flow (Shared Work)
**Person 1 Tasks:**
- [ ] Implement turn management
  - [ ] Current player indicator
  - [ ] Turn advancement
  - [ ] Round end detection
- [ ] Add player selection for targeted effects
- [ ] Implement game state transitions
  - [ ] Start game → Deal cards
  - [ ] Playing → Round end
  - [ ] Round end → Next round
  - [ ] Game end → Winner display
- [ ] Add input validation
- [ ] Create game history/log system

**Person 2 Tasks:**
- [ ] Create main menu
  - [ ] Start game button
  - [ ] Number of players selection (2-4)
  - [ ] Quit button
- [ ] Add player selection UI
  - [ ] Click to target opponent
  - [ ] Highlight selectable players
- [ ] Implement card selection for Guard (guess menu)
- [ ] Add game information panel
  - [ ] Current turn
  - [ ] Scores
  - [ ] Round number
- [ ] Create victory screen
- [ ] Add button class for reusability

**Collaboration:**
- [ ] Connect menu to game start
- [ ] Test complete game flow
- [ ] Playtest with 2-4 players

**Deliverable:** Playable game from start to finish (hot-seat multiplayer)

---

### Week 5: Polish & AI (Divided Work)
**Person 1 Tasks:**
- [ ] Implement AI opponent
  - [ ] Random card selection (basic)
  - [ ] Valid target selection
  - [ ] Random Guard guessing
  - [ ] (Optional) Smarter AI strategies
- [ ] Add difficulty levels (Easy/Medium)
- [ ] Save/load game state
- [ ] Bug fixes from playtesting
- [ ] Code refactoring and cleanup

**Person 2 Tasks:**
- [ ] Add animations
  - [ ] Card dealing animation
  - [ ] Card play animation
  - [ ] Card discard animation
  - [ ] Elimination effects
- [ ] Add visual feedback
  - [ ] Highlight current player
  - [ ] Show protected players (shield icon)
  - [ ] Show eliminated players (greyed out)
- [ ] Add sound effects
  - [ ] Card play sound
  - [ ] Victory sound
  - [ ] Button click sound
- [ ] Add background music
- [ ] Polish UI (colors, spacing, fonts)
- [ ] Add game rules screen

**Collaboration:**
- [ ] Extensive playtesting
- [ ] Balance AI difficulty
- [ ] Test all edge cases
- [ ] Performance optimization

**Deliverable:** Polished game with AI, animations, and sound

---

### Week 6: Testing & Final Touches
**Both Team Members:**
- [ ] Comprehensive testing
  - [ ] Test all card combinations
  - [ ] Test with 2, 3, and 4 players
  - [ ] Test AI behavior
  - [ ] Test all UI interactions
- [ ] Bug fixing
- [ ] Performance optimization
- [ ] Add settings menu
  - [ ] Sound volume control
  - [ ] Fullscreen toggle
- [ ] Create README with instructions
- [ ] Add credits screen
- [ ] Package game for distribution
  - [ ] (Optional) Use PyInstaller for executable
- [ ] Final code cleanup and documentation
- [ ] Celebrate completion!

**Deliverable:** Finished, polished, and distributable game

---

## 🗂️ Project Structure

```
love-letter-pygame/
├── main.py                 # Entry point, game loop
├── game.py                 # Game state management
├── card.py                 # Card class and effects
├── deck.py                 # Deck management
├── player.py               # Player class
├── ai.py                   # AI opponent logic
├── ui.py                   # UI helper functions
├── button.py               # Button class
├── constants.py            # Game constants (colors, sizes)
├── utils.py                # Utility functions
├── assets/
│   ├── images/
│   │   ├── cards/          # Card images (guard.png, priest.png, etc.)
│   │   ├── backgrounds/    # Background images
│   │   └── icons/          # UI icons
│   ├── fonts/
│   │   └── game_font.ttf   # Game font
│   └── sounds/
│       ├── card_play.wav
│       ├── victory.wav
│       └── background.mp3
├── tests/
│   ├── test_card.py
│   ├── test_game.py
│   └── test_player.py
├── requirements.txt        # Python dependencies
├── README.md              # Game instructions
└── TODO.md                # This file!
```

---

## 🛠️ Technical Implementation Details

### Game State Machine
```
MENU → SETUP → PLAYING → ROUND_END → GAME_OVER
                   ↑          |
                   └──────────┘
```

### Core Classes

#### Card Class
```python
class Card:
    def __init__(self, name, value, effect_description):
        self.name = name
        self.value = value
        self.effect_description = effect_description
    
    def play(self, game, player, target=None, guess=None):
        # Implement card-specific effect
        pass
```

#### Player Class
```python
class Player:
    def __init__(self, name, is_ai=False):
        self.name = name
        self.hand = []
        self.discarded = []
        self.is_protected = False
        self.is_eliminated = False
        self.score = 0
        self.is_ai = is_ai
```

#### Game Class
```python
class Game:
    def __init__(self, num_players):
        self.players = []
        self.deck = Deck()
        self.current_player_index = 0
        self.round_number = 1
        self.game_log = []
    
    def start_round(self):
        # Reset, shuffle, deal
        pass
    
    def play_turn(self, card, target=None, guess=None):
        # Execute card effect
        pass
    
    def check_round_end(self):
        # Check win conditions
        pass
```

---

## 🎨 Design Guidelines

### Card Dimensions
- Card size: 100x140 pixels
- Card spacing: 10 pixels
- Border radius: 10 pixels (rounded corners)

### Color Scheme (Suggested)
- Background: #2C3E50 (dark blue-grey)
- Card background: #ECF0F1 (light grey)
- Card border: #34495E (darker grey)
- Highlight color: #F39C12 (orange)
- Protected player: #3498DB (blue)
- Eliminated player: #E74C3C (red)
- Current player: #2ECC71 (green)

### Fonts
- Title: 36pt bold
- Card names: 18pt bold
- Card values: 48pt bold
- Body text: 14pt regular

---

## 🧪 Testing Checklist

### Card Effect Tests
- [ ] Guard correctly eliminates on correct guess
- [ ] Guard does nothing on wrong guess
- [ ] Priest reveals opponent's card
- [ ] Baron compares cards correctly
- [ ] Baron handles ties
- [ ] Handmaid protects until next turn
- [ ] Prince forces discard/draw
- [ ] Prince can target self
- [ ] Prince eliminates if Princess discarded
- [ ] King swaps hands
- [ ] Countess auto-discards with King/Prince
- [ ] Princess eliminates player

### Game Flow Tests
- [ ] 2-player game works
- [ ] 3-player game works
- [ ] 4-player game works
- [ ] Round ends when one player remains
- [ ] Round ends when deck is empty
- [ ] Highest card wins when deck empty
- [ ] Scores increment correctly
- [ ] Game ends at target score
- [ ] New round resets properly

### UI Tests
- [ ] Cards are clickable
- [ ] Player selection works
- [ ] Protected players can't be targeted
- [ ] Eliminated players can't play
- [ ] Animations don't break game logic
- [ ] Buttons respond to clicks
- [ ] Game is playable at different resolutions

---

## 📚 Additional Resources

### Python & Pygame
- Pygame Zero (simpler alternative): https://pygame-zero.readthedocs.io/
- Pygame Community: https://www.reddit.com/r/pygame/
- Python Discord server
- Stack Overflow

### Game Development
- itch.io (for inspiration and publishing)
- OpenGameArt.org (free game assets)
- LÖVE framework (Lua alternative to compare)

### Love Letter Specific
- BoardGameGeek page
- Strategy guides (for AI development)
- Variant rules (for future expansion)

---

## 🚀 Future Enhancements (After Core Game Complete)

### Phase 2 Features
- [ ] Online multiplayer (using sockets)
- [ ] Player statistics tracking
- [ ] Achievements system
- [ ] Different card back designs
- [ ] Custom player avatars
- [ ] Replay system
- [ ] Tournament mode
- [ ] Leaderboard

### Phase 3 Features
- [ ] Love Letter: Premium Edition cards
- [ ] Custom game modes
- [ ] Modding support
- [ ] Mobile version (Pygame subset)
- [ ] Spectator mode
- [ ] Tutorial mode with interactive guide

---

## 💡 Tips for Success

### For Both Team Members:
1. **Start Simple**: Get a basic working version before adding polish
2. **Test Often**: Playtest after every major feature
3. **Use Version Control**: Commit frequently with clear messages
4. **Communicate Daily**: Quick updates prevent merge conflicts
5. **Ask for Help**: Use Stack Overflow, Discord, Reddit
6. **Take Breaks**: Avoid burnout, game dev should be fun!
7. **Play the Original**: Understanding the game deeply is crucial

### Code Best Practices:
- Write docstrings for all classes and functions
- Use meaningful variable names
- Keep functions small and focused
- Comment complex logic
- Follow PEP 8 style guide for Python
- Don't repeat code (DRY principle)

### Collaboration Tips:
- Use Git branches for features
- Review each other's code
- Pair program on complex features
- Celebrate small wins together
- Be patient and supportive

---

## 🎯 Success Criteria

Your game is complete when:
- ✅ All 8 cards work correctly
- ✅ 2-4 player games run smoothly
- ✅ Basic AI opponent is playable
- ✅ Game has clear visual feedback
- ✅ No game-breaking bugs
- ✅ Game is fun to play!

---

## 📝 Notes Section
(Use this space to track ideas, bugs, and questions)

### Ideas:
- 

### Known Bugs:
- 

### Questions:
- 

### Team Progress Notes:
- 

---

**Good luck with your Love Letter game development! Remember: start small, test often, and have fun building! 🎮✨**
