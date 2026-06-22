# Data Flow Diagram

```mermaid
flowchart LR
  Visitor[Visitor] -->|Register/Login| Auth[Authentication]
  Auth --> DB[(SQLite Database)]
  User[User] -->|Upload, like, comment, report| Platform[Civic Art Platform]
  Platform --> DB
  Admin[Admin] -->|Approve, moderate, manage| AdminPanel[Admin Tools]
  AdminPanel --> DB
```
