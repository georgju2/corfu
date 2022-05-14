FROM ubuntu:20.10
# should be 21.04 but read: https://bugs.launchpad.net/ubuntu/+source/glibc/+bug/1916485

ENV DEBIAN_FRONTEND=noninteractive

# Ubuntu 20.04/10 + Raspbian libseccomp issue -> see 'workaround' folder instead of the attempts below
#RUN sed -i -e "s/deb /deb [trusted=yes] /g" /etc/apt/sources.list
#RUN sed -i -e "s/restricted//g" /etc/apt/sources.list
#RUN apt-get -o Acquire::Max-FutureTime=1999999999 update

# resolve necessary packages prior to python3.7 install
RUN apt-get update && \
    apt-get upgrade
RUN apt-get install -y wget build-essential checkinstall
RUN apt-get install -y libncursesw5-dev libssl-dev \
    libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

# install python package manager
# this will also install the latest python
RUN apt-get install -y python3-pip

# download and extract python3.7
WORKDIR /setup
RUN wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz && \
    tar xzf Python-3.7.6.tgz

# compile and install python 3.7
WORKDIR /setup/Python-3.7.6/
RUN ./configure --enable-optimizations --prefix=/usr
RUN make altinstall

# update python3 version
RUN ln -sf /usr/bin/python3.7 /usr/bin/python3

# copy and install requirements 
WORKDIR /app
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip install -r requirements.txt

# setup demo
#COPY src/ src/

#ENTRYPOINT ["python3", "src/demo.py"]
