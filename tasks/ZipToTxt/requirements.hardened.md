# Requirements Document

## Introduction

Webapp API for converting zip files into a single text (ZipToTxt).

## Requirements

### Requirement 1: Convert a zip file to a text file

**User Story:** As a client, I want to convert a zip file into a single text file, concatenating the contents of all text files in the zip.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /convert, THE SYSTEM SHALL convert a zip file into a single text file, concatenating the contents of all text files in the zip.
   1.1. SEC-REQ-1.1-EC-319-1-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
   1.2. SEC-REQ-1.1-EC-319-1-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
a5c2c8b6f9e2
-->
