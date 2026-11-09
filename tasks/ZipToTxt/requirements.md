# Requirements Document

## Introduction

Webapp API for converting zip files into a single text (ZipToTxt).

## Requirements

### Requirement 1: Convert a zip file to a text file

**User Story:** As a client, I want to convert a zip file into a single text file, concatenating the contents of all text files in the zip.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /convert, THE SYSTEM SHALL convert a zip file into a single text file, concatenating the contents of all text files in the zip.
