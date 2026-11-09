# Requirements Document

## Introduction

API for monitoring the status of services (Service Monitoring API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Register a heartbeat for a service

**User Story:** As a client, I want to accepts a request to signify that a specific service is still alive.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /heartbeat, THE SYSTEM SHALL accepts a request to signify that a specific service is still alive.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Get overview of registered services

**User Story:** As a client, I want to provides an overview of registered services and their last notification date, where the token of this request matches the token sent with the service request.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /services, THE SYSTEM SHALL provides an overview of registered services and their last notification date, where the token of this request matches the token sent with the service request.
   1.1. SEC-REQ-2.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-2.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-2.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.
   1.4. SEC-REQ-2.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.5. SEC-REQ-2.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
33808f4fdae1 39f8b1b29b70
-->
