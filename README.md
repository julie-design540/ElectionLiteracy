# Design and Implementation of a Digital Art-Based Civic Education Platform for Kenyan Elections

This project is a beginner-friendly Flask web application that uses digital artwork and community participation to teach Kenyan civic responsibility and election awareness.

## Mission

To become Kenya's digital hub for civic education through creative visual storytelling, helping citizens learn about elections, democracy, and civic responsibility in a safe, engaging online community.

## Features

- User registration, login, logout, profile management, and password changes
- Civic artwork upload, edit, delete, browse, search, filter, and download
- Likes, favourites, comments, and reports for community engagement
- Admin dashboard for approvals, moderation, user management, categories, and analytics
- Responsive UI with dark mode, toasts, spinner, animations, and glassmorphism styling

## Tech Stack

- Python
- Flask
- SQLAlchemy
- Flask-Login
- Flask-WTF
- SQLite
- HTML5, CSS3, JavaScript, Bootstrap 5, Bootstrap Icons
- Chart.js

## Project Structure

- `app.py` application factory and CLI seed command
- `config.py` configuration classes
- `extensions.py` Flask extension instances
- `models/` SQLAlchemy models
- `forms/` Flask-WTF forms
- `routes/` blueprints and route helpers
- `templates/` reusable Jinja templates
- `static/` CSS, JavaScript, and uploaded artwork references
- `instance/` runtime database and upload storage
- `migrations/` migration notes and generated history
- `docs/` project documentation

## Quick Start

1. Create a virtual environment.
2. Install dependencies from `requirements.txt`.
3. Set `FLASK_APP=app.py`.
4. Run `flask --app app.py seed-data` to create default categories and an admin user.
5. Run `flask --app app.py run`.

On Windows, you can also run `run.bat` from the project root.

## Default Admin

The administrator account is created using environment variables.
Set SEED_ADMIN_EMAIL, SEED_ADMIN_USERNAME, and SEED_ADMIN_PASSWORD before running the seed command.

## Module Checklist

- `app.py` application factory and app-wide setup
- `config.py` environment settings
- `extensions.py` Flask extensions
- `models/` users, artwork, categories, comments, likes, favourites, reports
- `forms/` authentication, artwork, and admin forms
- `routes/` public, auth, artwork, and admin blueprints
- `templates/` home, gallery, auth, artwork, admin, and error pages
- `static/` theme styling and client-side interactions
- `docs/` user, admin, testing, deployment, and analysis documentation

The core workflow is:

1. Visitors browse civic artwork and read election-related messages.
2. Registered users create and upload educational artwork.
3. Administrators verify content for accuracy, safety, and respectfulness.
4. Approved artwork enters the public gallery for wider engagement.
