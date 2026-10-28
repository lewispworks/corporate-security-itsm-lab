# Just-in-Time (JIT) Access Control Test Report

## 1. Objective

Validate a simulated just-in-time (JIT) access workflow in which a
requester submits an access request, an administrator approves or denies
it, and an approved temporary credential grants time-limited access to
a protected administrative resource.

The test also evaluates explicit revocation and audit logging.

## 2. Lab Components

- `guest01`: Simulated requester.
- `jit-gateway`: Handles requests, approvals, temporary grants, revocation,
  protected-resource access, and audit events.
- `admin-service`: Protected Flask administrative service.
- SQLite database: Stores ticket state, credential hashes, and audit events.

The gateway is published on the host loopback interface at
`127.0.0.1:8081`. The protected admin service is published on
`127.0.0.1:8080`. These are local lab endpoints, not public service
addresses.

## 3. Test Results

### Test A — Request authentication

- A request without the required request credential returned HTTP 401.
- A request with the configured request credential created a pending
  ticket and returned HTTP 201.

**Result: PASS**

### Test A2 — Requester identity enforcement

- A request without the required request credential returned HTTP 401.
- A request with an invalid request credential returned HTTP 401.
- A request body claiming the requester was `administrator` was submitted with a valid request credential.
- The resulting ticket recorded the requester as `guest01`, confirming that the gateway does not trust the caller-supplied identity.

**Result: PASS**

**Scope note:** This verifies identity-field spoofing protection for the simulated `guest01` requester. It does not independently authenticate individual people because the lab uses a shared request credential.

### Test B — Administrative request listing

- An authenticated administrative request to `GET /admin/requests`
  returned HTTP 200.
- The pending ticket appeared in the response with its requested
  duration and no approval or expiry timestamp yet.

**Result: PASS**

### Test C — Approval and temporary credential

- An administrator approved a pending ticket.
- The approval response returned a ticket-specific temporary bearer
  credential and an expiry timestamp.
- The credential was saved locally with restrictive file permissions
  for testing. Its value was not included in this report.

The gateway stores a hash of the temporary credential rather than
storing the plaintext credential in the ticket record.

**Result: PASS**

### Test D — Access while a grant is active

For ticket `JIT-08C4F65EB206`, an access request made immediately after
approval returned HTTP 200 with an administrative access-granted
response.

**Result: PASS**

### Test E — Expired grant

A one-minute grant was later used after its access window had elapsed.
The gateway returned HTTP 403 with an error indicating that the grant
had expired or been revoked.

This confirms that access was blocked after the short grant was no
longer usable. The separate audit record should be consulted when
distinguishing expiry from revocation for an individual ticket.

**Result: ACCESS BLOCKED; EXPIRY AUDIT REVIEW RECOMMENDED**

### Test F — Explicit revocation before scheduled expiry

Ticket `JIT-9139F5E6D79E` was approved for five minutes.

The test produced the following results:

1. Access before revocation returned HTTP 200.
2. The administrator revoked the grant and received HTTP 200.
3. An immediate subsequent access attempt returned HTTP 403.

The ticket's audit events included:

- `request_submitted`
- `access_granted`
- `access_allowed`
- `access_revoked`
- `access_denied`, with reason `revoked`

The audit timestamps show successful access, then revocation, then denial.
The denial occurred approximately 0.14 seconds after the successful
access event, with the revocation event recorded between them.

**Result: PASS**

## Test G: Expiration enforcement and audit logging

**Objective:** Verify that an approved JIT grant permits access while active, denies access after expiration, and records the expiration and denial events.

**Procedure and results:**

1. Reused pending request `JIT-3E257E80E47B` and approved it for its configured five-minute duration.
2. Used the issued temporary token to access the protected endpoint while the grant was active.
   - Result: HTTP 200 — PASS.
3. Retried access after the grant expired.
   - Result: HTTP 403; response indicated the grant had expired or been revoked — PASS.
4. Inspected the gateway audit log for the ticket.
   - Observed event sequence: `request_submitted`, `access_granted`, `access_allowed`, `access_expired`, `access_denied` — PASS.
   - Confirmed the `access_denied` event details reported `"reason": "expired"` — PASS.

**Conclusion:** The gateway permitted access during the authorized window and denied access after expiration. Audit events recorded the request, approval, successful access, expiration, and subsequent denial.

**Scope note:** This validates the JIT expiration behavior in the local Docker lab. It does not establish that the implementation meets all production identity, access-management, or compliance requirements.

## 4. Security Controls Demonstrated

- Authentication required to submit an access request.
- Administrative authentication required for privileged gateway actions.
- Pending requests require an administrative decision.
- Each approved ticket receives its own temporary bearer credential.
- Temporary credentials are stored as hashes in the gateway database.
- Grants have a configured duration and expiry timestamp.
- Administrators can revoke grants before their scheduled expiry.
- The gateway blocks access through expired or revoked grants.
- Audit events record key request, approval, access, revocation, and
  denial activity.
- Local database and credential artifacts are excluded from Git through
  the repository's ignore rules.

## 5. Lab Limitations and Production Considerations

This is a portfolio simulation, not a production JIT authorization system.

- The gateway assigns the fixed simulated requester identity `guest01`
  rather than trusting an identity supplied in the request body. The shared
  request credential does not independently verify a real-world person's
  identity; anyone who obtains it can submit requests as `guest01`.
- A bearer credential can be used by anyone who obtains it while the
  grant remains active. The credential itself is not bound to a verified
  user or device.
- The gateway has access to the configured administrative and request
  secrets. A production design should use stronger secret isolation and
  a managed secret store.
- The lab uses a local SQLite database on one host; it does not provide
  high availability or distributed coordination.
- The service currently uses Flask's development server. It should not
  be exposed as a production service without a production WSGI server
  and appropriate deployment controls.
- The endpoints are bound to host loopback for this lab, and this setup
  does not implement production TLS, SSO, MFA, or an enterprise identity
  provider.
- Audit events are useful test evidence but are stored locally; a
  production system should protect logs against tampering and forward
  them to centralized monitoring.

## 6. Conclusion

The lab demonstrated a JIT-style access lifecycle: request, administrative
approval, temporary access, and explicit revocation. The five-minute
revocation test confirmed that an active grant could be revoked and that
a subsequent request was denied before the scheduled expiry.

The results provide evidence of access-control enforcement and audit
logging while clearly identifying the identity, deployment, and
operational controls that would be needed for a production implementation.
