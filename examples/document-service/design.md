# Design Document

## Overview

A team document service. Users upload documents, open them by ID, search them by title, and see recent documents on a dashboard. This design is the input to SecSpec O1 (design-level hardening) in the proposal's running example. Spec It Safe reads only `requirements.md`, so it does not see this file.

## Data model

| Entity | Fields |
| --- | --- |
| User | `id`, `name` |
| Document | `id`, `title`, `content`, `owner_id` (User), `shared_with` (list of User ids), `created_at` |

Each document has one owner and a share list. A user may read a document only if they are its owner or are on its share list.

## Endpoints

| Requirement | Endpoint | Behaviour |
| --- | --- | --- |
| R1 | `POST /documents` | Stores the uploaded file and its user-supplied `title`. Sets `owner_id` to the caller. |
| R2 | `GET /documents/{id}` | Loads the document with the given `id` and returns it. |
| R3 | `GET /search?title=...` | Runs a database query that matches `title` against stored titles. |
| R4 | `GET /dashboard` | Renders an HTML page with one preview card per recent document. Each card shows the document `title`. |

## Data flows relevant to security

- **R3 → database.** The `title` query parameter is user input and is used in a database query (CWE-89 risk; SR S1).
- **R1 upload → storage.** Uploaded files are stored on the server (CWE-434 risk; SR S2).
- **R2 owned resource.** Documents are fetched by a user-controlled `id`; access depends on `owner_id` and `shared_with` (CWE-639 risk; SR S3).
- **R1 title → R4 HTML.** The `title` stored by R1 is later rendered inside HTML on the dashboard in R4 (stored XSS, CWE-79 risk; SR S4). No single requirement shows this flow.

## Public and protected endpoints

All four endpoints require an authenticated user. There are no public endpoints in this example.
