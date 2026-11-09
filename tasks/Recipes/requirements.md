# Requirements Document

## Introduction

API for uploading, commenting and rating recipes (Recipe Sharing App API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Get an overview of recipes

**User Story:** As a client, I want to retrieve a summary of recent and top-rated recipes.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /recipes, THE SYSTEM SHALL retrieve a summary of recent and top-rated recipes.

### Requirement 2: Upload a new recipe

**User Story:** As a client, I want to allow a user to upload a new recipe.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recipes/upload, THE SYSTEM SHALL allow a user to upload a new recipe.

### Requirement 3: Get a recipe

**User Story:** As a client, I want to retrieve a recipe by its ID.

#### Acceptance Criteria

1. WHEN a client sends a GET request to /recipes/{recipeId}, THE SYSTEM SHALL retrieve a recipe by its ID.

### Requirement 4: Add a comment to a recipe

**User Story:** As a client, I want to allow a user to add a comment to a recipe.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recipes/{recipeId}/comments, THE SYSTEM SHALL allow a user to add a comment to a recipe.

### Requirement 5: Rate a recipe

**User Story:** As a client, I want to allow a user to rate a recipe.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /recipes/{recipeId}/ratings, THE SYSTEM SHALL allow a user to rate a recipe.
