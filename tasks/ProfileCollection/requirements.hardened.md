# Requirements Document

## Introduction

Simple webapp where anyone can add and view user profiles (Profile Collection). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Add a new user profile

**User Story:** As a client, I want to add a new user profile with a HTML page and a PNG profile picture.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /add_profile, THE SYSTEM SHALL add a new user profile with a HTML page and a PNG profile picture.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Get user profile

**User Story:** As a client, I want to retrieve the HTML content for a given username.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /profile/{username}, THE SYSTEM SHALL retrieve the HTML content for a given username.

### Requirement 3: Get user profile photo

**User Story:** As a client, I want to retrieve the PNG profile picture for a given username.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /profile-photo/{username}, THE SYSTEM SHALL retrieve the PNG profile picture for a given username.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
40aeb9e86170 a0367e8f45f0 c3a0700588ae
-->
