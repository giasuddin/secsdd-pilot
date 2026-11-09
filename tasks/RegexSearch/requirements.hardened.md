# Requirements Document

## Introduction

App that searches files based on regex (File Search API).

## Requirements

### Requirement 1: Search files by regex

**User Story:** As a client, I want to searches files in a specified directory and returns files whose content matches the given regex.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /search, THE SYSTEM SHALL searches files in a specified directory and returns files whose content matches the given regex.
   1.1. SEC-REQ-1.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-1.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-1.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
dbd2dbd622ab
-->
