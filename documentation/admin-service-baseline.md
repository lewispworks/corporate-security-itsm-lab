# Admin Service — Initial Baseline

## Objective
Build a small internal web application for testing network access and authorization controls.

## Environment
- Host: Dell Latitude 5491
- Operating system: Ubuntu Server 24.04 LTS
- Runtime: Docker
- Application: Python / Flask
- Listening port: TCP 8080

## Initial Results
- Home endpoint: HTTP 200
- Public endpoint: HTTP 200
- Internal endpoint: HTTP 200
- Admin endpoint: HTTP 200
- Health endpoint: HTTP 200

## Initial Security Observation
The application returns a successful response from the administrative endpoint without an application-level authorization check.

## Limitation
These tests establish local application functionality only. Guest-to-service connectivity and network isolation have not yet been tested.

## Evidence
- Screenshot: initial service response
- Screenshot: initial administrative endpoint response

## Next Step
Build the guest container and test connectivity from the simulated guest environment.
