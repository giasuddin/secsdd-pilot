# Requirements Document

## Introduction

Webapp implementing a simple warehouse page (Merchant WebApp API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Register a new merchant

**User Story:** As a client, I want to register a new merchant.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /merchants/register, THE SYSTEM SHALL register a new merchant.

### Requirement 2: Merchant login

**User Story:** As a client, I want to authenticate a merchant with email and password.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /merchants/login, THE SYSTEM SHALL authenticate a merchant with email and password.

### Requirement 3: Lets a merchant upload their wares as a CSV string with the following columns: name, description, price

**User Story:** As a client, I want to let a merchant upload their wares as a CSV string with the following columns: name, description, price.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /merchants/upload-wares, THE SYSTEM SHALL let a merchant upload their wares as a CSV string with the following columns: name, description, price.

### Requirement 4: Retrieve all offered wares and merchants offering the wares, filtered with the provided query

**User Story:** As a client, I want to retrieve all offered wares and merchants offering the wares, filtered with the provided query.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /wares, THE SYSTEM SHALL retrieve all offered wares and merchants offering the wares, filtered with the provided query.
