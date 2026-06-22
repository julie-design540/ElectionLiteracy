# Deployment Guide

## Best Option For This Project

For a school/demo deployment, use PythonAnywhere because it can run Flask with SQLite and persistent project files with less setup.

For a more production-style deployment, use Render or Railway with a managed database and persistent file storage. Do not rely on temporary container storage for uploaded profile images, lesson files, or artwork.

## Required Environment Variables

- `FLASK_CONFIG=production`
- `SECRET_KEY=<generate-a-long-random-secret>`
- `DATABASE_URL=sqlite:////absolute/path/to/civic_art.db` for SQLite, or a managed database URL if you move away from SQLite
- `SEED_ADMIN_EMAIL=<admin-email>`
- `SEED_ADMIN_USERNAME=<admin-username>`
- `SEED_ADMIN_PASSWORD=<strong-admin-password>`

## Generic Hosted Start Command

Use this start command on platforms that ask for one:

```bash
waitress-serve --listen=0.0.0.0:$PORT app:app
```

The included `Procfile` uses the same command.

## PythonAnywhere Flow

1. Upload or clone the project into your PythonAnywhere account.
2. Create a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Create a new Manual Configuration Flask web app.
5. Point the WSGI file to this project and expose `app` from `app.py` as `application`.
6. Set the environment variables above.
7. Reload the web app.

## Render Or Railway Flow

1. Push the project to GitHub.
2. Create a new Python web service from the repository.
3. Use `pip install -r requirements.txt` as the build command.
4. Use `waitress-serve --listen=0.0.0.0:$PORT app:app` as the start command.
5. Add the production environment variables.
6. Add persistent storage or move uploads/database to managed services before real public use.

## Production Checklist

- Replace the default `SECRET_KEY`.
- Replace the default seeded admin password.
- Configure database and upload backups.
- Keep `FLASK_CONFIG=production`.
- Test login, uploads, comments, lesson completion, and admin moderation after deployment.
