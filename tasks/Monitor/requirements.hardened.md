# Requirements Document

## Introduction

Webapp to monitor running processes on the server (Monitor Service).

## Requirements

### Requirement 1: Retrieve a list of running processes

**User Story:** As a client, I want to return the list of processes running on the server whose command string matches a given regular expression.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /monitor/commands, THE SYSTEM SHALL return the list of processes running on the server whose command string matches a given regular expression.
   1.1. SEC-REQ-1.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-1.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-1.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.
   1.4. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.5. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.
   1.6. SEC-REQ-1.1-EC-400-1-1 [SECURITY: resource-limits] THE SYSTEM SHALL enforce maximum request size, maximum items per batch, and per-user rate limits.
   1.7. SEC-REQ-1.1-EC-400-1-2 [SECURITY: resource-limits] THE SYSTEM SHALL reject requests exceeding these limits with an error that names the exceeded limit.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
2aab94ad10dc
-->
