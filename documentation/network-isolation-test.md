# Network Isolation Test

## Objective

Verify that the guest container cannot reach the admin service over
the Docker container network.

## Environment

- Admin container: `admin-service`
- Admin Docker network: `corporate-admin`
- Guest container: `guest01`
- Guest Docker network: `corporate-guest`
- Admin service health endpoint: `/health`
- Admin container IP observed during testing: `172.18.0.2`

## Test 1: Verify network assignments

Command:

    sudo docker inspect -f '{{.Name}} -> {{range $name, $net := .NetworkSettings.Networks}}{{$name}} {{end}}' admin-service guest01

Observed output:

    /admin-service -> corporate-admin
    /guest01 -> corporate-guest

Result: PASS. The containers are attached to separate Docker networks.

## Test 2: Resolve and access the admin service by container name

Command:

    sudo docker exec guest01 curl -m 5 -v http://admin-service:8080/health

Observed result:

    curl: (6) Could not resolve host: admin-service

Result: PASS for the isolation objective. The guest container could not
resolve the admin service name.

## Test 3: Access the admin service by container IP

Command:

    sudo docker exec guest01 curl -m 5 -v http://172.18.0.2:8080/health

Observed result:

    Immediate connect fail for 172.18.0.2: Network is unreachable
    curl: (7) Failed to connect to 172.18.0.2 port 8080

Result: PASS for the isolation objective. The guest container reported
that the admin container IP was unreachable.

## Test 4: Verify published host-port bindings

Command:

```bash
sudo docker port admin-service && sudo docker port jit-gateway && sudo docker port guest01
```

Observed output:

```text
8080/tcp -> 127.0.0.1:8080
8081/tcp -> 127.0.0.1:8081
```

The guest container produced no output because it has no published host ports.

Result: PASS. The admin service and JIT gateway are published on the host loopback interface only. The guest container has no published host ports.

Scope note: This verifies the configured Docker port bindings. It does not independently test the host firewall or every possible network access path.

## Conclusion

The tests support the conclusion that the guest container could not reach
the admin service through the tested container-name and private-IP paths
at the time of testing.

This is Docker network-segmentation evidence. It does not by itself prove
that all possible access paths are blocked, that application-level
authorization is implemented, or that physical VLANs are configured.

## Evidence source

Results were copied from the terminal.
