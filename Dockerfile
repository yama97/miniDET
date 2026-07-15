FROM ubuntu:24.04

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
      iproute2 \
      iputils-ping \
      tcpdump \
      python3 \
      python3-pip \
      net-tools \
      procps \
      jq \
      vim-tiny && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["sleep", "infinity"]
