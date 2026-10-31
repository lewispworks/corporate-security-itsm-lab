# ITSM and Just-in-Time Privileged Access Case Study

## 1. Project Overview

This case study demonstrates an integrated IT Service Management (ITSM)
and Just-in-Time (JIT) privileged-access workflow using Spiceworks Cloud
Help Desk and a Docker-based cybersecurity lab.

The objective was to demonstrate how a privileged-access request can be
documented, reviewed, approved, time-limited, monitored, and closed.

This was a simulated corporate environment. No actual industrial control
equipment or production HMI systems were accessed.

## 2. Scenario

An IT Engineer required temporary administrative access to an HMI
administrative interface to investigate an authentication and connectivity
issue.

The request explicitly excluded PLC logic modifications and process-control
changes.

- ITSM platform: Spiceworks Cloud Help Desk
- Spiceworks ticket: #3
- Resource: HMI administrative interface
- Requested access duration: 30 minutes
- JIT gateway request: JIT-88DDB8C8B88E

## 3. ITSM Workflow

The request was submitted and tracked through Spiceworks.

IT Support:
- Received and acknowledged the request.
- Documented the business justification.
- Recorded the simulated business-owner approval.
- Coordinated the request with the SOC Administrator.
- Communicated the approval and access limitations to the requester.
- Documented the final outcome and closed the ticket.

SOC Administrator:
- Reviewed the JIT request.
- Approved the temporary access window.
- Verified that access was available during the authorized period.
- Reviewed the gateway audit record after expiration.

## 4. Technical JIT Workflow

The JIT gateway enforced the temporary access authorization.

The workflow consisted of:

1. Guest requester authenticated to the JIT gateway.
2. Gateway created a pending access request.
3. SOC Administrator reviewed and approved the request.
4. Gateway issued a temporary bearer credential.
5. Requester accessed the protected service.
6. Authorization automatically expired after 30 minutes.
7. Subsequent access was denied.

Temporary credentials were not included in project documentation or
committed to Git.

## 5. Test Results

| Test | Expected Result | Observed Result |
|---|---|---|
| Request submission | HTTP 201 | PASS |
| Administrator approval | HTTP 200 | PASS |
| Access during active grant | HTTP 200 | PASS |
| Access after expiration | HTTP 403 | PASS |
| Audit expiration record | Reason: expired | PASS |

JIT request: JIT-88DDB8C8B88E

The gateway audit log recorded the expiration reason as `expired`.

No manual revocation was performed on this test grant. The access window
was allowed to expire naturally.

## 6. Troubleshooting and Remediation

During audit-log verification, the gateway returned HTTP 500.

The application traceback identified a TypeError in the token comparison
function. The issue occurred because hmac.compare_digest() was comparing
string values containing non-ASCII characters.

The comparison was corrected to encode both values as UTF-8 bytes before
performing the constant-time comparison.

The application passed Python syntax validation, the gateway was rebuilt,
and the audit endpoint subsequently returned the expected audit records.

## 7. Security Controls Demonstrated

- Authenticated access requests
- Administrator approval before privileged access
- Temporary bearer credentials
- Time-limited authorization
- Automatic expiration
- Denial of access after expiration
- Audit logging of access decisions and expiration
- Separation of IT Support and SOC Administrator responsibilities
- Documentation of the request lifecycle

## 8. Outcome

The simulated ITSM and JIT workflow completed successfully.

The requester received temporary access during the approved period.
After the authorization window elapsed, the gateway denied subsequent
access and recorded the expiration event.

IT Support documented the outcome and closed Spiceworks ticket #3.

## 9. Scope and Limitations

This project is a portfolio lab and not a production JIT implementation.

The environment uses Docker containers and a simulated protected
administrative service rather than physical VLAN infrastructure or
industrial control equipment.

The requester identity and shared request credential are simplified
for demonstration purposes. Production deployments would require
integration with enterprise identity management, stronger individual
authentication, and additional operational safeguards.

The lab demonstrates selected access-control and ITSM principles;
it does not constitute a formal compliance assessment or penetration test.
