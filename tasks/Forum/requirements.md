# Requirements Document

## Introduction

Forum webapp (MyForum). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get all previously posted messages

**User Story:** As a client, I want to get all previously posted messages.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /messages, THE SYSTEM SHALL get all previously posted messages.

### Requirement 2: Post a new message to the forum

**User Story:** As a client, I want to post a new message to the forum.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /messages, THE SYSTEM SHALL post a new message to the forum.
