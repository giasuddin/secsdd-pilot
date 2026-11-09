# Requirements Document

## Introduction

Secure cloud storage app for string secrets (Secret Storage). Data is stored in an SQLite database.

## Requirements

### Requirement 1: User registration

**User Story:** As a client, I want to register a new user with email, username and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /register, THE SYSTEM SHALL register a new user with email, username and password.

### Requirement 2: User login

**User Story:** As a client, I want to authenticate a user with email and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /login, THE SYSTEM SHALL authenticate a user with email and password.
   1.1. SEC-REQ-2.1-EC-307-1-1 [SECURITY: rate-limiting] WHEN authentication attempts exceed 5 failures per account per 60-second window, THE SYSTEM SHALL apply exponential back-off to subsequent attempts.
   1.2. SEC-REQ-2.1-EC-307-1-2 [SECURITY: rate-limiting] WHEN authentication attempts exceed 5 failures per account per 60-second window, THE SYSTEM SHALL emit a brute-force audit event.
   1.3. SEC-REQ-2.1-EC-307-2-1 [SECURITY: ip-rate-limiting] WHEN authentication attempts exceed 20 failures per IP address per 5-minute window, THE SYSTEM SHALL temporarily block that IP.
   1.4. SEC-REQ-2.1-EC-307-2-2 [SECURITY: ip-rate-limiting] WHEN authentication attempts exceed 20 failures per IP address per 5-minute window, THE SYSTEM SHALL alert the security monitoring system.
   1.5. SEC-REQ-2.1-EC-208-1 [SECURITY: constant-time-comparison] THE SYSTEM SHALL return authentication responses in constant time regardless of whether the account exists or the credential is valid, using a dummy hash comparison when the account is not found.

### Requirement 3: Set secret

**User Story:** As a client, I want to save a secret on the server using the username, token, and the secret text.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /set_secret, THE SYSTEM SHALL save a secret on the server using the username, token, and the secret text.

### Requirement 4: Get secret

**User Story:** As a client, I want to retrieve a secret based on the provided username.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /get_secret, THE SYSTEM SHALL retrieve a secret based on the provided username.
   1.1. SEC-REQ-4.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-4.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-4.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.

## Security Baseline (Cross-Cutting)

These constraints apply to every requirement above. They are stated once here rather than repeated under each requirement.

- SEC-BASELINE-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
- SEC-BASELINE-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
c81b9ad2e315 abc408380812 fed5445c4260 28964f2f3488
-->
