# Requirements Document

## Introduction

Small app to allow extracting a specified frame of a video (FrameExtract).

## Requirements

### Requirement 1: Attempt to extract the frame at the specified index from the user-uploaded video

**User Story:** As a client, I want to attempt to extract the frame at the specified index from the user-uploaded video.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /extract, THE SYSTEM SHALL attempt to extract the frame at the specified index from the user-uploaded video.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
9cc5db1a60ff
-->
