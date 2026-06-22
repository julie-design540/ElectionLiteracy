# Testing Documentation

## Manual Test Cases

1. Register a new account.
2. Log in with valid credentials.
3. Upload artwork and confirm it appears as pending.
4. Log in as admin and approve the artwork.
5. Search and filter the gallery.
6. Like, favourite, comment, and report an artwork.
7. Confirm the admin dashboard counts update.

## Technical Checks

- Run `python -m compileall .`
- Verify templates render without missing variables
- Confirm uploaded files are saved to the local upload folder
