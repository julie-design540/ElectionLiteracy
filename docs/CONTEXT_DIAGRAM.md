# Context Diagram

```mermaid
flowchart LR
  Student[Student / Visitor] --> Platform[Civic Art Platform]
  Admin[Administrator] --> Platform
  Platform --> SQLite[(SQLite Database)]
  Platform --> Storage[(Local Upload Folder)]
```
