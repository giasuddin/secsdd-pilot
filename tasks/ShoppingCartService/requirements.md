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
