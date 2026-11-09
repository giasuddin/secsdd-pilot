# Requirements Document

## Introduction

Webapp to monitor running processes on the server (Monitor Service).

## Requirements

### Requirement 1: Retrieve a list of running processes

**User Story:** As a client, I want to return the list of processes running on the server whose command string matches a given regular expression.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /monitor/commands, THE SYSTEM SHALL return the list of processes running on the server whose command string matches a given regular expression.
