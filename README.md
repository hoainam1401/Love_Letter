# Love Letter

A **multiplayer card game** implementation with both local Pygame-based gameplay and network multiplayer support. The project includes a Python backend with Pygame UI and a React/TypeScript frontend for browser-based gameplay.

## Technologies

### Backend
- **Python** - Game logic and server
- **Pygame** - Local game UI and rendering
- **Socket programming** - Network multiplayer

### Frontend
- **TypeScript** - Type-safe development
- **React** - UI components
- **Vite** - Build tool with fast refresh
- **SWC** - Fast TypeScript/JSX compilation

## Project Structure

```
Love_Letter/
├── Love_Letter_Base/     # Python backend
│   ├── card.py           # Card definitions
│   ├── card_pile.py      # Deck management
│   ├── player.py         # Player logic
│   ├── game.py           # Game logic
│   ├── main.py           # Local game entry point
│   ├── server.py         # Network server
│   ├── client.py         # Network client
│   └── images/           # Card images
├── Love_Letter_Frontend/ # React frontend
│   ├── src/              # React components
│   └── public/           # Static assets
└── Plan/                 # Documentation
```

## Current Features

- **Fully playable multiplayer** over LAN network
- **Core gameplay mechanics** implemented
- **Turn-based system** with real-time client-server communication
- **Local Pygame UI** for desktop play
- **Multiple game modes:**
  - Local game (single machine)
  - Network multiplayer (client-server)

## How to Run

### Backend - Local Game

```bash
git clone https://github.com/hoainam1401/Love_Letter.git
cd Love_Letter/Love_Letter_Base

# Install dependencies
pip install -r requirements.txt

# Run local game
python main.py
```

### Backend - Network Multiplayer

**Start Server:**
```bash
cd Love_Letter/Love_Letter_Base
python server.py
```

**Connect Clients:**
```bash
cd Love_Letter/Love_Letter_Base
python client.py
```

### Frontend - React Web Interface

```bash
cd Love_Letter/Love_Letter_Frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Planned Features

- Complete the **web-based GUI** for browser gameplay
- Implement **offline mode with AI bots**
- Finalize **frontend-backend integration**
- Add **game animations and transitions**
- Implement **user authentication and matchmaking**

## Screenshots

![Screenshot 1](Screenshots/img1.png)  
*Local Pygame interface*

![Screenshot 2](Screenshots/img2.png)  
*Network multiplayer gameplay*

## Development

### Code Style

**Python (Backend):**
- camelCase for variables/functions (non-standard convention)
- PascalCase for classes
- Type hints at class level

**TypeScript (Frontend):**
- Strict TypeScript enabled
- ESLint with React Hooks rules
- PascalCase for components, camelCase for functions

## License

This project is for educational purposes
