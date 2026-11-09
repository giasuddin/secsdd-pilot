# Requirements Document

## Introduction

Forum webapp (MyForum). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get all previously posted messages

**User Story:** As a client, I want to get all previously posted messages.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /messages, THE SYSTEM SHALL get all previously posted messages.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Post a new message to the forum

**User Story:** As a client, I want to post a new message to the forum.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /messages, THE SYSTEM SHALL post a new message to the forum.
   1.1. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
3df772c3d95c 2c0f119d0a0b
-->
