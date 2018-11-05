FROM ubuntu

COPY Client.py /home/Data/


ENV IPRANGE=localhost

RUN apt-get update
RUN apt-get install -y python3

EXPOSE 15555/tcp
EXPOSE 15555/udp

CMD python3 /home/Data/Client.py $IPRANGE
