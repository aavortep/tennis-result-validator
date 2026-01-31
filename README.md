# Tennis Tournament Manager

A web app for running tennis tournaments. Handles player registration, match scheduling, score tracking, disputes, and rankings.

## Tech Stack

- Python 3.11 + Django 5
- PostgreSQL 15
- Docker & Docker Compose
- Django REST Framework

## Quick Start

```bash
# clone and run
git clone https://github.com/aavortep/tennis-result-validator.git
cd tennis-result-validator
docker-compose up
```

App runs at http://localhost:8000

Default credentials:
- **DB**: `tennis_tournament`
- **User**: `tennis_user`
- **Password**: `tennis_password`
- **Port**: `5432`

## Docker

### Basic commands

```bash
# start everything
docker-compose up

# run in background
docker-compose up -d

# rebuild after code changes
docker-compose up --build

# stop containers
docker-compose down

# stop and remove volumes (wipes database)
docker-compose down -v
```

### Volumes

The app uses 3 volumes for persistent data:

| Volume | Path in container | What it stores |
|--------|-------------------|----------------|
| postgres_data | /var/lib/postgresql/data | database |
| media_data | /app/media | uploaded files (evidence, avatars) |
| static_data | /app/staticfiles | collected static files |

```bash
# check volumes
docker volume ls | grep tennis

# backup database
docker-compose exec db pg_dump -U tennis_user tennis_tournament > backup.sql

# restore database
cat backup.sql | docker-compose exec -T db psql -U tennis_user tennis_tournament
```

### Run without compose

```bash
# build image
docker build -t tennis-app .

# run with external postgres
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=tennis_tournament \
  -e DB_USER=tennis_user \
  -e DB_PASSWORD=tennis_password \
  tennis-app
```

### Logs and debugging

```bash
# view logs
docker-compose logs -f web

# shell into container
docker-compose exec web bash

# run django commands
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
```

## Project Structure

```
apps/
  accounts/     # users, auth, roles (organizer/referee/player/spectator)
  tournaments/  # tournaments and matches
  scores/       # score submission, disputes, evidence
  rankings/     # player rankings (per tournament + global)
```

## User Roles

| Role      | What they can do                                |
| --------- | ----------------------------------------------- |
| Organizer | create tournaments, manage players/referees     |
| Referee   | confirm scores, resolve disputes                |
| Player    | join tournaments, submit scores, raise disputes |
| Spectator | view tournaments and rankings                   |

## API Endpoints

### Accounts

- `POST /api/accounts/register/` - sign up
- `POST /api/accounts/login/` - login
- `GET /api/accounts/profile/` - get profile
- `GET /api/accounts/players/` - list players

### Tournaments

- `GET /api/tournaments/` - list tournaments
- `POST /api/tournaments/` - create tournament (organizers)
- `POST /api/tournaments/<id>/add-player/` - join tournament
- `GET /api/tournaments/<id>/matches/` - get matches

### Scores

- `POST /api/scores/submit/` - submit match score
- `POST /api/scores/<id>/confirm/` - confirm score
- `POST /api/scores/disputes/create/` - open dispute
- `POST /api/scores/disputes/<id>/resolve/` - resolve dispute

### Rankings

- `GET /api/rankings/global/` - global leaderboard
- `GET /api/rankings/tournament/<id>/` - tournament leaderboard
- `GET /api/rankings/head-to-head/<p1>/<p2>/` - head to head stats

## Running Tests

```bash
docker-compose exec web python manage.py test
```

## Environment Variables

You can override defaults in docker-compose:

| Variable    | Default            | Description   |
| ----------- | ------------------ | ------------- |
| DB_NAME     | tennis_tournament  | database name |
| DB_USER     | tennis_user        | db username   |
| DB_PASSWORD | tennis_password    | db password   |
| SECRET_KEY  | your-secret-key... | django secret |
| DEBUG       | True               | debug mode    |

## Score Validation

The app validates tennis scores:

- 2-5 sets per match
- Valid set scores (6-0 to 6-4, 7-5, 7-6)
- Winner needs 2 sets (best of 3) or 3 sets (best of 5)
