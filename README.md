# Streaming Zeek Events with Apache Kafka and ksqlDB

This is a customization of the cp-all-in-one-community example available here: https://github.com/confluentinc/cp-all-in-one/



### Recommended Reading

This guide is partly based on the Confluent Quick Start Guide for Confluent Platform:
https://docs.confluent.io/current/quickstart/cos-docker-quickstart.html#cos-docker-quickstart

This example includes an additional Docker image: [bertisondocker/zeek-tcpreplay-kafka](https://github.com/berthayes/zeek-tcpreplay-kafka) for generating [Zeek](https://zeek.org) data to stream to Apache Kafka in real time.

You might want the ksqlDB syntax reference to be handy:
https://docs.ksqldb.io/en/latest/developer-guide/syntax-reference/


### Set Up Demo Environment

The [zeek-tcp-replay](https://github.com/berthayes/zeek-tcpreplay-kafka) Docker image includes a pcap file for streaming and analysis.  This file is named zeek-streamer.pcap  An additional, optional pcap file is available here:  https://drive.google.com/open?id=1wMCm_ByWlkI4Zym_Stim-xUK4Zb4Zm5Q

This pcap is 1GB in size and was originally captured over an hour or so.  The local network is 192.168.1.0/24 and there are maybe a dozen or so hosts that are active.  Some hosts are more active than others, and some hosts’ activities are more interesting than others.

To get started, open a terminal window and clone the git repository as shown below.  Backup the default pcap file and replace it with the garage_net.pcap you downloaded from Google Drive.

```
$ git clone --recurse-submodules https://github.com/berthayes/cp-all-in-one-community-with-zeek.git
$ cd cp-all-in-one-community-with-zeek
$ mv pcaps/zeek_streamer.pcap pcaps/repo.pcap
```
Move the file garage_net.pcap to the pcaps directory in the cloned repository:

```
$ mv ~/Downloads/garage_net.pcap pcaps/zeek_streamer.pcap
```

Start up the Docker images:

```
$ docker-compose -f docker-compose.yml \
-f cp-all-in-one/cp-all-in-one-community/docker-compose.yml \
-f docker-compose-override.yml up -d
```

It might take a couple of minutes for files to download and images to start up.

```
$ docker ps
```

You should have nine different images running:
```
confluentinc/cp-ksqldb-cli:5.5.0
confluentinc/ksqldb-examples:5.5.0
confluentinc/cp-ksqldb-server:5.5.0
cnfldemos/kafka-connect-datagen:0.3.2-5.5.0
confluentinc/cp-kafka-rest:5.5.0
bertisondocker/zeek-tcpreplay-kafka:latest
confluentinc/cp-schema-registry:5.5.0
confluentinc/cp-kafka:5.5.0
confluentinc/cp-zookeeper:5.5.0
```

One of the running Docker images is responsible for reading the pcap file you downloaded earlier, and sending events from Zeek to Apache Kafka.  This image starts sending data automatically at start time, and the Apache Kafka broker is configured to create topics automatically when it receives them.  As soon as the environment is up and running, events are streaming into Kafka.

### Start Processing Data with Apache Kafka & ksqlDB

Make sure you’re still in the cp-all-in-one-community-with-zeek directory and run the kafka-console-consumer to watch a topic (prove that data is flowing).  Pipe the output through jq to keep it pretty:

```
$ docker exec broker /usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic files | jq
```

Try the command above with dns instead of files.

```
$ docker exec broker /usr/bin/kafka-console-consumer --bootstrap-server localhost:9092 --topic dns | jq
```

In this case, topics are automatically created with the same name Zeek would give to their respective log files (e.g. dns, conn, http, ssl, x509, etc.)

### Run the ksqlDB CLI:

```
$ cd cp-all-in-one-community-with-zeek
$ docker exec -it ksqldb-cli ksql http://ksqldb-server:8088

ksql> SHOW TOPICS;

 Kafka Topic    | Partitions | Partition Replicas 
--------------------------------------------------
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

ksqlDB has the ```PRINT``` command, which will print events from topics similar to the console-consumer above:

```
ksql> PRINT 'files' LIMIT 1;
```

Although we have topics, we haven’t created any streams or tables from them:

```
ksql> LIST STREAMS;

 Stream Name | Kafka Topic | Format 
------------------------------------
------------------------------------
ksql> 
```

### Creating a Stream with Conn Data

A Zeek “conn” event looks like this:
```json
{
  "ts": 1589364400.639986,
  "uid": "CiNixT1Cjx3iztNbE2",
  "id.orig_h": "192.168.1.9",
  "id.orig_p": 53768,
  "id.resp_h": "192.168.1.1",
  "id.resp_p": 53,
  "proto": "tcp",
  "duration": 0.0005700588226318359,
  "orig_bytes": 0,
  "resp_bytes": 0,
  "conn_state": "RSTO",
  "local_orig": true,
  "local_resp": true,
  "missed_bytes": 0,
  "history": "ShR",
  "orig_pkts": 2,
  "orig_ip_bytes": 84,
  "resp_pkts": 1,
  "resp_ip_bytes": 44
}
```

The following command will create a stream called “conn_stream” based on the connection log data from Zeek.  ksqlDB can’t automatically identify the format of the data, so we specify ```VALUE_FORMAT=’JSON’``` when we create this stream.  Also notice that some of the fields have a dot or period in them, so they get wrapped in quotes (e.g. ```“id.orig_h”```).  Quotes are also required when we create a field named ```“query”``` when creating a stream of DNS data.

```SQL
CREATE STREAM conn_stream (
ts DOUBLE(16,6), 
uid STRING, 
"id.orig_h" VARCHAR, 
"id.orig_p" INTEGER, 
"id.resp_h" VARCHAR, 
"id.resp_p" INTEGER, 
proto STRING, 
service STRING, 
conn_state STRING, 
local_orig BOOLEAN, 
local_resp BOOLEAN, 
missed_bytes INTEGER, 
history STRING, 
orig_packets INTEGER, 
orig_ip_bytes INTEGER, 
resp_pkts INTEGER, 
resp_ip_bytes INTEGER) 
WITH (KAFKA_TOPIC='conn', VALUE_FORMAT='JSON');
```
Now that you’ve created this stream, you can query it with ksqlDB.

```
ksql> SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG = true EMIT CHANGES LIMIT 10;
```
The Zeek conn logs will keep track of whether a connection originated from the local network, or whether it came in from the outside.  Very handy!  Run the same search, but look for connections that originate from outside the local network:

```
ksql> SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true EMIT CHANGES;
```
You can sit and watch this query for a while, but there are very few (if any?) connections that originate from outside the network.  When I run this search, I get some ipv6 stuff, which mostly reflects that my ```local_nets``` value is ipv4 only.

Here’s a query that will look for any connections that did not originate locally, and that are destined for the local_net 192.168.1.0/24:

```
ksql> SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true AND "id.resp_h" LIKE '192.168.1%' EMIT CHANGES;
```

You can sit and watch this query for a REALLY long time and not see much happen.  Here’s where we can take advantage of the ability to replay a stream from the beginning of a topic.  Set auto.offset.reset to earliest as shown below.

```
ksql> SET 'auto.offset.reset'='earliest';
```

This will start reading events at the earliest offset instead of the latest.  Now re-run the above search to find incoming connections starting from the first recorded event.

If I’m a SOC Analyst, I might want to separate this kind of data to give it further analysis.  This is easy enough to do once the data is in a SIEM, but with this kind of high-level query, why put it in the SIEM in the first place?

Create a new topic that only has connection data for inbound connections to the local_net 192.168.1.0/24:

```
ksql> CREATE STREAM INBOUND_STREAM WITH (VALUE_FORMAT='AVRO') AS \
>SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true AND "id.resp_h" LIKE '192.168.1%';
```
Note how this created a new topic called INBOUND_STREAM.  Also note that the value format is now AVRO instead of JSON.

```
ksql> SHOW TOPICS;

 Kafka Topic    | Partitions | Partition Replicas 
--------------------------------------------------
 INBOUND_STREAM | 1          | 1                  
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

ksql> SELECT * FROM INBOUND_STREAM EMIT CHANGES;
```

### Creating a Stream with DNS Data

Take a look at the ksqldb_scripts/ directory in the GitHub repository and review the create_bro_dns_stream.sql file.  ksqlDB supports the ability to run .sql files as scripts, so instead of copy/pasting try this:

```
ksql> SHOW STREAMS;

 Stream Name    | Kafka Topic    | Format 
------------------------------------------
 CONN_STREAM    | conn           | JSON   
 INBOUND_STREAM | INBOUND_STREAM | AVRO   
------------------------------------------
ksql> RUN SCRIPT /ksqldb_scripts/create_bro_dns_stream.sql;

 Message        
----------------
 Stream created 
----------------
ksql> SHOW STREAMS;

 Stream Name    | Kafka Topic    | Format 
------------------------------------------
 CONN_STREAM    | conn           | JSON   
 DNS_STREAM     | dns            | JSON   
 INBOUND_STREAM | INBOUND_STREAM | AVRO   
------------------------------------------
```
Congratulations!  You now have Zeek conn data AND Zeek DNS data as streams to analyze in ksqlDB.

```
ksql> SELECT "query", COUNT("query") AS LOOKUPS FROM DNS_STREAM GROUP BY "query" EMIT CHANGES;
```
Take a look at an example of a DNS event as it is recorded by the Zeek connection logger:
```
ksql> SELECT * FROM CONN_STREAM WHERE "id.resp_p"=53 AND PROTO='udp' EMIT CHANGES LIMIT 1;
```
Now take a look at an example of a DNS event as it’s recorded by the Zeek DNS logger:
```
ksql> SELECT * FROM DNS_STREAM WHERE "id.resp_p"=53 AND PROTO='udp' EMIT CHANGES LIMIT 1;
```
Notice how the CONN_STREAM event has byte counts associated with the traffic, but not the DNS query or reply information?  And how the DNS_STREAM event has the DNS information, but not byte counts?

### Creating an Enriched Stream

Both sets of data are available when pieces of these streams are combined to create a new stream.  Take a look at the create_rich_dns_stream.sql file:

```sql
CREATE STREAM RICH_DNS WITH (PARTITIONS=1, VALUE_FORMAT='AVRO') AS 
SELECT d."query", 
    d."id.orig_h" AS SRC_IP, 
    d."id.resp_h" AS DEST_IP,
    d."id.orig_p" AS SRC_PORT, 
    d."id.resp_h" AS DEST_PORT, 
    d.QTYPE_NAME, 
    d.TTLS, 
    SPLIT(d."query", '.')[1] AS HOSTNAME, 
    SPLIT(d."query", '.')[2] AS ELEMENT2, 
    SPLIT(d."query", '.')[3] AS ELEMENT3, 
    SPLIT(d."query", '.')[4] AS ELEMENT4, 
    d.ANSWERS, 
    d.TS, 
    d.UID, 
    c.UID, 
    c.ORIG_IP_BYTES AS REQUEST_BYTES, 
    c.RESP_IP_BYTES AS REPLY_BYTES, 
    c.LOCAL_ORIG 
FROM DNS_STREAM d INNER JOIN CONN_STREAM c WITHIN 1 MINUTES ON d.UID = c.UID WHERE LOCAL_ORIG = true;
```
You can run this by copying and pasting it at the ksql> prompt, or by running it as a script from the ksql> prompt:
```
ksql> RUN SCRIPT /ksqldb_scripts/create_rich_dns_stream.sql;
```
If your auto.offset.reset value is still set to earliest, now is a good time to set it to latest:
```
ksql> SET 'auto.offset.reset'='latest';
```
Take a look at the documentation on how ksqlDB handles tumbling windows and time processing:
https://docs.ksqldb.io/en/latest/concepts/time-and-windows-in-ksqldb-queries/

This query will count the number of hostnames queried (e.g. the “www” in www.example.org) by a specific IP address.  The query uses a Tumbling window of 5 minutes to keep a running tally:

```
ksql> SELECT SRC_IP, HOSTNAME, COUNT(HOSTNAME) AS COUNT_HOSTNAME \
FROM RICH_DNS WINDOW TUMBLING (SIZE 5 MINUTES) \
GROUP BY SRC_IP, HOSTNAME EMIT CHANGES;
```

### Looking at SSL Data

Run the following scripts to create the SSL_STREAM and X509_STREAM:

```
ksql> RUN SCRIPT /ksqldb_scripts/create_bro_ssl_stream.sql;

 Message        
----------------
 Stream created 
----------------

ksql> RUN SCRIPT /ksqldb_scripts/create_bro_x509_stream.sql;

 Message        
----------------
 Stream created 
----------------
```
Take a look at a single SSL event:
```
ksql> SELECT * FROM SSL_STREAM EMIT CHANGES LIMIT 1;
```
Notice how the SSL event has IP and port information, as well as information about the Subject and Issuer of the certificate that was used.  We even get a field called ```VALIDATION_STATUS``` that helpfully indicates that a certificate has expired.  Missing, however, is more detailed information about the certificate itself.

Looking at the X509 event, we see more detailed information about the certificate itself, including the creation and expiration dates in epoch form.

The following ksqlDB query can combine the best of both worlds; it will also use the ```TIMESTAMPTOSTRING``` function to create fields with human readable timestamps:

```sql
SELECT 
s.TS AS SSL_TS, 
s."id.orig_h" AS SRC_IP, 
s."id.orig_p" AS SRC_PORT, 
s."id.resp_h" AS DEST_IP, 
s."id.resp_p" AS DEST_PORT, 
s.VERSION AS VERSION, 
s.CIPHER AS CIPHER, 
s.CURVE AS CURVE, 
s.SERVER_NAME AS SERVER_NAME, 
s.SUBJECT AS SUBJECT, 
s.ISSUER AS ISSUER, 
s.VALIDATION_STATUS AS VALIDATION_STATUS, 
x.TS AS X509_TS, 
x."certificate.version" AS CERTIFICATE_VERSION, 
x."certificate.not_valid_before" AS CERTIFICATE_NOT_VALID_BEFORE, 
x."certificate.not_valid_after" AS CERTIFICATE_NOT_VALID_AFTER, 
TIMESTAMPTOSTRING((x."certificate.not_valid_after" * 1000), 'yyyy-MM-dd HH:mm:ss') AS CERT_EXPIRATION_DATE, 
TIMESTAMPTOSTRING((x."certificate.not_valid_before" * 1000), 'yyyy-MM-dd HH:mm:ss') AS CERT_REGISTRATION_DATE, 
x."certificate.key_alg" AS CERTIFICATE_KEY_ALG, 
x."certificate.sig_alg" AS CERTIFICATE_SIG_ALG, 
x."certificate.key_type" AS CERTIFICATE_KEY_TYPE, 
x."certificate.key_length" AS CERTIFICATE_KEY_LENGTH 
FROM SSL_STREAM s INNER JOIN X509_STREAM x WITHIN 1 SECONDS 
on s.SUBJECT = x."certificate.subject" 
WHERE s.VALIDATION_STATUS!='ok' EMIT CHANGES;
```

Here’s the same query as above, but modified to find certificates that are less than 30 days old.  It takes these results and creates a new stream from them.  This action automatically creates a new topic.  This topic now has enriched data that’s been filtered for an infosec use case BEFORE it’s ever touched the SIEM.

```sql
CREATE STREAM NEW_SSL_STREAM AS
SELECT 
s.TS AS SSL_TS, 
s."id.orig_h" AS SRC_IP, 
s."id.orig_p" AS SRC_PORT, 
s."id.resp_h" AS DEST_IP, 
s."id.resp_p" AS DEST_PORT, 
s.VERSION AS VERSION, 
s.CIPHER AS CIPHER, 
s.CURVE AS CURVE, 
s.SERVER_NAME AS SERVER_NAME, 
s.SUBJECT AS SUBJECT, 
s.ISSUER AS ISSUER, 
s.VALIDATION_STATUS AS VALIDATION_STATUS, 
x.TS AS X509_TS, 
x."certificate.version" AS CERTIFICATE_VERSION, 
x."certificate.not_valid_before" AS CERTIFICATE_NOT_VALID_BEFORE, 
x."certificate.not_valid_after" AS CERTIFICATE_NOT_VALID_AFTER, 
TIMESTAMPTOSTRING((x."certificate.not_valid_after" * 1000), 'yyyy-MM-dd HH:mm:ss') AS CERT_EXPIRATION_DATE, 
TIMESTAMPTOSTRING((x."certificate.not_valid_before" * 1000), 'yyyy-MM-dd HH:mm:ss') AS CERT_REGISTRATION_DATE, 
x."certificate.key_alg" AS CERTIFICATE_KEY_ALG, 
x."certificate.sig_alg" AS CERTIFICATE_SIG_ALG, 
x."certificate.key_type" AS CERTIFICATE_KEY_TYPE, 
x."certificate.key_length" AS CERTIFICATE_KEY_LENGTH 
FROM SSL_STREAM s INNER JOIN X509_STREAM x WITHIN 1 SECONDS 
on s.SUBJECT = x."certificate.subject" 
WHERE (UNIX_TIMESTAMP() - (x."certificate.not_valid_before") * 1000) < 2592000000 EMIT CHANGES;
```

### Tips and Tricks
To start off a fresh pcap streaming to Zeek->Confluent:
Note the --loop option which will replay this pcap a skillion times.

```
$ cd cp-all-in-one-community-with-zeek
$ ls pcaps/
garage_net.pcap  zeek_streamer.pcap
$ docker exec -d zeek-streamer /usr/bin/tcpreplay --loop=1000000000 -i dummy0 /pcaps/repo.pcap
```
Stop Confluent Docker containers:
```
$ docker container stop $(docker container ls -a -q -f "label=io.confluent.docker")
```

Stop Zeek streamer Docker container:
```
$ docker stop zeek-streamer
```
