# Requirements Document

## Introduction

Webapp that registers and retrieves user clicks (Click Tracking API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Register a click

**User Story:** As a client, I want to endpoint to register a user's click in the database.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /click, THE SYSTEM SHALL endpoint to register a user's click in the database.

### Requirement 2: Retrieve clicks

**User Story:** As a client, I want to endpoint to retrieve clicks before or after a certain date.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /clicks, THE SYSTEM SHALL endpoint to retrieve clicks before or after a certain date.
