# Software Requirements Specification

## Purpose

Build a web-based civic education platform that teaches Kenyan users, especially young people, about elections and civic responsibility through digital artwork and interactive community participation.

## System Description

The platform behaves like a civic-focused creative network. Visitors can browse educational artwork, while registered users can create, upload, save, like, comment on, and report civic content. Administrators moderate submissions to ensure the public gallery remains accurate, respectful, and useful for civic learning.

## Functional Requirements

- User authentication and profile management
- Artwork upload, review, and gallery browsing
- Likes, favourites, comments, and reports
- Shares and engagement visibility for users
- Search, category filtering, and download support
- Admin moderation, approvals, and analytics
- Civic category management

## Non-Functional Requirements

- Responsive design
- Beginner-friendly code structure
- SQLite persistence
- Secure password handling and CSRF protection

## Constraints

- No SPA framework
- No REST API
- No external database server

## Design Principle

If a feature does not support learning, creating, sharing, engaging, or moderating civic education content, it should not be part of the core scope.
