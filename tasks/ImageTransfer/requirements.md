# Requirements Document

## Introduction

API for uploading and sharing images (Image Upload and Share API).

## Requirements

### Requirement 1: Upload an image. Accept all formats

**User Story:** As a client, I want to allow users to upload images, returning a shareable link.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /upload, THE SYSTEM SHALL allow users to upload images, returning a shareable link.

### Requirement 2: Share an image

**User Story:** As a client, I want to look at an image in the browser.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /images/{imageId}, THE SYSTEM SHALL look at an image in the browser.
