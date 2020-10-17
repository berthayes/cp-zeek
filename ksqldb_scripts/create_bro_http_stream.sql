CREATE STREAM http_stream ( \
ts DOUBLE(16,6), \
uid STRING, \
"id.orig_h" VARCHAR, \
"id.orig_p" INTEGER, \
"id.resp_h" VARCHAR, \
"id.resp_p" INTEGER, \
trans_depth INTEGER, \
method STRING, \
host VARCHAR, \
uri VARCHAR, \
referrer VARCHAR, \
version VARCHAR, \
user_agent VARCHAR, \
request_body_len INTEGER, \
response_body_len INTEGER, \
status_code INTEGER, \
status_msg STRING, \
tags ARRAY<STRING>,
orig_fuids ARRAY<STRING>,
orig_mime_types ARRAY<STRING>,
resp_fuids ARRAY<STRING>,
resp_mime_types ARRAY<STRING>) \
WITH (KAFKA_TOPIC='http', VALUE_FORMAT='JSON');
