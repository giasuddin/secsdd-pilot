# Requirements Document

## Introduction

Webapp for product recommendation by searched tags (Recommendation). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get all posted products that match at least one of the provided tags

**User Story:** As a client, I want to get all posted products that match at least one of the provided tags.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /recommender, THE SYSTEM SHALL get all posted products that match at least one of the provided tags.

### Requirement 2: Post a new product along with its tags

**User Story:** As a client, I want to post a new product along with its tags.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recommender, THE SYSTEM SHALL post a new product along with its tags.
