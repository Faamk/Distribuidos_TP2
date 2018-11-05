FROM ubuntu

COPY Server/Server.py /home/Data/


ENV IP=localhost
ENV IPRANGE=localhost
ENV ID=1
ENV LOGFILE=log.txt

RUN apt-get update
RUN apt-get install -y python3

EXPOSE 15555/tcp
EXPOSE 15555/udp

CMD python3 /home/Data/Server.py $IP $IPRANGE $ID $LOGFILE
