#!/bin/bash
# Dumb script to edit a template file and replace the ksqldb-server line

WORKSHOP_DOMAIN=`cat /home/ubuntu/cp-zeek/yak_shaving.conf | grep workshop_domain | awk -F= {'print $2'} | tr -d '[:space:]'`
# This assumes that the domain name that the workshop runs in is managed by AWS Route 53


DOCKER_COMPOSE_FILE="/home/ubuntu/cp-zeek/docker-compose.yml"


# Run this if you want to (have to) run Confluent Control Center on port 80 and ksqldb server (REST API) on port 443 with no encryption
/bin/sed -e 's/      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: \"http:\/\/localhost:8088\"/      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: \"http:\/\/'$1'.'$WORKSHOP_DOMAIN':443\"/' -e 's/      - "9021:9021"/      - "80:9021"/' -e 's/      - "8088:8088"/      - "443:8088"/' $DOCKER_COMPOSE_FILE > /home/ubuntu/cp-zeek/workshop-docker-compose.yml


# Run this if you are sane and can run these services on their default ports (9021 for Confluent Control Center and 8088 for ksqlDB)
#/bin/sed -e 's/      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: \"http:\/\/ksqldb-server:8088\"/      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: \"http:\/\/'$1'.'$WORKSHOP_DOMAIN':8088\"/' $DOCKER_COMPOSE_FILE > /home/ubuntu/cp-zeek/workshop-docker-compose.yml
