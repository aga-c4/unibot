FROM python:3

ENV TZ 'Europe/Moscow'
ENV LOCSTR 'en_US.UTF-8 UTF-8'

RUN apt-get update && apt-get install --no-install-recommends --no-install-suggests -y \
        ca-certificates tzdata locales \
        curl mc \
    && echo $TZ > /etc/timezone \
    && rm /etc/localtime \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get autoremove \
    && echo $LOCSTR > /etc/locale.gen && locale-gen \
    && apt-get autoclean 

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./imon.py" ]
