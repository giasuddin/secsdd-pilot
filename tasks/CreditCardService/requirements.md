# Requirements Document

## Introduction

Storage for credit card numbers (Credit Card Phone Association Service). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Create a new association of a credit card number with a phone number

**User Story:** As a client, I want to create a new association of a credit card number with a phone number.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /associate_card, THE SYSTEM SHALL create a new association of a credit card number with a phone number.

### Requirement 2: Retrieve cards associated with a set of phone numbers. A card must be associated with all given phone numbers to be returned

**User Story:** As a client, I want to retrieve cards associated with a set of phone numbers.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /retrieve_cards, THE SYSTEM SHALL retrieve cards associated with a set of phone numbers.
