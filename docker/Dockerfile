FROM ubuntu:18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
  software-properties-common python3-venv make git vim nginx

WORKDIR /opt
ARG NOCACHE=1
RUN git clone https://github.com/drkeoni/hrsync.git && \
    cd /opt/hrsync && \
    git submodule update --init --recursive

WORKDIR /opt/hrsync
RUN make create-ve setup

RUN make build-site

COPY config/nginx/hrsync /etc/nginx/sites-available
RUN ln -s /etc/nginx/sites-available/hrsync /etc/nginx/sites-enabled/hrsync && \
    rm /etc/nginx/sites-enabled/default && \
    mkdir -p /opt/log/nginx

COPY bin/start-hrsync-server /usr/local/bin

EXPOSE 80
VOLUME ["/opt/log/hrsync"]

CMD ["/usr/local/bin/start-hrsync-server"]
