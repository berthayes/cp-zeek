#!/bin/sh
curl -s localhost:8083/connectors -X POST -H "Content-Type: application/json" -d '{
	"name": "syslog",
	"config": {
		"tasks.max": "1",
		"connector.class": "io.confluent.connect.syslog.SyslogSourceConnector",
		"syslog.port": "5140",
		"syslog.listener": "UDP",
		"confluent.topic.bootstrap.servers": "broker:29092",
		"confluent.topic.replication.factor": "1" 
	}
}'
