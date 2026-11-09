# Requirements Document

## Introduction

Endpoint to decide whether a user requested to be unsubscribed from a mailing list (UnsubscribeApp).

## Requirements

### Requirement 1: Expects a raw E-Mail from a user (i.e. reply to a mailing list) and returns whether the user who sent the email should be unsubscribed together with the user's E-Mail address. Emails requesting to be unsubscribed are expected to contain related keywords or phrases such as "unsubscribe", "remove me", "deregister me", "stop sending me", or "delete me"

**User Story:** As a client, I want to expect a raw E-Mail from a user.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /decideUnsubscribe, THE SYSTEM SHALL expect a raw E-Mail from a user.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
e08cbe6f4320
-->
