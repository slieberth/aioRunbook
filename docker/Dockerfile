# aioRunbook demo 

FROM ubuntu:16.04

MAINTAINER Stefan Lieberth: 0.1

RUN apt-get update && apt-get install -y \
    sudo \
    iputils-ping \
    net-tools \
    vim \
    curl \
    wget \
    tcl \
    python3  \
    python3-pip \
    python3-tk \
    git \
    ssh
RUN pip3 install git+https://github.com/slieberth/aioRunbook.git
RUN && mkdir aioRunbook  \
    && cd aioRunbook/  \
    && mkdir templates \
    && cd templates/ \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/index.html > index.html  \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/listDir.html > listDir.html  \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/viewResultFile.html > viewResultFile.html \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/viewYamlFile.html > viewYamlFile.html \
    && cd .. \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/docker/aioServerConfig.yml > aioServerConfig.yml \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/docker/runMyServer.py > runMyServer.py \
    && mkdir testDir1 \
    && mkdir testDir2 \
    && mkdir testDir3 \
    && cd testDir1/ \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/tests/testDir1/test11.yml > test11.yml \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/tests/testDir1/test12.yml > test12.yml \
    && mkdir -p /root/.ssh \
    && cd /root/.ssh \
    && ssh-keygen -f ca_key -t rsa -N '' \
    && ssh-keygen -f id_rsa -t rsa -N '' \
    && ssh-keygen -s ca_key -I user -n user id_rsa \
    && cd /
WORKDIR "/runbooks"
CMD ["python3", "/aioRunbook/runMyServer.py" ]

