# Requirements Document

## Introduction

API for maintaining a shopping cart (Shopping Cart Service). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Create a new shopping cart

**User Story:** As a client, I want to create a new shopping cart.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /create_cart, THE SYSTEM SHALL create a new shopping cart.

### Requirement 2: Add or remove items from the cart

**User Story:** As a client, I want to add or remove items from the cart.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /add_to_cart, THE SYSTEM SHALL add or remove items from the cart.

### Requirement 3: Retrieve all items in the cart

**User Story:** As a client, I want to retrieve all items in the cart.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /retrieve_cart, THE SYSTEM SHALL retrieve all items in the cart.

## Security Baseline (Cross-Cutting)

These constraints apply to every requirement above. They are stated once here rather than repeated under each requirement.

- SEC-BASELINE-1 [SECURITY: transport-encryption] THE SYSTEM SHALL transmit all sensitive data exclusively over TLS 1.2 or higher.
- SEC-BASELINE-2 [SECURITY: transport-encryption] THE SYSTEM SHALL NOT transmit sensitive information over an unencrypted channel.

<!-- spec-it-safe:reviewed v1
Requirements already hardened by Specification Hardening Engine, as hashes of their text.
A re-run hardens only requirements whose hash is missing here.
7bcc4967b769 3a4e60e5a794 a9e4559c4eba
-->
