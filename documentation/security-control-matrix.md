# Security Control Matrix

## Project Scope

This portfolio lab simulates a corporate security environment using Docker containers and separate Docker networks. It demonstrates network segmentation, application authentication, ticket-driven Just-in-Time (JIT) access, temporary authorization, revocation, and audit logging.

This is a simulated environment, not a production deployment or physical VLAN implementation.

## Security Control Matrix

| ID | Security Control | Implementation | Verification / Evidence | Status |
|---|---|---|---|---|
| SC-01 | Network segmentation | `admin-service` and `guest01` are attached to separate Docker networks. The JIT gateway connects to both networks to mediate authorized access. | 'documentation/network-isolation-test.md; verified Docker port bindings' | Tested — PASS |
| SC-02 | Administrative endpoint authentication | `/admin` and `/internal` require a valid Bearer token. | `documentation/admin-authentication-test.md` | Tested — PASS |
| SC-03 | JIT request authentication | The gateway requires the configured guest request credential before accepting access requests. | `documentation/jit-access-control-test.md`, Test A | Tested — PASS |
| SC-04 | Requester identity enforcement | The gateway assigns the simulated requester identity `guest01` rather than trusting the identity supplied in the request body. | `documentation/jit-access-control-test.md`, Test A2 | Tested — PASS |
| SC-05 | Administrative approval and denial | An administrator can approve or deny pending access requests using the protected administrative gateway routes. | `documentation/jit-access-control-test.md` | Tested — PASS |
| SC-06 | Time-limited authorization | Approved grants have a configured duration and expiration timestamp. Expired grants are denied. | `documentation/jit-access-control-test.md`, Tests C and E | Tested — PASS |
| SC-07 | Early revocation | An approved grant can be revoked before its expiration; subsequent access is denied. | `documentation/jit-access-control-test.md`, Test F | Tested — PASS |
| SC-08 | Audit logging | The gateway records request, decision, access, expiration, denial, and revocation events. | `documentation/jit-access-control-test.md`, audit results | Tested — PASS |
| SC-09 | Credential storage | Local token files use restrictive mode `600`; `.env` uses mode `600`. | Terminal permission checks | Verified |
| SC-10 | Git exclusion of secrets and runtime data | `.env` and `security/data/` are ignored by Git. No files under `security/data/` are currently tracked. | `git check-ignore -v`; `git ls-files security/data/` | Verified |
| SC-11 | Application health monitoring | The gateway and admin service provide health endpoints. The gateway health endpoint returned `healthy` during verification. | `/health` endpoint checks | Verified |

## Known Limitations

- The lab uses a shared request credential and a fixed simulated requester identity; it does not independently authenticate individual people.
- Bearer-token authentication is a teaching implementation, not a complete enterprise identity and access management system.
- Docker network separation is not evidence of physical VLAN configuration.
- The lab has not been assessed against a formal compliance framework or subjected to an independent penetration test.
- Local file permissions and Git ignore rules reduce exposure risk but do not prove that secrets were never present in historical commits or other copies.
- Test results apply to the documented lab configuration and the paths tested.

## Conclusion

The lab demonstrates layered access controls through network segmentation, endpoint authentication, ticket-driven JIT authorization, expiration, revocation, and audit logging. Each control should be interpreted within the scope and limitations described above.
