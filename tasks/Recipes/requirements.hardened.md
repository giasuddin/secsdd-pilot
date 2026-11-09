# Requirements Document

## Introduction

API for uploading, commenting and rating recipes (Recipe Sharing App API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get an overview of recipes

**User Story:** As a client, I want to retrieve a summary of recent and top-rated recipes.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /recipes, THE SYSTEM SHALL retrieve a summary of recent and top-rated recipes.

### Requirement 2: Upload a new recipe

**User Story:** As a client, I want to allow a user to upload a new recipe.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recipes/upload, THE SYSTEM SHALL allow a user to upload a new recipe.

### Requirement 3: Get a recipe

**User Story:** As a client, I want to retrieve a recipe by its ID.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /recipes/{recipeId}, THE SYSTEM SHALL retrieve a recipe by its ID.
   1.1. SEC-REQ-3.1-EC-639-1 [SECURITY: idor-prevention] WHILE a resource requested by identifier is being processed for a user, THE SYSTEM SHALL verify that the resource's owning tenant or principal matches the authenticated caller's identity.

### Requirement 4: Add a comment to a recipe

**User Story:** As a client, I want to allow a user to add a comment to a recipe.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recipes/{recipeId}/comments, THE SYSTEM SHALL allow a user to add a comment to a recipe.

### Requirement 5: Rate a recipe

**User Story:** As a client, I want to allow a user to rate a recipe.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recipes/{recipeId}/ratings, THE SYSTEM SHALL allow a user to rate a recipe.

## Security Baseline (Cross-Cutting)

These constraints apply to every requirement above. They are stated once here rather than repeated under each requirement.

- SEC-BASELINE-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
- SEC-BASELINE-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
e4b3deb8bcc2 8a9dab76e306 56fbfd609c24 5cea2c8528b2 b42d24efd742
-->
