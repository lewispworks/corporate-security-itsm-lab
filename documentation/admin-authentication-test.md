# Application Authentication Test

## Objective

Verify that administrative and internal endpoints require a valid
bearer token while public and health endpoints remain available.

## Implementation

- `/admin` requires a valid bearer token.
- `/internal` requires a valid bearer token.
- The expected token is read from the `ADMIN_TOKEN` environment variable.
- Token comparison uses `hmac.compare_digest`.
- The token is stored in a local `.env` file excluded by `.gitignore`.

## Test results

| Endpoint | Test condition | Expected result | Observed result | Outcome |
|---|---|---|---|---|
| `/admin` | No token | 401 Unauthorized | 401 Unauthorized | PASS |
| `/admin` | Invalid token | 401 Unauthorized | 401 Unauthorized | PASS |
| `/admin` | Valid token | 200 OK | 200 OK | PASS |
| `/internal` | No token | 401 Unauthorized | 401 Unauthorized | PASS |
| `/internal` | Valid token | 200 OK | 200 OK | PASS |
| `/health` | No token | 200 OK | 200 OK | PASS |
| `/public` | No token | 200 OK | 200 OK | PASS |
| `/` | No token | 200 OK | 200 OK | PASS |

## Security significance

The administrative and internal endpoints previously returned their
resources without requiring credentials. Both now deny requests without
a valid bearer token.

This demonstrates application-level access control alongside the
Docker network segmentation tested separately.

## Scope and limitations

This is a portfolio lab implementation, not a production authentication
system. A shared bearer token is a simple demonstration of access control,
not a complete identity or authorization solution.

A production design would consider TLS, centralized secret management,
token rotation, audit logging, identity-based authorization, and
appropriate protections against secret exposure.

The public and health endpoints intentionally remain accessible without
a token. Their suitability for exposure depends on the deployment context.
