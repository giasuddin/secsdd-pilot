# Requirements Document

## Introduction

Webapp for product recommendation by searched tags (Recommendation). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get all posted products that match at least one of the provided tags

**User Story:** As a client, I want to get all posted products that match at least one of the provided tags.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /recommender, THE SYSTEM SHALL get all posted products that match at least one of the provided tags.
   1.1. SEC-REQ-1.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-1.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-1.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.
   1.4. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.5. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Post a new product along with its tags

**User Story:** As a client, I want to post a new product along with its tags.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recommender, THE SYSTEM SHALL post a new product along with its tags.
   1.1. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
da58d50c09af d8adc5a4709a
-->
