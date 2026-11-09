# Requirements Document

## Introduction

Secure cloud storage app for string secrets (Secret Storage). Data is stored in an SQLite database.

## Requirements

### Requirement 1: User registration

**User Story:** As a client, I want to register a new user with email, username and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /register, THE SYSTEM SHALL register a new user with email, username and password.

### Requirement 2: User login

**User Story:** As a client, I want to authenticate a user with email and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /login, THE SYSTEM SHALL authenticate a user with email and password.

### Requirement 3: Set secret

**User Story:** As a client, I want to save a secret on the server using the username, token, and the secret text.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /set_secret, THE SYSTEM SHALL save a secret on the server using the username, token, and the secret text.

### Requirement 4: Get secret

**User Story:** As a client, I want to retrieve a secret based on the provided username.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /get_secret, THE SYSTEM SHALL retrieve a secret based on the provided username.
