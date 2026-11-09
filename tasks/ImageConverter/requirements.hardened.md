# Requirements Document

## Introduction

Image converter web app (GIF Creator API).

## Requirements

### Requirement 1: Create a GIF from images

**User Story:** As a client, I want to accepts images, a target size, delay, and a flag to append a reverted version to create a GIF.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /create-gif, THE SYSTEM SHALL accepts images, a target size, delay, and a flag to append a reverted version to create a GIF.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
eac9d19d75c1
-->
