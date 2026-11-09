# Requirements Document

## Introduction

Webapp implementing a simple login page (LoginAPI). Data is stored in an SQLite database.

## Requirements

### Requirement 1: User login

**User Story:** As a client, I want to authenticate a user with email and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /login, THE SYSTEM SHALL authenticate a user with email and password.

### Requirement 2: User registration

**User Story:** As a client, I want to register a new user with email, password, and name.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /register, THE SYSTEM SHALL register a new user with email, password, and name.
