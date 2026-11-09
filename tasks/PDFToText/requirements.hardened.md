# Requirements Document

## Introduction

API for extracting the text part of PDF files and retrieving it as plain text (PDF to Text Converter API).

## Requirements

### Requirement 1: Convert a PDF file to Text

**User Story:** As a client, I want to upload a PDF file to convert it into Text format.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /convert, THE SYSTEM SHALL upload a PDF file to convert it into Text format.
   1.1. SEC-REQ-1.1-EC-434-1-1 [SECURITY: file-type-validation] WHEN a user uploads a file, THE SYSTEM SHALL validate the file's magic bytes against an allowlist of permitted MIME types.
   1.2. SEC-REQ-1.1-EC-434-1-2 [SECURITY: file-type-validation] WHEN a user uploads a file, THE SYSTEM SHALL reject files whose extension does not match their detected content type.
   1.3. SEC-REQ-1.1-EC-434-2-1 [SECURITY: upload-storage-isolation] WHEN a user uploads a file, THE SYSTEM SHALL enforce a maximum file size of the configured limit.
   1.4. SEC-REQ-1.1-EC-434-2-2 [SECURITY: upload-storage-isolation] WHEN a user uploads a file, THE SYSTEM SHALL store uploaded files outside every directory the system serves or executes files from, under a randomized filename and without execute permission.
   1.5. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.6. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
b8ef6c960fd1
-->
