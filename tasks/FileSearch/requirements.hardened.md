# Requirements Document

## Introduction

API for searching files in a server data directory (FileSearch).

## Requirements

### Requirement 1: Retreive a list of files from the server that contain the specified content or match the filename

**User Story:** As a client, I want to the server stores files in the /data directory.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /search, THE SYSTEM SHALL the server stores files in the /data directory.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
800b5e295967
-->
