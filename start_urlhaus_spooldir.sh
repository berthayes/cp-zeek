#!/bin/sh
curl -s localhost:8083/connectors -X POST -H "Content-Type: application/json" -d '{
	"name": "csv_spooldir",
	"config": {
	  "name": "csv_spooldir",
		"connector.class": "com.github.jcustenborder.kafka.connect.spooldir.SpoolDirCsvSourceConnector",
		"tasks.max": "1",
		"topic": "urlhaus",
		"input.path": "/var/spooldir/urlhaus/csv_input",
		"finished.path": "/var/spooldir/urlhaus/csv_finished",
		"error.path": "/var/spooldir/urlhaus/csv_errors",
	  "input.file.pattern": ".*\\.csv$",
    "schema.generation.enabled": true,
    "csv.first.row.as.header": true
	}
}'
