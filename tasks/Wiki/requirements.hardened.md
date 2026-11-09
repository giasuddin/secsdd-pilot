# Requirements Document

## Introduction

Wiki webapp (Wiki API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get a list of all entries with their titles and links to respective entries

**User Story:** As a client, I want to get a list of all entries with their titles and links to respective entries.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /entries, THE SYSTEM SHALL get a list of all entries with their titles and links to respective entries.

### Requirement 2: Create a new entry

**User Story:** As a client, I want to create a new entry.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /entries, THE SYSTEM SHALL create a new entry.
   1.1. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 3: Get a specific entry

**User Story:** As a client, I want to get a specific entry.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /entries/{entryId}, THE SYSTEM SHALL get a specific entry.

### Requirement 4: Update an existing entry

**User Story:** As a client, I want to update an existing entry.

#### Acceptance Criteria

1. WHEN a client sends a PUT request to /entries/{entryId}, THE SYSTEM SHALL update an existing entry.

### Requirement 5: View the history of edits for a specific entry

**User Story:** As a client, I want to view the history of edits for a specific entry.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /entries/{entryId}/edits, THE SYSTEM SHALL view the history of edits for a specific entry.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
bae1d0918616 3f4192ac1b0d 2dc8146de1d0 4ad6f1578795 cd681efa6c4f
-->
