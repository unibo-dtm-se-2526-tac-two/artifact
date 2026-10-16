
# Tac²

![Status](https://img.shields.io/badge/status-in%20development-orange)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Vue.js](https://img.shields.io/badge/Vue.js-frontend-42b883?logo=vuedotjs&logoColor=white)
![License](https://img.shields.io/badge/License-Apache%202.0-lightgrey?logo=apache)

A two-player, two-level tic-tac-toe strategy game featuring forced-board moves and a chess clock.

## Project Overview


## Project Overview

**Tac²** is a two-player strategy game that expands classic tic-tac-toe into two levels: a large 3×3 grid containing nine smaller tic-tac-toe boards.

The objective is to win three small boards in a row, column, or diagonal on the larger board. Each move determines which small board the opponent must play in next. If the designated board has already been won or is full, the opponent can choose another available board.

The game features a chess clock, with a configurable time limit (e.g., five minutes per player). A player who runs out of time loses the game.

Beyond the core game mechanics, Tac² aims to provide user accounts, an interactive tutorial, multiple game modes, a global leaderboard, and personal statistics.

## How to Play

1. **Play a move.** Place your mark in an available cell of the current small board.
2. **Determine the opponent's next board.** The position of your move determines which small board the opponent must play in next. For example, playing in the top-right cell sends the opponent to the top-right small board.
3. **Win a small board.** Complete a horizontal, vertical, or diagonal line of three marks within a small board.
4. **Win the game.** Win three small boards in a row, column, or diagonal on the larger grid.
5. **Manage your time.** Each player has five minutes. Running out of time results in a loss.

If the designated next board has already been won or is full, the opponent may choose another eligible board.


## Key Features

The planned features of Tac² include:

- **User Authentication and Profiles:** User registration, login, and personal profile management.
- **Interactive Tutorial (Level 0):** A step-by-step introduction to the game rules and mechanics for new players.
- **Multiple Game Modes:**
  - **Local Multiplayer:** Two players compete on the same device.
  - **Player vs. Computer:** Single-player matches against AI opponents with multiple difficulty levels, such as easy, medium, and hard.
  - **Online Multiplayer:** Players create or join online rooms using a room key.
- **Global Leaderboard:** A public ranking of players based on their performance and scores against the computer.
- **User Statistics:** A personal dashboard showing win rates, performance across difficulty levels, and match history.
- **Timed Gameplay:** A chess clock that limits the time available to each player.


## Team

Tac² is developed by:

- **Begoyim Kosimova**
- **Sofia Scardovi**
- **Martina Samorè**

University of Bologna — Digital Transformation Management, A.Y. 2025/2026.

## Project Scope

The project focuses on implementing Tac²'s core game mechanics, board-selection rules, win conditions, and timed gameplay.

The final implementation scope and acceptance criteria are defined by the project requirements and documented in the accompanying Software Engineering report.


## Proposed Technology Stack

The following technologies are proposed for development. The final implementation may evolve as the project progresses.

- **Python:** Backend programming language and game logic.
- **FastAPI:** Backend API framework, including WebSockets for online multiplayer rooms.
- **PostgreSQL:** Relational database for user accounts, profiles, match records, and statistics.
- **FastAPI Users:** Authentication and user-management functionality.
- **Vue.js:** Frontend framework for the interactive user interface.
- **JavaScript:** Frontend interactions and client-side functionality.
- **Poetry:** Python dependency and build management.
- **pytest:** Python testing framework.
- **Vitest and Vue Test Utils:** Frontend unit testing.
- **Playwright:** End-to-end browser testing.
- **Ruff and Mypy:** Python code quality and static analysis.
- **Docker and Docker Compose:** Application containerisation and local development environment.
- **GitHub Actions:** Continuous integration and continuous delivery (CI/CD), including automated checks and builds.

## Project Structure

The repository separates the Python application from the Vue frontend.

```text
artifact/
├── docs
├── tac_two/
│   ├── __init__.py
│   ├── __main__.py
│   └── frontend/
│       ├── src/
│       │   ├── components/
│       │   ├── views/
│       │   ├── router/
│       │   ├── stores/
│       │   ├── App.vue
│       │   └── main.js
│       ├── e2e/
│       ├── package.json
│       └── vite.config.js
├── tests/
├── pyproject.toml
├── README.md
└── LICENSE
```

This illustrates the principal project files; additional configuration and source files may be present.

## Development Setup

### Prerequisites

- Python version supported by `pyproject.toml`.
- Poetry.
- Node.js compatible with the frontend's `package.json` requirements.
- npm.

### Python Environment

Install the Python dependencies from the repository root:

```bash
poetry install
```

Run the Python test suite:

```bash
poetry run poe test
```

Run the configured static checks:

```bash
poetry run poe static-checks
```

Run Python coverage:

```bash
poetry run poe coverage
poetry run poe coverage-report
```

Generate an HTML coverage report:

```bash
poetry run poe coverage-html
```

### Frontend Environment

Navigate to the frontend directory:

```bash
cd tac_two/frontend
```

Install the JavaScript dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

Run the frontend unit tests:

```bash
npm run test:unit -- --run
```

Build the frontend for production:

```bash
npm run build
```

Run the end-to-end tests:

```bash
npm run test:e2e
```

Playwright may require browser binaries to be installed before the end-to-end tests can run.

## Testing and Quality Assurance

Tac² includes testing infrastructure for the Python application and Vue frontend.

- **Python tests:** pytest.
- **Frontend unit tests:** Vitest and Vue Test Utils.
- **End-to-end tests:** Playwright.
- **Code quality:** Ruff and Mypy.
- **Coverage:** Python coverage tooling.

The testing strategy should cover the core game rules, including:

- Valid and invalid moves;
- board-selection rules;
- small-board victory conditions;
- overall game victory conditions;
- handling of completed or full boards;
- chess-clock behavior and timeout outcomes;
- relevant frontend interactions and user-visible feedback.

Coverage measurements and acceptance-test results should be documented once the corresponding tests have been implemented and executed.

## Build and Code Quality

Run the configured Python static checks from the repository root:

```bash
poetry run poe static-checks
```

Build the frontend:

```bash
cd tac_two/frontend
npm run build
```

These checks help identify static-analysis issues and frontend build errors before changes are merged.

## Versioning and Releases

Tac² follows Semantic Versioning:

`MAJOR.MINOR.PATCH`

Version numbers should be updated consistently across relevant project metadata, the changelog, Git tags, and published releases.

Release automation and the release history will be documented here once configured.

## Project Documentation

The accompanying Software Engineering report should document:

- Functional and non-functional requirements;
- user stories and acceptance criteria;
- game rules and domain modelling;
- architecture and design decisions;
- implementation details;
- testing strategy and validation evidence;
- development, build, and deployment instructions;
- licensing decisions and future improvements.

Links to the project report, user guide, developer guide, and release history can be added here when those resources are available.

## Third-Party Software

Tac² uses open-source software and third-party dependencies, including Python and Vue.js.

- **Python:** See the [official Python license documentation](https://docs.python.org/3/license.html).
- **Vue.js:** Vue.js is distributed under the [MIT License](https://github.com/vuejs/core/blob/main/LICENSE).
- **Other dependencies:** Each dependency remains subject to its own license terms and applicable notices.

The licenses of third-party packages should be reviewed and documented where appropriate.

## License

Tac² is distributed under the **Apache License 2.0**.

This permissive open-source license allows use, modification, and redistribution subject to its terms. It also includes an express patent license and requires preservation of applicable notices.

See the [`LICENSE`](LICENSE) file for the complete license text.

