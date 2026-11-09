# Requirements Document

## Introduction

Webapp implementing a simple login page (LoginAPI). Data is stored in an SQLite database.

## Requirements

### Requirement 1: User login

**User Story:** As a client, I want to authenticate a user with email and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /login, THE SYSTEM SHALL authenticate a user with email and password.
   1.1. SEC-REQ-1.1-EC-307-1-1 [SECURITY: rate-limiting] WHEN authentication attempts exceed 5 failures per account per 60-second window, THE SYSTEM SHALL apply exponential back-off to subsequent attempts.
   1.2. SEC-REQ-1.1-EC-307-1-2 [SECURITY: rate-limiting] WHEN authentication attempts exceed 5 failures per account per 60-second window, THE SYSTEM SHALL emit a brute-force audit event.
   1.3. SEC-REQ-1.1-EC-307-2-1 [SECURITY: ip-rate-limiting] WHEN authentication attempts exceed 20 failures per IP address per 5-minute window, THE SYSTEM SHALL temporarily block that IP.
   1.4. SEC-REQ-1.1-EC-307-2-2 [SECURITY: ip-rate-limiting] WHEN authentication attempts exceed 20 failures per IP address per 5-minute window, THE SYSTEM SHALL alert the security monitoring system.
   1.5. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.6. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.
   1.7. SEC-REQ-1.1-EC-208-1 [SECURITY: constant-time-comparison] THE SYSTEM SHALL return authentication responses in constant time regardless of whether the account exists or the credential is valid, using a dummy hash comparison when the account is not found.

### Requirement 2: User registration

**User Story:** As a client, I want to register a new user with email, password, and name.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /register, THE SYSTEM SHALL register a new user with email, password, and name.
   1.1. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
abc408380812 fda45e4e1911
-->
