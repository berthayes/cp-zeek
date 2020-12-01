# Streaming Zeek Events with Apache Kafka and ksqlDB
[Custom Start](https://github.com/berthayes/cp-zeek/#Custom-Start)
## Quickstart
- [Running on localhost](https://github.com/berthayes/cp-zeek/#Running-on-localhost)

- [Running on an external host](https://github.com/berthayes/cp-zeek/#Running-on-an-external-host)

- [Starting the Connectors](https://github.com/berthayes/cp-zeek/#Starting-the-Connectors)

- [Running on a bunch of EC2 hosts in AWS](https://github.com/berthayes/cp-zeek/blob/master/Workshop_Instructions.md)

[ksqlDB Walkthrough](ksqldb_walkthrough.md) - A guided walk through using ksqlDB to analyze Zeek and Syslog data.


## Running on localhost
``` 
git clone https://github.com/berthayes/cp-zeek
cd cp-zeek
docker-compose up -d
```

Wait about 5 minutes or so for everything to start up, then point your web browser to http://localhost:9021

To start the Syslog and Spooldir connectors, see: [Starting the Connectors](https://github.com/berthayes/cp-zeek/#Starting-the-Connectors) 

## Running on an external host
To run this environment on a system that is not your laptop/workstation, edit the `docker-compose.yml` file.

Look for this line:
```
CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: "http://localhost:8088"
```
And change it to something like this:
```
CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: "http://yourhost.yourdomain.com:8088"
```
Then start up docker as above with:
```
docker-compose up -d
```
Wait about 5 minutes or so for everything to start up, then point your web browser to http://yourhost.yourdomain.com:9021

To start the Syslog and Spooldir connectors, see: [Starting the Connectors](https://github.com/berthayes/cp-zeek/#Starting-the-Connectors) 


## Starting the Connectors

If you also want to analyze streaming Syslog data, run:

```
curl localhost:8083/connectors -X POST -H "Content-Type: application/json" -d @syslog_connect.json
```

To start the Spooldir connector that consumes a sample URLHaus watchlist, run:
```
curl localhost:8083/connectors -X POST -H "Content-Type: application/json" -d @urlhaus_spooldir.json
```

To start the Spooldir connector that consumes a watchlist of ad servers, run:
```
curl localhost:8083/connectors -X POST -H "Content-Type: application/json" -d @adhosts_spooldir.json
```

## Custom Start

This repository is a customization based on the Quick Start for Apache Kafka Using Confluent Platform (Docker) documentation available here: https://docs.confluent.io/current/quickstart/ce-docker-quickstart.html It focuses on analyzing [Zeek](https://zeek.org) and Syslog events with [ksqlDB](https://ksqldb.io) running on the Confluent Platform for Apache Kafka.


### Customize Your Environment

This docker-compose.yml leverages an additional Docker image: [bertisondocker/zeek-tcpreplay-kafka](https://github.com/berthayes/zeek-tcpreplay-kafka) for generating [Zeek](https://zeek.org) data to stream to Apache Kafka in real time.  When the image runs, tcpreplay automatically starts reading `./pcaps/zeek-streamer.pcap`

To run this with the included packet capture simply run: 
`docker-compose up -d`

To analyze your own packet capture, Copy your pcap file to `./cp-zeek/pcaps/zeek-streamer.pcap` The zeek-streamer Docker image begins reading the zeek-streamer.pcap file automatically at startup.

A super-fun pcap for analysis is available here:
https://drive.google.com/open?id=1wMCm_ByWlkI4Zym_Stim-xUK4Zb4Zm5Q

It's around 1GB in size and was originally captured over an hour or so.  The local network is 192.168.1.0/24 and there are maybe a dozen or so hosts that are active.  Some hosts are more active than others, and some hosts’ activities are more interesting than others.

The Apache Kafka broker is configured to create topics automatically when it receives events.  As soon as the environment is up and running, events are streaming into Kafka with separate topics created for each flavor of Zeek logs.