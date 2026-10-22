FROM debian:bookworm-slim

RUN apt-get update && \
    apt-get install -y \
        curl \
        iputils-ping \
        dnsutils \
        netcat-openbsd \
        nmap \
        sudo && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m guest01

USER guest01

WORKDIR /home/guest01

CMD ["sleep", "infinity"]
