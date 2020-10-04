# Streaming Zeek Events with Apache Kafka and ksqlDB

This workshop is a customization based on the Quick Start for Apache Kafka Using Confluent Platform (Docker) documentation available here: https://docs.confluent.io/current/quickstart/ce-docker-quickstart.html

This repository is for creating a classroom environment for a ksqlDB workshop.
The python scripts use boto3 to talk to the AWS API for automating provisioning, and the shell scripts manage the hosts once they're running.

Admittedly, this is pretty stone-age.  There are probably easier ways to do this, but I didn't have time to learn Ansible when I wrote this.

### Recommended Reading

This workshop leverages an additional Docker image: [bertisondocker/zeek-tcpreplay-kafka](https://github.com/berthayes/zeek-tcpreplay-kafka) for generating [Zeek](https://zeek.org) data to stream to Apache Kafka in real time.

You might want the ksqlDB syntax reference to be handy:
https://docs.ksqldb.io/en/latest/developer-guide/syntax-reference/


### Set Up Demo Environment

Check the instructions.txt for how to create the classroom environment.

The [zeek-tcp-replay](https://github.com/berthayes/zeek-tcpreplay-kafka) Docker image includes a pcap file for streaming and analysis.  

The pcap we're using in this workshop is available here:
https://drive.google.com/open?id=1wMCm_ByWlkI4Zym_Stim-xUK4Zb4Zm5Q

It's around 1GB in size and was originally captured over an hour or so.  The local network is 192.168.1.0/24 and there are maybe a dozen or so hosts that are active.  Some hosts are more active than others, and some hosts’ activities are more interesting than others.


One of the running Docker images is responsible for reading the alternate pcap and sending events from Zeek to Apache Kafka.  This image starts sending data automatically at start time, and the Apache Kafka broker is configured to create topics automatically when it receives them.  As soon as the environment is up and running, events are streaming into Kafka.

### Start Processing Data with Apache Kafka & ksqlDB



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
SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG = true EMIT CHANGES LIMIT 10;
```
The Zeek conn logs will keep track of whether a connection originated from the local network, or whether it came in from the outside.  Very handy!  Run the same search, but look for connections that originate from outside the local network:

```
SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true EMIT CHANGES;
```
You can sit and watch this query for a while, but there are very few (if any?) connections that originate from outside the network.  When I run this search, I get some ipv6 stuff, which mostly reflects that my ```local_nets``` value is ipv4 only.

Here’s a query that will look for any connections that did not originate locally, and that are destined for the local_net 192.168.1.0/24:

```
SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true AND "id.resp_h" LIKE '192.168.1%' EMIT CHANGES;
```

You can sit and watch this query for a REALLY long time and not see much happen.  Here’s where we can take advantage of the ability to replay a stream from the beginning of a topic.  Set auto.offset.reset to earliest as shown below.

```
SET 'auto.offset.reset'='earliest';
```

This will start reading events at the earliest offset instead of the latest.  Now re-run the above search to find incoming connections starting from the first recorded event.

If I’m a SOC Analyst, I might want to separate this kind of data to give it further analysis.  This is easy enough to do once the data is in a SIEM, but with this kind of high-level query, why put it in the SIEM in the first place?

Create a new topic that only has connection data for inbound connections to the local_net 192.168.1.0/24:

```
CREATE STREAM INBOUND_STREAM WITH (VALUE_FORMAT='AVRO') AS SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true AND "id.resp_h" LIKE '192.168.1%';
```
Note how this created a new topic called INBOUND_STREAM.  Also note that the value format is now AVRO instead of JSON.

```
SHOW TOPICS;
```

```
SELECT * FROM INBOUND_STREAM EMIT CHANGES;
```

### Creating a Stream with DNS Data

Take a look at the ksqldb_scripts/ directory in the GitHub repository and review the create_bro_dns_stream.sql file.  ksqlDB supports the ability to run .sql files as scripts, so instead of copy/pasting try this:

Run the ksql-cli be running:
```
$  docker exec -it ksqldb-cli ksql http://ksqldb-server:8088
                  
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

CLI v5.5.1, Server v5.5.1 located at http://ksqldb-server:8088

Having trouble? Type 'help' (case-insensitive) for a rundown of how things work!

ksql>
```


```
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
SELECT "query", COUNT("query") AS LOOKUPS FROM DNS_STREAM GROUP BY "query" EMIT CHANGES;
```
Take a look at an example of a DNS event as it is recorded by the Zeek connection logger:
```
SELECT * FROM CONN_STREAM WHERE "id.resp_p"=53 AND PROTO='udp' EMIT CHANGES LIMIT 1;
```
Now take a look at an example of a DNS event as it’s recorded by the Zeek DNS logger:
```
SELECT * FROM DNS_STREAM WHERE "id.resp_p"=53 AND PROTO='udp' EMIT CHANGES LIMIT 1;
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
Copy and paste this into the ksqlDB editor in Control Center

Make sure that auto.offset.reset is set to Latest.

Take a look at the documentation on how ksqlDB handles tumbling windows and time processing:
https://docs.ksqldb.io/en/latest/concepts/time-and-windows-in-ksqldb-queries/

This query will count the number of hostnames queried (e.g. the “www” in www.example.org) by a specific IP address.  The query uses a Tumbling window of 5 minutes to keep a running tally:

```
SELECT SRC_IP, HOSTNAME, COUNT(HOSTNAME) AS COUNT_HOSTNAME \
FROM RICH_DNS WINDOW TUMBLING (SIZE 5 MINUTES) \
GROUP BY SRC_IP, HOSTNAME EMIT CHANGES;
```

### Looking at SSL Data

Run the following scripts to create the SSL_STREAM and X509_STREAM:

```
RUN SCRIPT /ksqldb_scripts/create_bro_ssl_stream.sql;

 Message        
----------------
 Stream created 
----------------

RUN SCRIPT /ksqldb_scripts/create_bro_x509_stream.sql;

 Message        
----------------
 Stream created 
----------------
```
Take a look at a single SSL event:
```
SELECT * FROM SSL_STREAM EMIT CHANGES LIMIT 1;
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



