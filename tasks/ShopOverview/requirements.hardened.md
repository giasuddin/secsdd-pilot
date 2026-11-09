# Requirements Document

## Introduction

Webapp implementing a simple warehouse page (Merchant WebApp API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Register a new merchant

**User Story:** As a client, I want to register a new merchant.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /merchants/register, THE SYSTEM SHALL register a new merchant.

### Requirement 2: Merchant login

**User Story:** As a client, I want to authenticate a merchant with email and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /merchants/login, THE SYSTEM SHALL authenticate a merchant with email and password.
   1.1. SEC-REQ-2.1-EC-307-1-1 [SECURITY: rate-limiting] WHEN authentication attempts exceed 5 failures per account per 60-second window, THE SYSTEM SHALL apply exponential back-off to subsequent attempts.
   1.2. SEC-REQ-2.1-EC-307-1-2 [SECURITY: rate-limiting] WHEN authentication attempts exceed 5 failures per account per 60-second window, THE SYSTEM SHALL emit a brute-force audit event.
   1.3. SEC-REQ-2.1-EC-307-2-1 [SECURITY: ip-rate-limiting] WHEN authentication attempts exceed 20 failures per IP address per 5-minute window, THE SYSTEM SHALL temporarily block that IP.
   1.4. SEC-REQ-2.1-EC-307-2-2 [SECURITY: ip-rate-limiting] WHEN authentication attempts exceed 20 failures per IP address per 5-minute window, THE SYSTEM SHALL alert the security monitoring system.
   1.5. SEC-REQ-2.1-EC-208-1 [SECURITY: constant-time-comparison] THE SYSTEM SHALL return authentication responses in constant time regardless of whether the account exists or the credential is valid, using a dummy hash comparison when the account is not found.

### Requirement 3: Lets a merchant upload their wares as a CSV string with the following columns: name, description, price

**User Story:** As a client, I want to let a merchant upload their wares as a CSV string with the following columns: name, description, price.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /merchants/upload-wares, THE SYSTEM SHALL let a merchant upload their wares as a CSV string with the following columns: name, description, price.

### Requirement 4: Retrieve all offered wares and merchants offering the wares, filtered with the provided query

**User Story:** As a client, I want to retrieve all offered wares and merchants offering the wares, filtered with the provided query.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /wares, THE SYSTEM SHALL retrieve all offered wares and merchants offering the wares, filtered with the provided query.
   1.1. SEC-REQ-4.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-4.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-4.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.
   1.4. SEC-REQ-4.1-EC-89-1-1 [SECURITY: parameterized-query] THE SYSTEM SHALL execute all database queries using parameterized statements or prepared statements only.
   1.5. SEC-REQ-4.1-EC-89-1-2 [SECURITY: parameterized-query] THE SYSTEM SHALL NOT construct query strings by concatenation of user-supplied values.
   1.6. SEC-REQ-4.1-EC-89-2-1 [SECURITY: input-validation] WHEN a user submits the input, THE SYSTEM SHALL validate each input parameter against the format rules defined for its field.
   1.7. SEC-REQ-4.1-EC-89-2-2 [SECURITY: input-validation] WHEN a user submits the input, THE SYSTEM SHALL NOT use an input parameter that failed validation in any database operation.

## Security Baseline (Cross-Cutting)

These constraints apply to every requirement above. They are stated once here rather than repeated under each requirement.

- SEC-BASELINE-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
- SEC-BASELINE-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
0ac8cb91c3cc a0491713834b c8423a2836b4 e0467e61b797
-->
