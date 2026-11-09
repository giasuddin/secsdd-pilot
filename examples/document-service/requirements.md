# Requirements Document

## Introduction

This document defines the requirements for a team document service. Users upload documents, open them by ID, search them, and see recent documents on a dashboard. Each document has an owner and a share list. Preview cards on the dashboard are rendered as HTML.

## Requirements

### Requirement 1: Document Upload

**User Story:** As a user, I want to upload a document so that my team can use it.

#### Acceptance Criteria

1. WHEN a user uploads a document, THE SYSTEM SHALL store it with its title.

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
