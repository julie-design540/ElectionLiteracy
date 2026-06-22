# Database Schema

## Users

- `id`
- `username`
- `email`
- `password_hash`
- `role`
- `bio`
- `profile_image`
- `created_at`

## Categories

- `id`
- `name`
- `slug`
- `description`
- `is_default`
- `created_at`

## Artwork

- `id`
- `title`
- `slug`
- `description`
- `filename`
- `mime_type`
- `status`
- `is_featured`
- `download_count`
- `user_id`
- `category_id`
- `created_at`
- `updated_at`

## Comments

- `id`
- `content`
- `is_moderated`
- `user_id`
- `artwork_id`
- `created_at`

## Likes

- `id`
- `user_id`
- `artwork_id`
- `created_at`

## Favourites

- `id`
- `user_id`
- `artwork_id`
- `created_at`

## Reports

- `id`
- `reason`
- `details`
- `status`
- `user_id`
- `artwork_id`
- `reviewed_by_id`
- `reviewed_at`
- `created_at`
