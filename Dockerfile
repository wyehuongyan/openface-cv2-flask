FROM gitlab.aporigin.com:5005/3danalec/opencv-dlib-torch:0.1.0
MAINTAINER Wye Huong Yan <wyehuong@aporigin.com>

ENV INSTALL_PATH /usr/src/openface

# Create app directory
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

RUN apt-get update && apt-get install -y \
    curl \
    git \
    graphicsmagick \
    python-dev \
    python-pip \
    python-numpy \
    python-nose \
    python-scipy \
    python-pandas \
    python-protobuf\
    wget \
    zip \
    libmysqlclient-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Bundle app source
COPY . .

RUN cd $INSTALL_PATH && \
    ./models/get-models.sh && \
    pip2 install -r requirements.txt && \
    python2 setup.py install && \
    pip2 install -r demos/web/requirements.txt && \
    pip2 install -r training/requirements.txt

RUN ln -s /root/torch/install/bin/th /usr/local/bin/th

# expose Flask port
EXPOSE 5000