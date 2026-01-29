# Tennis Tournament Referee & Result Validator

A comprehensive web application for managing tennis tournaments with role-based access control, score submission, dispute resolution, and player rankings.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [User Roles](#user-roles)
- [Features](#features)
- [Getting Started](#getting-started)
- [Docker Setup](#docker-setup)
- [Web Interface (GUI)](#web-interface-gui)
- [Database Migrations](#database-migrations)
- [Running Tests](#running-tests)
- [API Reference](#api-reference)
- [Example Workflows](#example-workflows)
- [Future Improvements](#future-improvements)

## Project Overview

The Tennis Tournament Referee & Result Validator is a Django-based web application designed to manage tennis tournaments from creation to completion. It provides both a **web GUI** (using Bootstrap 5) and a **REST API** for integration with other systems.

The application supports multiple user roles with different permissions, allows players to submit and confirm match scores, handles score disputes with evidence submission, and automatically calculates player rankings.

### Key Capabilities

- Complete tournament lifecycle management
- Role-based access control (Organizer, Referee, Player, Spectator)
- Score submission and confirmation workflow
- Dispute resolution with evidence support
- Automatic ranking calculations
- RESTful API with Django REST Framework

## Architecture

This project follows a **Layered Monolithic Architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│              (Views, Serializers, URLs)                      │
├─────────────────────────────────────────────────────────────┤
│                    Application Layer                         │
│              (Services, Business Logic)                      │
├─────────────────────────────────────────────────────────────┤
│                      Domain Layer                            │
│                  (Models, Entities)                          │
├─────────────────────────────────────────────────────────────┤
│                   Infrastructure Layer                       │
│              (Database, External Services)                   │
└─────────────────────────────────────────────────────────────┘
```

### Project Structure

```
tennis_tournament/
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Django container definition
├── .env.example               # Environment template
├── requirements.txt           # Python dependencies
├── environment.yml            # Conda environment
├── manage.py                  # Django management script
├── README.md                  # This file
│
├── tennis_project/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/                      # Application modules
│   ├── accounts/              # User & authentication
│   │   ├── models.py         # User model with roles
│   │   ├── views.py          # Auth endpoints
│   │   ├── services.py       # Auth business logic
│   │   ├── serializers.py    # DRF serializers
│   │   ├── permissions.py    # Role-based permissions
│   │   └── tests/
│   │
│   ├── tournaments/           # Tournament management
│   │   ├── models.py         # Tournament, Match models
│   │   ├── views.py
│   │   ├── services.py
│   │   ├── serializers.py
│   │   └── tests/
│   │
│   ├── scores/                # Score & dispute handling
│   │   ├── models.py         # Score, Dispute, Evidence
│   │   ├── views.py
│   │   ├── services.py
│   │   ├── serializers.py
│   │   └── tests/
│   │
│   └── rankings/              # Player rankings
│       ├── models.py         # Ranking, GlobalRanking
│       ├── views.py
│       ├── services.py
│       ├── serializers.py
│       └── tests/
│
├── core/                      # Shared utilities
│   ├── exceptions.py         # Custom exceptions
│   ├── mixins.py             # Model mixins
│   └── utils.py              # Utility functions
│
├── templates/                 # Django templates (GUI)
│   ├── base.html             # Base layout with Bootstrap 5
│   ├── home.html             # Home page
│   ├── accounts/             # Login, register, profile
│   ├── tournaments/          # Tournament & match pages
│   ├── scores/               # Score submission & disputes
│   └── rankings/             # Rankings display
│
└── media/                     # Uploaded files
    └── evidence/
```

### Architecture Characteristics

| Characteristic | Level | Description |
|---------------|-------|-------------|
| Simplicity | High | Clean, understandable codebase |
| Modularity | High | Clear separation of apps and layers |
| Testability | High | Service layer enables easy unit testing |
| Responsiveness | Medium | Synchronous request handling |
| Scalability | Medium-Low | Single deployment model |
| Elasticity | Low | Manual scaling required |

## Tech Stack

- **Backend Framework:** Django 5.x
- **API Framework:** Django REST Framework 3.x
- **Database:** PostgreSQL 15
- **Containerization:** Docker & docker-compose
- **Authentication:** Django Session Authentication
- **Image Handling:** Pillow
- **CORS:** django-cors-headers

## User Roles

### Organizer

Tournament administrators with full management capabilities.

**Capabilities:**
- Create, update, delete tournaments
- Manage players and referees
- Add/remove participants from tournaments
- Assign players and referees to matches
- View and resolve disputed results
- Manage account settings

### Referee

Match officials responsible for score validation.

**Capabilities:**
- View assigned matches
- Submit match scores (auto-confirmed)
- Update/delete submitted scores
- View dispute evidence
- Resolve disputes for assigned matches
- Manage account settings

### Player

Tournament participants who play matches.

**Capabilities:**
- View matches and opponents
- Submit match scores
- Update/delete own score submissions
- Confirm opponent's score
- Dispute opponent's score (with evidence)
- View rankings
- Manage account settings

### Spectator

Viewers with read-only access.

**Capabilities:**
- View tournaments and matches
- View match results
- View player rankings
- Manage account settings

## Features

### Tournament Management
- Create tournaments with date ranges and player limits
- Tournament status workflow: Draft → Registration → In Progress → Completed
- Add/remove players and referees
- Generate and manage matches

### Match Management
- Create matches within tournaments
- Assign players and referees
- Track match status: Scheduled → In Progress → Completed/Disputed
- Support for multiple tournament rounds (R128 to Final)

### Score Management
- Players submit scores after matches
- Opponent confirmation workflow
- Referee scores auto-confirm
- Tennis score validation (set scores, tiebreaks)
- Automatic winner determination

### Dispute Resolution
- Players can dispute scores with reason
- Evidence submission (file or text)
- Referee/Organizer review process
- Final resolution with winner declaration

### Rankings
- Tournament-specific rankings
- Global rankings across all tournaments
- Points system based on round advancement
- Winner bonuses
- Win/loss statistics

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & docker-compose
- Conda (optional, for local development)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   cd tennis_tournament
   ```

2. **Create conda environment:**
   ```bash
   conda env create -f environment.yml
   conda activate tennis_tournament
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```

## Docker Setup

### Using docker-compose (Recommended)

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f web

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=tennis_tournament
DB_USER=tennis_user
DB_PASSWORD=tennis_password
DB_HOST=db
DB_PORT=5432
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| web | 8000 | Django application |
| db | 5432 | PostgreSQL database |

## Web Interface (GUI)

The application includes a full web interface built with **Bootstrap 5**. Access it at `http://localhost:8000/` after starting the Docker containers.

### Available Pages

| URL | Page | Access |
|-----|------|--------|
| `/` | Home | Public |
| `/login/` | Login | Public |
| `/register/` | Register | Public |
| `/profile/` | User Profile | Authenticated |
| `/tournaments/` | Tournament List | Public |
| `/tournaments/create/` | Create Tournament | **Organizer only** |
| `/tournaments/{id}/` | Tournament Details | Public |
| `/tournaments/{id}/edit/` | Edit Tournament | Tournament Creator |
| `/matches/` | My Matches | Player/Referee |
| `/matches/{id}/` | Match Details | Public |
| `/matches/{id}/score/` | Submit Score | Player/Referee |
| `/disputes/` | Dispute List | Authenticated |
| `/disputes/{id}/` | Dispute Details | Authenticated |
| `/disputes/{id}/resolve/` | Resolve Dispute | Organizer/Referee |
| `/rankings/` | Global Rankings | Public |
| `/rankings/tournament/{id}/` | Tournament Rankings | Public |
| `/rankings/my/` | My Rankings | Player |
| `/admin/` | Django Admin | Superuser |

### Quick Start Guide

1. **Register an account** at `/register/` - choose your role:
   - **Organizer**: Can create and manage tournaments
   - **Referee**: Can officiate matches and resolve disputes
   - **Player**: Can participate in matches and submit scores
   - **Spectator**: Can view tournaments and rankings

2. **Create a tournament** (Organizer only):
   - Go to `/tournaments/`
   - Click "Create Tournament"
   - Fill in details and save

3. **Manage tournament**:
   - Open registration to allow players to be added
   - Add players and referees
   - Create matches
   - Start tournament when ready

4. **Submit scores** (after match):
   - Go to match details
   - Click "Submit Score"
   - Enter set scores

5. **View rankings**:
   - Global rankings at `/rankings/`
   - Tournament-specific at `/rankings/tournament/{id}/`

## Database Migrations

Migrations run automatically on container startup. For manual operations:

```bash
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

## Running Tests

```bash
# Run all tests
docker-compose exec web python manage.py test

# Run specific app tests
docker-compose exec web python manage.py test apps.accounts
docker-compose exec web python manage.py test apps.tournaments
docker-compose exec web python manage.py test apps.scores
docker-compose exec web python manage.py test apps.rankings

# Run with verbosity
docker-compose exec web python manage.py test -v 2

# Run specific test class
docker-compose exec web python manage.py test apps.scores.tests.test_services.ScoreServiceTest
```

### Test Coverage

- **Unit Tests:** Service layer business logic
- **Integration Tests:** Complete workflows (score submission, dispute resolution)
- **Permission Tests:** Role-based access control

## API Reference

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/register/` | Register new user |
| POST | `/api/accounts/login/` | User login |
| POST | `/api/accounts/logout/` | User logout |
| GET/PUT | `/api/accounts/profile/` | Get/update profile |
| POST | `/api/accounts/password/change/` | Change password |
| DELETE | `/api/accounts/delete/` | Delete account |
| GET | `/api/accounts/players/` | List all players |
| GET | `/api/accounts/referees/` | List all referees |

### Tournament Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/tournaments/` | List/create tournaments |
| GET/PUT/DELETE | `/api/tournaments/{id}/` | Tournament details |
| POST | `/api/tournaments/{id}/add-player/` | Add player |
| DELETE | `/api/tournaments/{id}/remove-player/{player_id}/` | Remove player |
| POST | `/api/tournaments/{id}/add-referee/` | Add referee |
| POST | `/api/tournaments/{id}/status/` | Update status |
| GET | `/api/tournaments/{id}/matches/` | List matches |

### Match Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | `/api/tournaments/matches/` | List/create matches |
| GET | `/api/tournaments/matches/{id}/` | Match details |
| GET | `/api/tournaments/matches/my-matches/` | User's matches |
| PUT | `/api/tournaments/matches/{id}/assign-players/` | Assign players |
| PUT | `/api/tournaments/matches/{id}/assign-referee/` | Assign referee |
| POST | `/api/tournaments/matches/{id}/start/` | Start match |

### Score Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/scores/submit/` | Submit score |
| GET/PUT/DELETE | `/api/scores/{id}/` | Score details |
| POST | `/api/scores/{id}/confirm/` | Confirm score |
| GET | `/api/scores/match/{match_id}/` | Match scores |

### Dispute Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/scores/disputes/` | List disputes |
| GET | `/api/scores/disputes/open/` | Open disputes |
| POST | `/api/scores/disputes/create/` | Create dispute |
| GET | `/api/scores/disputes/{id}/` | Dispute details |
| POST | `/api/scores/disputes/{id}/resolve/` | Resolve dispute |
| POST | `/api/scores/disputes/{id}/review/` | Mark under review |
| GET | `/api/scores/disputes/{id}/evidence/` | List evidence |
| POST | `/api/scores/evidence/submit/` | Submit evidence |

### Ranking Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/rankings/tournament/{id}/` | Tournament leaderboard |
| GET | `/api/rankings/global/` | Global leaderboard |
| GET | `/api/rankings/my/` | User's rankings |
| GET | `/api/rankings/my/global/` | User's global ranking |
| GET | `/api/rankings/player/{id}/` | Player rankings |

## Example Workflows

### 1. Tournament Setup

```bash
# 1. Organizer creates tournament
POST /api/tournaments/
{
  "name": "Summer Open 2024",
  "start_date": "2024-07-01",
  "end_date": "2024-07-14",
  "location": "Central Tennis Club",
  "max_players": 32
}

# 2. Open registration
POST /api/tournaments/1/status/
{"action": "open_registration"}

# 3. Add players
POST /api/tournaments/1/add-player/
{"player_id": 5}

# 4. Start tournament
POST /api/tournaments/1/status/
{"action": "start"}
```

### 2. Match Score Submission

```bash
# 1. Player submits score
POST /api/scores/submit/
{
  "match": 1,
  "set_scores": [
    {"player1": 6, "player2": 4},
    {"player1": 6, "player2": 3}
  ]
}

# 2. Opponent confirms
POST /api/scores/1/confirm/
```

### 3. Dispute Resolution

```bash
# 1. Player disputes score
POST /api/scores/disputes/create/
{
  "match": 1,
  "reason": "Score was recorded incorrectly"
}

# 2. Submit evidence
POST /api/scores/evidence/submit/
{
  "dispute": 1,
  "description": "Photo of scoreboard"
}

# 3. Referee resolves
POST /api/scores/disputes/1/resolve/
{
  "resolution_notes": "After review, player1 wins",
  "winner_id": 5
}
```

## Future Improvements

### Short-term
- [ ] JWT authentication support
- [ ] Email notifications
- [ ] WebSocket for real-time updates
- [ ] API rate limiting

### Medium-term
- [ ] Tournament bracket visualization
- [ ] Player statistics dashboard
- [ ] Match scheduling optimization
- [ ] Mobile app API enhancements

### Long-term
- [ ] Machine learning for match predictions
- [ ] Video evidence support
- [ ] Multi-language support
- [ ] External API integrations (ATP/WTA rankings)

## License

This project is developed for educational purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
