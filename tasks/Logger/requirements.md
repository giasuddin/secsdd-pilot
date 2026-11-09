# Requirements Document

## Introduction

Simple logging service (LoggingAPI).

## Requirements

### Requirement 1: Log a message

**User Story:** As a client, I want to log a message to the server.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /log, THE SYSTEM SHALL log a message to the server.

### Requirement 2: Retrieve logs

**User Story:** As a client, I want to retrieve all logged messages.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /logs, THE SYSTEM SHALL retrieve all logged messages.
