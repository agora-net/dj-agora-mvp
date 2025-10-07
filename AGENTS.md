---
description: Describes the Agora project, layout, where to find additional context
version: 1.0
tags: ["agora", "project", "core-behavior"]
---

# AI Agent Instructions: Secure Python Project

You are an expert Python and Django developer focused on writing secure, simple, and maintainable code.

## Core Principles

1. Security First: Prioritize security in all code. Explicitly state potential security risks and implement mitigations.
1. Simplicity: Write the simplest possible code that fulfills the requirement. Avoid over-engineering.
1. Prefer Standard Library: Use the standard library over external packages whenever it is practical and does not compromise security or essential functionality.
1. Context is Key: When dealing with external libraries (e.g., Keycloak, Ondato, Stripe), use context7 to fetch the latest, version-specific documentation and examples.

## Running Python

Use `uv` to run python commands in a virtual environment.

Bad: `python -c 'print("hello world")'`
Good: `uv run python -c 'print("hello world")'`

## Run commands regularly

Use `just` to run commands. Check the `@/Justfile` for available commands.

Examples:

- `just lint-backend` and `just format-backend` should be used when making backend code changes.

## Additional context

When looking for library documentation:

- Use MCP server "context 7" for the latest library docs and best practices

Refer to the following files for additional context depending on purpose:

- When writing git commits: @/.cursor/rules/conventional-commit.mdc

## Working Behaviour

When working on a new feature/bugfix etc, create and checkout a new Git branch to keep changes separate.

- feature/new-feature-name
- bug/bug-name

## Project Structure & Tooling

### Running the project

Assume the project is already running with hot reload functionality. The app runs in a docker container. To access the app you have to go through `https://app.local.agora.gdn/`. To view the logs of the container use `podman compose logs app`. Keycloak is also running in docker, it is available at `https://idp.local.agora.gdn/`.

### Project Layout

This project follows the standard Django layout.

Project apps are in @/agora/apps.

Project Scope: @/README.md

Task Runner (just): When asked to create reusable tasks, add them to the justfile. Each task must have a documentation comment explaining what it does.

### Libraires

## Django Development: Secure by Default

Security is a TOP PRIORITY.

1. Input Validation: Treat all external input as untrusted. Validate everything on the server-side. Use libraries like `nh3` for sanitization.

## External Services: Security Focus

### Keycloak - Identity provider

**Core Principle**: Never handle user authentication tokens directly. All token validation is handled by the OAuth proxy in front of the application.

**API Interactions**:

- **Admin API Access**: Use Keycloak Admin API for server-side operations only
- **Service Account**: Create a dedicated service account with minimal required permissions
- **Client Credentials**: Use client credentials flow for API authentication
- **Scope Limitation**: Grant only the specific permissions needed (e.g., `manage-users`, `manage-clients`)

**Security Requirements**:

- **Environment Variables**: Store Keycloak credentials in environment variables, never in code
- **HTTPS Only**: Always use HTTPS for Keycloak API communication
- **Credential Rotation**: Implement regular credential rotation for service accounts
- **Audit Logging**: Log all Keycloak API operations for security auditing

**Common Operations**:

- **User Management**: Update user attributes, groups, and roles
- **Client Management**: Create/update OAuth clients programmatically
- **Realm Management**: Configure realms, roles, and policies
- **User Metadata**: Store and retrieve custom user attributes

**Error Handling**:

- **Graceful Degradation**: Handle Keycloak API failures gracefully
- **Retry Logic**: Implement exponential backoff for transient failures
- **Circuit Breaker**: Consider circuit breaker pattern for API calls
- **Fallback Behavior**: Define fallback behavior when Keycloak is unavailable

**Best Practices**:

- **Connection Pooling**: Reuse HTTP connections for API calls
- **Request Timeouts**: Set appropriate timeouts for all API requests
- **Rate Limiting**: Respect Keycloak's rate limits and implement backoff
- **Monitoring**: Monitor API response times and error rates

### Ondato Identity

    Server-Side Operations: All interactions with the Ondato API that require a secret key must be performed on the server. Never expose your Ondato secret key to the client.

    Verification Flow:

        Server: Create a VerificationSession from your Go backend.

        Server: Pass the client_secret from the session to the frontend.

        Client: Use the client_secret to initialize the Ondato.js Identity flow.

        Server: Use webhooks to securely receive verification results (identity.verification_session.verified, etc.). Verify the webhook signature to ensure the request is from Ondato.
