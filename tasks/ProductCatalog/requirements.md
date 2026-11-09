# Requirements Document

## Introduction

Catalog of products with multiple unstructured properties (Product Catalog). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Add a new product to the catalog

**User Story:** As a client, I want to add a new product to the catalog.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /add, THE SYSTEM SHALL add a new product to the catalog.

### Requirement 2: Download the entire current catalog with its unstructured properties for a given product name as a data entry

**User Story:** As a client, I want to download the entire current catalog with its unstructured properties for a given product name as a data entry.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /download, THE SYSTEM SHALL download the entire current catalog with its unstructured properties for a given product name as a data entry.

### Requirement 3: Upload data for a product with the given name in the catalog. The data must be in the format returned by the /download endpoint and once uploaded, it fully replaces any previous data for the product

**User Story:** As a client, I want to upload data for a product with the given name in the catalog.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /upload, THE SYSTEM SHALL upload data for a product with the given name in the catalog.

### Requirement 4: Search for products in the catalog

**User Story:** As a client, I want to search for products in the catalog.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /search, THE SYSTEM SHALL search for products in the catalog.
