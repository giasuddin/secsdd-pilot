# Requirements Document

## Introduction

API for streaming songs from a server data directory (SongDownloader).

## Requirements

### Requirement 1: Retrieve the chosen song from the server

**User Story:** As a client, I want to given the specified song as filename, the server returns a bytestream of that files content.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /download, THE SYSTEM SHALL given the specified song as filename, the server returns a bytestream of that files content.
   1.1. SEC-REQ-1.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-1.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-1.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.
   1.4. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.5. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.
   1.6. SEC-REQ-1.1-EC-22-1-1 [SECURITY: path-canonicalization] THE SYSTEM SHALL resolve all file paths to a canonical form.
   1.7. SEC-REQ-1.1-EC-22-1-2 [SECURITY: path-canonicalization] THE SYSTEM SHALL verify the resolved path remains within the designated base directory.
   1.8. SEC-REQ-1.1-EC-22-1-3 [SECURITY: path-canonicalization] THE SYSTEM SHALL reject paths containing traversal sequences (../, ..\ or encoded equivalents).

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
688be2ccdd74
-->
