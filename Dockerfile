FROM ubuntu:latest

RUN apt-get update
RUN apt-get purge python
RUN apt-get autoremove -y
RUN apt-get install -y python2.7 python-pip python-dev

# =======================
# Install python-opencv #
# =======================

RUN apt-get install -y libcairo2-dev libjpeg8-dev libpango1.0-dev libgif-dev build-essential g++
RUN apt-get install -y libdc1394-22-dev libdc1394-22 libdc1394-utils
RUN apt-get install -y python-opencv 

# ==============
# Install Dlib #
# ==============
RUN apt-get install -y cmake libboost-python-dev git libopenblas-dev liblapack-dev
RUN git clone https://github.com/davisking/dlib.git /dlib/
WORKDIR /dlib/
RUN python setup.py install

# ==========================
# Install the requirements #
# ==========================

RUN apt-get install -y python-numpy python-scipy python-sklearn

WORKDIR /app/
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt 
RUN pip install flake8

ADD . /app/
RUN flake8 printermood

