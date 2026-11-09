# Requirements Document

## Introduction

Webapp implementing a user login and creation service (InviteAPI). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Create an invitation by the current user to create a new user

**User Story:** As a client, I want to prepare an invitation id to send to be sent in private to the user email.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /invite_user, THE SYSTEM SHALL prepare an invitation id to send to be sent in private to the user email.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Given an invitation, create a user

**User Story:** As a client, I want to given an id of an invitation previously created by existing user, create a new user.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /create_user, THE SYSTEM SHALL given an id of an invitation previously created by existing user, create a new user.
   1.1. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
026a7b7b1c36 93748494756f
-->
