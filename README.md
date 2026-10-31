# Corporate Security & ITSM Laboratory

## Overview

A hands-on cybersecurity portfolio project simulating selected enterprise security controls using Ubuntu Server, Docker, and Python Flask services.

The lab demonstrates network isolation, protected administrative endpoints, a ticket-based Just-in-Time (JIT) access workflow, temporary credentials, access expiration, early revocation, and audit logging.

The project emphasizes layered security controls, access governance, verification, and technical documentation.

## Lab Environment

- **Host:** Dell Latitude 5491
- **Operating system:** Ubuntu Server 24.04 LTS
- **Memory:** 8 GB RAM
- **Container platform:** Docker
- **Application framework:** Python Flask
- **JIT state and audit storage:** SQLite

The MacBook Air is intended to serve as the SOC/admin workstation. The currently verified Docker lab runs on the Dell.

## Architecture

- `admin-service/`: Protected administrative web service.
- `guest/`: Simulated guest/requester container.
- `jit-gateway/`: Access-request, approval, temporary-grant, revocation, protected-access, and audit endpoints.
- `compose/`: Docker Compose deployment configuration.
- `documentation/`: Test reports, baseline documentation, and security control matrix.
- `security/data/`: Local database and temporary credential artifacts; excluded from Git.

Docker bridge networks simulate separation between the guest and administrative environments. The JIT gateway connects to both networks and mediates authorized access. The guest container cannot directly resolve the administrative service through its Docker network.

This is a lab simulation, not a physical VLAN implementation.

## Implemented and Tested Controls

- Separate Docker networks for guest and administrative services.
- Administrative endpoint Bearer-token authentication.
- Authenticated JIT request submission.
- Requester identity enforcement using a fixed simulated identity (`guest01`) rather than a caller-supplied identity.
- Administrative approval and denial of pending access requests.
- Ticket-specific temporary credentials.
- Time-limited grants with expiration enforcement.
- Early revocation of approved grants.
- Denial of access after expiration or revocation.
- Audit events for requests, decisions, grants, successful access, expiration, revocation, and denial.
- Local secret and runtime-artifact exclusion through Git ignore rules.
- Application health endpoints for service monitoring.

### JIT Access Workflow

1. The simulated requester submits an access request using the configured request credential.
2. The gateway creates a ticket and records the simulated requester identity.
3. An administrator reviews the request and approves or denies it.
4. An approved request receives a ticket-specific temporary credential.
5. Access is permitted while the grant is active.
6. Access is denied when the grant expires or is revoked.
7. The gateway records relevant request, decision, and access events in its audit log.

### ITSM Workflow Integration

Spiceworks Cloud Help Desk was used to simulate an enterprise IT support ticket lifecycle associated with privileged-access requests.

The workflow demonstrated:

1. Submission and acknowledgment of an IT support request.
2. Documentation of business justification and simulated business-owner approval.
3. Coordination between IT Support and the SOC Administrator.
4. Independent JIT approval through the gateway.
5. Verification of temporary access and automatic expiration.
6. Documentation of security results and ticket closure.

The Spiceworks ticket was linked to its corresponding JIT gateway request to maintain traceability between the ITSM process and technical access-control evidence.

The integration was performed through a coordinated manual workflow rather than an automated Spiceworks API connection.

## Test Documentation

- `documentation/admin-service-baseline.md`
- `documentation/network-isolation-test.md`
- `documentation/admin-authentication-test.md`
- `documentation/jit-access-control-test.md`
- `documentation/security-control-matrix.md`
- `documentation/itsm-jit-access-case-study.md`

The test reports document observed results and the scope of each verification. The security control matrix maps implemented controls to their corresponding evidence.

## Security Limitations

This is a learning and demonstration environment, not a production authorization system.

Requester identities are not independently verified, and the request credential is shared. The gateway assigns a fixed simulated identity, but this does not establish the real-world identity of the person submitting a request.

Bearer credentials can be transferred to another person. The gateway has access to configured application secrets to perform its authorization and protected-access functions.

The database and logs are local to the host, and the Flask development server is not suitable for production deployment.

The lab does not currently provide enterprise SSO, MFA, a managed secret store, centralized tamper-resistant audit storage, or production TLS.

Docker network separation does not demonstrate physical VLAN configuration. The documented test results apply to the specific lab configuration and access paths tested; they are not an independent penetration test or formal compliance assessment.

## Planned Improvements

Potential future enhancements include:

- Stronger requester identity verification through individual accounts and enterprise identity integration.
- Multi-factor authentication for privileged-access approvals.
- More restrictive secret handling and automated credential lifecycle management.
- Production-grade application hosting behind a WSGI server.
- TLS implementation and centralized, tamper-resistant audit storage.
- Additional host-hardening evidence and security validation.
- Expanded monitoring, alerting, and automated security testing.

## Handling Secrets

Never commit `.env`, temporary token files, database files, or unreviewed container inspection snapshots.

Use a sanitized `.env.example` containing placeholders only for documenting required configuration variables.

Review Git ignore rules and staged changes before committing project updates. Never include actual credentials or temporary access tokens in screenshots, documentation, or source control.

The JIT gateway returns temporary bearer credentials once upon approval and stores their SHA-256 hashes in the SQLite database rather than storing plaintext credentials. Temporary credentials saved during testing are kept locally under security/data/ with restrictive file permissions and excluded from Git.
