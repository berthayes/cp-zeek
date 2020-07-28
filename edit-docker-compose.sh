#!/bin/bash
# Dumb script to edit a template file and replace the ksqldb-server line

DOCKER_COMPOSE_FILE="/home/ubuntu/cp-zeek/template-docker-compose.yml"
/bin/sed -e 's/      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: \"http:\/\/ksqldb-server:8088\"/      CONTROL_CENTER_KSQL_KSQLDB1_ADVERTISED_URL: \"http:\/\/'$1'.confluentpublicsector.net\"/' $DOCKER_COMPOSE_FILE >docker-compose.yml