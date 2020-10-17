#!/bin/sh
curl localhost:8083/connectors -X POST -H "Content-Type: application/json" -d '{
	"name": "ad_hosts",
	"config": {
	  "name": "ad_hosts",
		"connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirCsvSourceConnector",
		"tasks.max": "1",
		"topic": "ad_hosts",
		"input.path": "/var/spooldir/ad_hosts/csv_input",
		"finished.path": "/var/spooldir/ad_hosts/csv_finished",
		"error.path": "/var/spooldir/ad_hosts/csv_errors",
	  "input.file.pattern": ".*\\.csv$",
    "schema.generation.enabled": true,
    "csv.first.row.as.header": true
	}
}'
