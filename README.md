# Streaming Zeek Events with Apache Kafka and ksqlDB

This is a customization of the cp-all-in-one-community demo available here: https://github.com/confluentinc/cp-all-in-one/

This version includes an additional image: [bertisondocker/zeek-tcpreplay-kafka](https://github.com/berthayes/zeek-tcpreplay-kafka) for generating [Zeek](https://zeek.org) data to stream to Apache Kafka in real time.

This version now includes ALL of pieces of Confluent Community, including ksqlDB.

## How Do I Work This?

* ```git clone https://github.com/berthayes/cp-all-in-one-community-with-zeek.git```
* ```cd cp-all-in-one-community-with-zeek```
* ```docker-compose -f docker-compose.yml -f cp-all-in-one/cp-all-in-one-community/docker-compose.yml up -d```

You are now automatically streaming events into Apache Kafka from the packet capture you had in ```pcaps/zeek_streamer.pcap```

Check to make sure:

```
$ docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
                  
                  ===========================================
                  =       _              _ ____  ____       =
                  =      | | _____  __ _| |  _ \| __ )      =
                  =      | |/ / __|/ _` | | | | |  _ \      =
                  =      |   <\__ \ (_| | | |_| | |_) |     =
                  =      |_|\_\___/\__, |_|____/|____/      =
                  =                   |_|                   =
                  =  Event Streaming Database purpose-built =
                  =        for stream processing apps       =
                  ===========================================

Copyright 2017-2020 Confluent Inc.

CLI v5.5.0, Server v5.5.0 located at http://ksqldb-server:8088

Having trouble? Type 'help' (case-insensitive) for a rundown of how things work!

ksql> LIST TOPICS;

 Kafka Topic    | Partitions | Partition Replicas 
--------------------------------------------------
 RICH_DNS       | 1          | 1                  
 conn           | 1          | 1                  
 dhcp           | 1          | 1                  
 dns            | 1          | 1                  
 files          | 1          | 1                  
 http           | 1          | 1                  
 known_services | 1          | 1                  
 software       | 1          | 1                  
 ssl            | 1          | 1                  
 weird          | 1          | 1                  
 x509           | 1          | 1                  
--------------------------------------------------
ksql> 
```
