# Requirements Document

## Introduction

API for streaming songs from a server data directory (SongDownloader).

## Requirements

### Requirement 1: Retrieve the chosen song from the server

**User Story:** As a client, I want to given the specified song as filename, the server returns a bytestream of that files content.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /download, THE SYSTEM SHALL given the specified song as filename, the server returns a bytestream of that files content.
