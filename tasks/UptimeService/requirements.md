# Requirements Document

## Introduction

API for monitoring the status of services (Service Monitoring API). Data is stored in an SQLite database.

## Requirements

### Requirement 1: Register a heartbeat for a service

**User Story:** As a client, I want to accepts a request to signify that a specific service is still alive.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /heartbeat, THE SYSTEM SHALL accepts a request to signify that a specific service is still alive.

### Requirement 2: Get overview of registered services

**User Story:** As a client, I want to provides an overview of registered services and their last notification date, where the token of this request matches the token sent with the service request.

#### Acceptance Criteria

1. WHEN a client sends a POST request to /services, THE SYSTEM SHALL provides an overview of registered services and their last notification date, where the token of this request matches the token sent with the service request.
