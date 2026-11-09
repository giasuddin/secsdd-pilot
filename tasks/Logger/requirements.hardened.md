# Requirements Document

## Introduction

Simple logging service (LoggingAPI).

## Requirements

### Requirement 1: Log a message

**User Story:** As a client, I want to log a message to the server.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /log, THE SYSTEM SHALL log a message to the server.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Retrieve logs

**User Story:** As a client, I want to retrieve all logged messages.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /logs, THE SYSTEM SHALL retrieve all logged messages.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
f7fbe81db6f3 e955bd74524c
-->
