# Processing Zeek & Syslog Data with Apache Kafka & ksqlDB

This document is a step-by-step walkthrough that guides the reader through processing Zeek IDS data and Syslog data using ksqlDB.

This table of contents is provided as a reference.  Please note that each section must be completed fully before the next section will work.

## Table of Contents
- [Creating a Stream with Conn Data](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#creating-a-stream-with-conn-data)
- [Creating a Stream with DNS Data](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#creating-a-stream-with-dns-data)
- [Creating an Enriched Stream - Joining Streams](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#creating-an-enriched-stream---joining-streams)
- [Creating an Enriched Stream - User Defined Lookups](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#creating-an-enriched-stream---user-defined-lookups)
- [Looking at SSL Data](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#looking-at-ssl-data)
- [Analyzing Syslog Events](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#analyzing-syslog-events)
- [Matching hostnames in a watchlist](https://github.com/berthayes/cp-zeek/blob/master/ksqldb_walkthrough.md#matching-hostnames-in-a-watchlist)

### Creating a Stream with Conn Data
#### Monitoring for inbound connections


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

The following command will create a stream called “conn_stream” based on the conn event data from Zeek.  ksqlDB can’t automatically identify the format of the data, so we specify ```VALUE_FORMAT=’JSON’``` when we create this stream.  Also notice that some of the fields have a dot or period in them, so they get wrapped in quotes (e.g. ```“id.orig_h”```).  Quotes are also required when we create a field named ```“query”``` when creating a stream of DNS data.

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
You can sit and watch this query for a while, but there are very few (if any?) connections that originate from outside the network.  When I run this search, I get some ipv6 stuff, which mostly reflects that my ```local_nets``` value in Zeek is ipv4 only.

Here’s a query that will look for any connections that did not originate locally, and that are destined for the local_net 192.168.1.0/24:

```
SELECT * FROM CONN_STREAM WHERE LOCAL_ORIG != true AND "id.resp_h" LIKE '192.168.1%' EMIT CHANGES;
```

You can sit and watch this query for a REALLY long time and not see much happen.  Here’s where we can take advantage of the ability to replay a stream from the beginning of a topic.  Set auto.offset.reset to earliest using the Web UI


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

Take a look at the ksqldb_scripts/ directory in the GitHub repository.  Copy the SQL code from `cp-zeek/ksqldb_scripts/create_bro_dns_stream.sql` into the ksqlDB editor and run the query.

If you are running this environment in Docker on your local workstation/laptop, you can run the ksql command line interface by running:

```
$ docker exec -it ksqldb-cli /usr/bin/ksql http://ksqldb-server:8088
```
```
OpenJDK 64-Bit Server VM warning: Option UseConcMarkSweepGC was deprecated in version 9.0 and will likely be removed in a future release.
                  
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

CLI v6.0.0, Server v6.0.0 located at http://ksqldb-server:8088

Having trouble? Type 'help' (case-insensitive) for a rundown of how things work!

ksql>
```
ksql commands can be saved and run as scripts from this command line:

```
ksql> RUN SCRIPT /ksqldb_scripts/create_bro_dns_stream.sql;

 Message        
----------------
 Stream created 
----------------
ksql> RUN SCRIPT /ksqldb_scripts/create_bro_ssl_stream.sql

 Message        
----------------
 Stream created 
----------------
ksql> RUN SCRIPT /ksqldb_scripts/create_bro_x509_stream.sql

 Message        
----------------
 Stream created 
----------------
ksql>
```

Congratulations!  You now have Zeek conn data AND Zeek DNS data as streams to analyze in ksqlDB.

```sql
SELECT "query", COUNT("query") AS LOOKUPS FROM DNS_STREAM GROUP BY "query" EMIT CHANGES;
```
Take a look at an example of a DNS event as it is recorded by the Zeek connection logger:
```sql
SELECT * FROM CONN_STREAM WHERE "id.resp_p"=53 AND PROTO='udp' EMIT CHANGES LIMIT 1;
```
Now take a look at an example of a DNS event as it’s recorded by the Zeek DNS logger:
```sql
SELECT * FROM DNS_STREAM WHERE "id.resp_p"=53 AND PROTO='udp' EMIT CHANGES LIMIT 1;
```
Notice how the CONN_STREAM event has byte counts associated with the traffic, but not the DNS query or reply information?  And how the DNS_STREAM event has the DNS information, but not byte counts?

### Creating an Enriched Stream - Joining Streams

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

```sql
SELECT SRC_IP, HOSTNAME, COUNT(HOSTNAME) AS COUNT_HOSTNAME 
FROM RICH_DNS WINDOW TUMBLING (SIZE 5 MINUTES) 
GROUP BY SRC_IP, HOSTNAME EMIT CHANGES;
```

### Creating an Enriched Stream - User Defined Lookups

This repository leverages two User Defined Lookups (UDF) in ksqlDB.  The source code for these UDFs is here: https://github.com/berthayes/ksql-udf-asn and here: https://github.com/alexwoolford/ksql-udf-geoip

These UDFs leverage the MaxMind Java API to return Geolocation data and Autonomous System Number (ASN) information for an IP address.

```sql
SELECT "id.resp_h" AS DEST_IP, 
"id.orig_h" AS SRC_IP, 
getgeoforip("id.resp_h") AS DEST_GEO, 
getasnforip("id.resp_h") AS DEST_ASN
FROM CONN_STREAM WHERE "id.resp_p" = 443 AND "id.resp_h" NOT LIKE '192.168.1.%'
EMIT CHANGES;
```

```json
{
  "DEST_IP": "34.253.248.189",
  "SRC_IP": "192.168.1.9",
  "DEST_GEO": {
    "CITY": "Dublin",
    "COUNTRY": "Ireland",
    "SUBDIVISION": "Leinster",
    "LOCATION": {
      "LON": -6.2488,
      "LAT": 53.3338
    }
  },
  "DEST_ASN": {
    "ASN": 16509,
    "ORG": "AMAZON-02"
  }
}
```
It's often helpful to enrich IP information with this meta data at the data fabric layer rather than the end point layer (e.g. SIEM)



### Looking at SSL Data

Create streams for SSL data and X509 data by copy/pasting the `cp-zeek/ksqldb_scripts/create_bro_ssl_stream.sql` and `cp-zeek/ksqldb_scripts/create_bro_x509_stream.sql` into the ksqlDB editor in Confluent Control Center.

Alternatively, use the ksql CLI to run the `create_bro_x509_stream.sql` script as shown above.

Take a look at a single SSL event:
```sql
SELECT * FROM SSL_STREAM EMIT CHANGES LIMIT 1;
```
Notice how the SSL event has IP and port information, as well as information about the Subject and Issuer of the certificate that was used.  We even get a field called ```VALIDATION_STATUS``` that helpfully indicates that a certificate has expired.  Missing, however, is more detailed information about the certificate itself.

Looking at the X509 event, we see more detailed information about the certificate itself, including the creation and expiration dates in epoch form.

```sql
SELECT * FROM X509_STREAM EMIT CHANGES LIMIT 1;
```

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
EMIT CHANGES;
```

Here’s the same query as above, but modified to find certificates that are less than 30 days old. It also uses the UDF `getgeoforip()` and `getasnforip()`  It takes these results and creates a new stream from them.  This action automatically creates a new topic.  This topic now has enriched data that’s been filtered for an infosec use case BEFORE it’s ever touched the SIEM.

```sql
CREATE STREAM NEW_SSL_STREAM AS
SELECT 
s.TS AS SSL_TS, 
s."id.orig_h" AS SRC_IP, 
s."id.orig_p" AS SRC_PORT, 
s."id.resp_h" AS DEST_IP, 
s."id.resp_p" AS DEST_PORT, 
getgeoforip(s."id.resp_h") AS DEST_GEOIP,
getasnforip(s."id.resp_h") AS DEST_ASN,
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

## Analyzing Syslog Events

The running connect image has the [Confluent syslog connector](https://www.confluent.io/hub/confluentinc/kafka-connect-syslog) installed.  A connect worker can be configured by running:

```docker exec -it connect /tmp/start_syslog_connector.sh```

Alternatively, you can configure a connect worker through the Confluent Control Center GUI.

### Create a stream from syslog data
ksqlDB can't analyze raw records in a topic, it analyzes this data when its materialized as a stream.

Create a stream from the syslog data with the following ksqlDB query:

```sql
CREATE STREAM SYSLOG_STREAM WITH (KAFKA_TOPIC='syslog', VALUE_FORMAT='AVRO');
```

The `tag` field in the syslog data represents the process that generated the log, e.g. `cron`, `sshd`, etc.

This ksql query uses `REGEXP_EXTRACT` to extract the usernames and remote ip addresses that failed SSH logins:

```sql
SELECT TIMESTAMP, 
TAG, MESSAGE, HOST, REMOTEADDRESS AS DEST_IP,
TIMESTAMPTOSTRING(TIMESTAMP, 'yyyy-MM-dd HH:mm:ss') AS EVENT_TIME, 
REGEXP_EXTRACT('Invalid user (.*) from', MESSAGE, 1) AS USER,
REGEXP_EXTRACT('Invalid user .* from (.*) port', MESSAGE, 1) AS SRC_IP
FROM  SYSLOG_STREAM WHERE TAG='sshd' AND MESSAGE LIKE 'Invalid user%' 
EMIT CHANGES;
```
This results in a record that looks like this:

```json
{
  "TIMESTAMP": 1603040775000,
  "TAG": "sshd",
  "MESSAGE": "Invalid user ralphie from 192.168.1.183 port 56350",
  "HOST": "deb9-LAN",
  "DEST_IP": "172.18.1.9",
  "EVENT_TIME": "2020-10-18 17:06:15",
  "USER": "ralphie",
  "SRC_IP": "192.168.1.183"
}
```
The groomed data you get as a result of this queryi is ideal for downstream consumption.

This ksql query looks for more than 10 failed SSH logins in 5 seconds on a host:

```sql
SELECT WINDOWSTART AS starttime, 
WINDOWEND AS endtime, 
HOST, 
TAG, 
MESSAGE, 
COUNT(*) AS COUNT_OF_INVALID_SSH 
FROM SYSLOG_STREAM WINDOW TUMBLING (SIZE 5 SECONDS) 
WHERE TAG='sshd' AND MESSAGE LIKE 'Connection closed by invalid user%' 
GROUP BY HOST, TAG, MESSAGE
HAVING COUNT(*) > 10
EMIT CHANGES;
```
Season to taste, then create a table for this select query.  This table will create a new topic which can be fed downstream to a real-time alerting platform or a SIEM.

```sql
CREATE TABLE BRUTE_FORCE_SSH_TABLE WITH (KAFKA_TOPIC='bruteforce', VALUE_FORMAT='AVRO') AS
SELECT WINDOWSTART AS starttime, 
WINDOWEND AS endtime, 
HOST, 
TAG, 
MESSAGE, 
COUNT(*) AS COUNT_OF_INVALID_SSH 
FROM SYSLOG_STREAM WINDOW TUMBLING (SIZE 5 SECONDS) 
WHERE TAG='sshd' AND MESSAGE LIKE 'Connection closed by invalid user%' 
GROUP BY HOST, TAG, MESSAGE
HAVING COUNT(*) > 10
EMIT CHANGES;
```

## Matching hostnames in a watchlist

A sample csv file of known Ad servers is in the `ad_hosts.csv` file included in this repository.

```
./cp-zeek/spooldir/ad_hosts/csv_input/ad_hosts.csv
```
It looks like this:
```
id,dateadded,domain,source
1,1602886038,fr.a2dfp.net,https://winhelp2002.mvps.org/hosts.txt
2,1602886038,mfr.a2dfp.net,https://winhelp2002.mvps.org/hosts.txt
3,1602886038,ad.a8.net,https://winhelp2002.mvps.org/hosts.txt
4,1602886038,asy.a8ww.net,https://winhelp2002.mvps.org/hosts.txt
5,1602886038,static.a-ads.com,https://winhelp2002.mvps.org/hosts.txt
6,1602886038,abcstats.com,https://winhelp2002.mvps.org/hosts.txt
7,1602886038,track.acclaimnetwork.com,https://winhelp2002.mvps.org/hosts.txt
8,1602886038,csh.actiondesk.com,https://winhelp2002.mvps.org/hosts.txt
9,1602886038,ads.activepower.net,https://winhelp2002.mvps.org/hosts.txt
```
To ingest this CSV file into a ne topic and automatically create a schema for that topic, start a new Spooldir connector to watch for this source:
```
./start_adhosts_spooldir.sh
```
Once this is started, or if it had already been started, the `ad_hosts.csv` file moves to:
```
./cp-zeek/spooldir/ad_hosts/csv_finished/ad_servers.csv
```
If you look under Topics, you should now see an topic called ad_hosts.

Create a stream from this topic so that ksqlDB can process it:
```sql
CREATE STREAM ADHOSTS_STREAM WITH (KAFKA_TOPIC='adhosts', VALUE_FORMAT='AVRO');
```

Because joining a stream to a stream requires a time window, and we want to consider our list of bad hostnames as more of a static snapshot, we will create a table from this stream:

```sql
CREATE TABLE adverts (id STRING, dateadded STRING, domain VARCHAR PRIMARY KEY, source VARCHAR)
WITH (KAFKA_TOPIC='adhosts', VALUE_FORMAT='AVRO');;
```

So now we have a table against which we can match streaming events.

So let's take the HTTP_STREAM and re-key it by host so it can be joined with this table:

```sql
CREATE STREAM KEYED_HTTP WITH (KAFKA_TOPIC='keyed_http')
AS SELECT * FROM  HTTP_STREAM
PARTITION BY HOST
EMIT CHANGES;
```

Now create a NEW stream that joins the `KEYED_HTTP` with the `ADVERTS` table:

```sql
CREATE STREAM MATCHED_HOSTNAMES_ADVERTS WITH (KAFKA_TOPIC='matched_adhosts', PARTITIONS=1, REPLICAS=1)
AS SELECT * FROM KEYED_HTTP
INNER JOIN ADVERTS ADVERTS ON KEYED_HTTP.HOST = ADVERTS.HOSTNAME
EMIT CHANGES;
```
This kind of query won't help if the ad server is using HTTPS since the HOST header field would be encrypted.  So instead of matching on HTTP HOST field, match on DNS lookups for that hostname.

Create a new DNS stream that has the `"query"` value for its key:
```sql
CREATE STREAM KEYED_DNS WITH (KAFKA_TOPIC='keyed_dns', PARTITIONS=1, REPLICAS=1)
AS SELECT * FROM  DNS_STREAM
PARTITION BY "query"
EMIT CHANGES;
```
Now create a new stream with a join where the DNS query value matches an ad server hostname:
```sql
CREATE STREAM MATCHED_DOMAINS_DNS WITH (KAFKA_TOPIC='matched_dns', PARTITIONS=1, REPLICAS=1)
AS SELECT * FROM KEYED_DNS
INNER JOIN ADVERTS ADVERTS ON KEYED_DNS."query" = ADVERTS.HOSTNAME
EMIT CHANGES;
```
This query creates a new stream `MATCHED_DOMAINS_DNS` that is backed by a new topic, `matched_dnsThis query doesn't really turn up much, which tells me that these hosts aren't beingThis kind of query won't help if the ad server is using HTTPS since the HOST header field would be encrypted.  matching on HTTP HOST field, match on DNS lookups for that hostname.

You can look for all DNS lookups that match any host listed in the ad_hosts.csv file with the following query:
```
SELECT * FROM  MATCHED_DOMAINS_DNS EMIT CHANGES;
```

## Creating a Table: Aggregate Bytes by Service

If you've already created the CONN_STREAM in the examples above, you can run the following query to create a table from that stream:
```sql
CREATE TABLE 5MIN_BYTE_COUNTS AS
SELECT "id.orig_h" AS LOCALIP,
SERVICE,
TIMESTAMPTOSTRING(WINDOWSTART, 'yyyy-MM-dd HH:mm:ss') AS window_start,
TIMESTAMPTOSTRING(WINDOWEND, 'yyyy-MM-dd HH:mm:ss') AS window_end,
SUM(ORIG_IP_BYTES + RESP_IP_BYTES) AS SUM_BYTES
FROM CONN_STREAM WINDOW TUMBLING (SIZE 5 MINUTES)
GROUP BY "id.orig_h", SERVICE;
```
