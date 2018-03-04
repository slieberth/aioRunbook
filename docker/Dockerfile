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
    && pip3 install git+https://github.com/slieberth/aioRunbook.git \
    && mkdir aioRunbook  \
    && cd aioRunbook/  \
    && mkdir templates \
    && cd templates/ \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/index.html > index.html  \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/listDir.html > listDir.html  \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/viewResultFile.html > viewResultFile.html  \
    && curl https://raw.githubusercontent.com/slieberth/aioRunbook/master/aioRunbook/templates/viewYamlFile.html > viewYamlFile.html 

CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]

