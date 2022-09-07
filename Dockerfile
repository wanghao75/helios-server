FROM ubuntu:20.04
MAINTAINER wanghao wanghaosq@gmail.com
WORKDIR /app
COPY helios-server ./helios-server
RUN apt-get update \
    && apt-get install -y sudo \
    && sudo apt-get install -y software-properties-common \
    && sudo add-apt-repository ppa:deadsnakes/ppa -y \
    && sudo apt update \
    && sudo apt-get install -y rabbitmq-server \
	postgresql \
	python3.6 \
	python3.6-dev \
	python3.6-venv \
        python3-pip \
	libpq-dev \
        tcl \
        expect \
        python-celery-common \

ENV TIME_ZONE Asia/Shanghai
COPY helios-server/start_service.sh /usr/bin/start_service.sh
RUN chmod +x /usr/bin/start_service.sh 
EXPOSE 8000
CMD ["start_service.sh"]
