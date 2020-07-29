#!/usr/local/bin/python3

import sys
import boto3
import re

# expect to be passed a hostname and an IP
# ksqldb-1 3.129.90.9

input_file = sys.argv[1]
if len(input_file) == 0:
    input_file = 'dns_script_hosts.txt'



client = boto3.client('route53')
with open(input_file) as f:
  content = f.read().splitlines()
#  print(content)
#  type(content)
f.close()

for line in content:
  pair = line.split()
  print(pair)
  hostname = pair[0]
  print(hostname)
  host_ip = pair[1]
  print(host_ip)
  role_name_and_number = re.split("-", hostname)
  role_name = role_name_and_number[0]
  role_number = role_name_and_number[1]
  if role_name == 'c3':
      fqdn = 'netcom' + role_number + '.confluentpublicsector.net'
  elif role_name == 'ksqldb':
      fqdn = 'ksqldb' + role_number + '.confluentpublicsector.net'

  response = client.change_resource_record_sets(
      HostedZoneId = 'Z273IV6G9RGJR2',
      ChangeBatch = {
          'Comment': 'Bert script creating DNS records',
          'Changes': [
              {
                  'Action': 'CREATE',
                  'ResourceRecordSet': {
                      'Name': fqdn,
                      'ResourceRecords': [
                          {
                              'Value': host_ip
                          }
                      ],
                      'TTL': 300,
                      'Type': 'A',

                  }

              }
          ]
      }
  )
  print(response)