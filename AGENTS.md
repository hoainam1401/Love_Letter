# Repository Guide

## Project Boundaries

- The repository contains three divergent Pygame implementations, not one shared package. Change only the requested tree; do not copy fixes among `Love_Letter_Base/`, `Love_Letter_Base_offline/`, and `Love_Letter_Base_online/` without comparing their rules and UI first.
- `Love_Letter_Base_offline/` is the self-contained local game with AI. `main.py` owns the game loop and AI orchestration, `gui.py` owns rendering/input widgets, and `game.py`, `card.py`, `card_pile.py`, and `player.py` implement rules and state.
- `Love_Letter_Base/` is the older Pygame/socket implementation. Its `server.py` listens on TCP port 21011; run `main.py`, `server.py`, and `client.py` from this directory because image paths are relative to the working directory.
- `Love_Letter_Base_online/` contains two separate experiments: a Pygame socket client/server at its root and a Django/React web stack under `Love_Letter_Backend/` and `Love_Letter_Frontend/`. They are not integrated with each other.
- The online Pygame client is not ready for ordinary local use: `main.py` has `connect()` commented out and contains a hard-coded host (`25.14.115.139`). Do not treat that address as configuration or silently re-enable it.
- The root README's frontend path and TypeScript claim are stale. The actual frontend is `Love_Letter_Base_online/Love_Letter_Frontend/` and consists of JavaScript/JSX.

## Commands

- Offline desktop setup/run: `python -m pip install -r Love_Letter_Base_offline/requirements.txt`, then `cd Love_Letter_Base_offline && python main.py`.
- Frontend setup: `cd Love_Letter_Base_online/Love_Letter_Frontend && npm ci`. Vite 7 requires Node `^20.19.0` or `>=22.12.0`.
- Frontend checks: run `npm run lint` and `npm run build` from `Love_Letter_Base_online/Love_Letter_Frontend/`. There is no frontend test script.
- Frontend development: set `VITE_API_URL` to the Django origin, then run `npm run dev` from the frontend directory. API calls already include paths such as `/api/token/`.
- Django setup: install `Love_Letter_Base_online/Love_Letter_Backend/requirements.txt`, then run management commands from `Love_Letter_Base_online/Love_Letter_Backend/backend/`, where `manage.py` lives.
- Django development/checks: `python manage.py migrate`, `python manage.py runserver`, and `python manage.py test api`. `api/tests.py` is currently only a stub, so this does not cover game logic.

## Environment And Data

- Django uses PostgreSQL only; the SQLite configuration is commented out. Before any management command, provide `DJANGO_SECRET_KEY`, `SNAME`, `SUSER`, `SPASSWORD`, `SHOST`, and numeric `SPORT` (an ignored `.env` is loaded by settings). Missing `SPORT` fails during settings import.
- The Django user model is `api.Player`. Preserve `AUTH_USER_MODEL = "api.Player"`; model changes require migrations created from the directory containing `manage.py`.
- The React authentication flow depends on the Django JWT endpoints and stores access/refresh tokens in `localStorage`; changing endpoint paths requires checking `src/api.js`, `src/components/Form.jsx`, and `src/components/ProtectedRoute.jsx` together.

## Repository Quirks

- Pygame code intentionally uses camelCase methods and state fields. Avoid broad PEP 8 renames because socket payload keys and UI/game coordination use those names directly.
- `Love_Letter_Base_offline/build/` and `Love_Letter_Base_online/build/` are tracked pygbag 0.9.2 outputs, including APKs and web caches. Do not hand-edit them or include churn there unless the task explicitly rebuilds packaged artifacts.
- There are no automated tests for the Pygame game logic. For rule changes, inspect the relevant tree's `game.py` plus `card.py`/`player.py`, then manually exercise the affected state transition in that tree's UI.
