# Requirements Document

## Introduction

Small app to allow extracting a specified frame of a video (FrameExtract).

## Requirements

### Requirement 1: Attempt to extract the frame at the specified index from the user-uploaded video

**User Story:** As a client, I want to attempt to extract the frame at the specified index from the user-uploaded video.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /extract, THE SYSTEM SHALL attempt to extract the frame at the specified index from the user-uploaded video.
