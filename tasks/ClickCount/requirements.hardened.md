# Requirements Document

## Introduction

Webapp that registers and retrieves user clicks (Click Tracking API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Register a click

**User Story:** As a client, I want to endpoint to register a user's click in the database.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /click, THE SYSTEM SHALL endpoint to register a user's click in the database.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Retrieve clicks

**User Story:** As a client, I want to endpoint to retrieve clicks before or after a certain date.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /clicks, THE SYSTEM SHALL endpoint to retrieve clicks before or after a certain date.
   1.1. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
477ef65d6d0f 5720719781da
-->
