# Installation Guide

1. Install Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create the database and seed the default data:

```bash
flask --app app.py seed-data
```

5. Run the development server:

```bash
flask --app app.py run
```

## Recommended Environment Variables

- `SECRET_KEY`
- `DATABASE_URL`
- `FLASK_CONFIG`
- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_USERNAME`
- `SEED_ADMIN_PASSWORD`
