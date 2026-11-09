# Requirements Document

## Introduction

Webapp implementing a user login and creation service (InviteAPI). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Create an invitation by the current user to create a new user

**User Story:** As a client, I want to prepare an invitation id to send to be sent in private to the user email.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /invite_user, THE SYSTEM SHALL prepare an invitation id to send to be sent in private to the user email.

### Requirement 2: Given an invitation, create a user

**User Story:** As a client, I want to given an id of an invitation previously created by existing user, create a new user.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /create_user, THE SYSTEM SHALL given an id of an invitation previously created by existing user, create a new user.
