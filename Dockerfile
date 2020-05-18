FROM ubuntu:latest
RUN apt-get update && apt-get -y update
RUN apt-get install -y build-essential python3.7 python3-pip python3-dev
RUN pip3 -q install pip --upgrade
RUN mkdir k-median-geo
WORKDIR k-median-geo/
COPY . .
ADD . /
RUN pip3 install -r requirements.txt
RUN python3 setup.py install

EXPOSE 3000

CMD [ "/bin/bash" ]
# docker run -it ubuntu /bin/bash