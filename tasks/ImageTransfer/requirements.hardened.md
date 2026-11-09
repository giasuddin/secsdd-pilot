# Requirements Document

## Introduction

API for uploading and sharing images (Image Upload and Share API).

## Requirements

### Requirement 1: Upload an image. Accept all formats

**User Story:** As a client, I want to allow users to upload images, returning a shareable link.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /upload, THE SYSTEM SHALL allow users to upload images, returning a shareable link.
   1.1. SEC-REQ-1.1-EC-306-1 [SECURITY: authentication-required] IF a request that the specification does not explicitly allow without authentication arrives without a valid authenticated session or signed token, THEN THE SYSTEM SHALL reject the request.
   1.2. SEC-REQ-1.1-EC-306-2-1 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL return no protected data in the rejection.
   1.3. SEC-REQ-1.1-EC-306-2-2 [SECURITY: authentication-enforcement] IF a request is rejected for missing authentication, THEN THE SYSTEM SHALL NOT process the request further.
   1.4. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.5. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

### Requirement 2: Share an image

**User Story:** As a client, I want to look at an image in the browser.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /images/{imageId}, THE SYSTEM SHALL look at an image in the browser.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
bfef8dcd2240 235b90cf6b7b
-->
