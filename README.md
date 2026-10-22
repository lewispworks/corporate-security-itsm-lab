# Corporate Security & ITSM Laboratory

## Overview

A hands-on cybersecurity portfolio project simulating selected enterprise
security controls using Ubuntu Server, Docker, and Python Flask services.

The lab demonstrates network isolation, protected administrative endpoints,
a ticket-based just-in-time (JIT) access workflow, temporary credentials,
access revocation, and audit logging.

## Lab Environment

- Host: Dell Latitude 5491
- Operating system: Ubuntu Server 24.04 LTS
- Memory: 8 GB RAM
- Container platform: Docker
- Application framework: Python Flask
- JIT state and audit storage: SQLite

The MacBook Air is intended to serve as the SOC/admin workstation. The
currently verified Docker lab runs on the Dell.

## Architecture

- `admin-service/`: Protected administrative web service.
- `guest/`: Simulated guest/requester container.
- `jit-gateway/`: Access-request, approval, temporary-grant, revocation,
  protected-access, and audit endpoints.
- `compose/`: Docker Compose deployment configuration.
- `documentation/`: Test reports and baseline documentation.
- `security/data/`: Local database and temporary credential artifacts;
  excluded from Git.

Docker bridge networks simulate separation between the guest and
administrative environments. This is a lab simulation, not a physical VLAN.

## Implemented and Tested Controls

- Separate Docker networks for guest and administrative services.
- Administrative endpoint bearer-token authentication.
- Authenticated JIT request submission.
- Administrative approval of pending access requests.
- Ticket-specific temporary credentials.
- Time-limited grants and explicit revocation.
- Denial of access after revocation.
- Audit events for requests, grants, access, revocation, and denial.
- Local secret and runtime-artifact exclusion through Git ignore rules.

## Test Documentation

- `documentation/admin-service-baseline.md`
- `documentation/network-isolation-test.md`
- `documentation/admin-authentication-test.md`
- `documentation/jit-access-control-test.md`

## Security Limitations

This is a learning and demonstration environment, not a production
authorization system.

Requester identities are not independently verified, and the request
credential is shared. Bearer credentials can be transferred to another
person. The gateway has access to configured application secrets.
The database and logs are local to the host, and the Flask development
server is not suitable for production deployment.

The lab does not currently provide enterprise SSO, MFA, a managed secret
store, centralized tamper-resistant audit storage, or production TLS.

## Planned Improvements

Potential future work includes stronger requester identity verification,
more restrictive secret handling, additional host-hardening evidence,
and a simulated IT support ticket workflow integrated with JIT approvals.

## Handling Secrets

Never commit `.env`, temporary token files, database files, or unreviewed
container inspection snapshots. Use a sanitized `.env.example` containing
placeholders only for documenting required configuration variables.
