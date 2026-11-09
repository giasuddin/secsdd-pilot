# Requirements Document

## Introduction

Calculator web app (MyCalculator).

## Requirements

### Requirement 1: Calculate the result of an arithmetic expression

**User Story:** As a client, I want to calculate the result of an arithmetic expression.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /calculator, THE SYSTEM SHALL calculate the result of an arithmetic expression.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
8a843c6ccb10
-->
