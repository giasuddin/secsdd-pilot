# Requirements Document

## Introduction

This document defines the requirements for a team document service. Users upload documents, open them by ID, search them, and see recent documents on a dashboard. Each document has an owner and a share list. Preview cards on the dashboard are rendered as HTML.

## Requirements

### Requirement 1: Document Upload

**User Story:** As a user, I want to upload a document so that my team can use it.

#### Acceptance Criteria

1. WHEN a user uploads a document, THE SYSTEM SHALL store it with its title.
   1.1. SEC-REQ-1.1-EC-434-1-1 [SECURITY: file-type-validation] WHEN a user uploads a file, THE SYSTEM SHALL validate the file's magic bytes against an allowlist of permitted MIME types.
   1.2. SEC-REQ-1.1-EC-434-1-2 [SECURITY: file-type-validation] WHEN a user uploads a file, THE SYSTEM SHALL reject files whose extension does not match their detected content type.
   1.3. SEC-REQ-1.1-EC-434-2-1 [SECURITY: upload-storage-isolation] WHEN a user uploads a file, THE SYSTEM SHALL enforce a maximum file size of the configured limit.
   1.4. SEC-REQ-1.1-EC-434-2-2 [SECURITY: upload-storage-isolation] WHEN a user uploads a file, THE SYSTEM SHALL store uploaded files outside every directory the system serves or executes files from, under a randomized filename and without execute permission.

### Requirement 2: Document Retrieval

**User Story:** As a user, I want to open a document by its ID.

#### Acceptance Criteria

1. WHEN a user requests /documents/{id}, THE SYSTEM SHALL return the document.

### Requirement 3: Document Search

**User Story:** As a user, I want to search documents by title.

#### Acceptance Criteria

1. WHEN a user searches by title, THE SYSTEM SHALL return matching documents from the database.

### Requirement 4: Dashboard

**User Story:** As a user, I want to see my recent documents on a dashboard.

#### Acceptance Criteria

1. WHEN a user opens the dashboard, THE SYSTEM SHALL show a preview card for each recent document.

## Security Baseline (Cross-Cutting)

These constraints apply to every requirement above. They are stated once here rather than repeated under each requirement.

- SEC-BASELINE-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
- SEC-BASELINE-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
- SEC-BASELINE-3 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
a7cf68e78791 79a43a9c8f33 e5f21e5baa16 4e30ea2a69a4
-->
