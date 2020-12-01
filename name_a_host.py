#!/usr/local/bin/python3

import sys
import boto3
import re
from configparser import ConfigParser
import argparse


parser = argparse.ArgumentParser(description=
    '''This script creates a bunch of EC2 hosts in AWS for running Docker & Demos''')
parser.add_argument('-f', dest='config_file', action='store', help='the full path of the config file', default='yak_shaving.conf')

args = parser.parse_args()

if args.config_file:
    config_file = args.config_file

cfg = ConfigParser()
cfg.read(config_file)

pem = cfg.get('aws', 'your_pem')
workshop_hostname_root = cfg.get('workshop', 'workshop_hostname_root')
workshop_domain = cfg.get('workshop', 'workshop_domain')
HostedZoneId = cfg.get('workshop', 'HostedZoneId')
workshop_name = cfg.get('workshop', 'workshop_name')

def create_dns_record(hostname, host_ip):
  role_name_and_number = re.split("-", hostname)
  role_name = role_name_and_number[0]
  role_number = role_name_and_number[1]
  if role_name == 'c3':
      fqdn = workshop_hostname_root + role_number + '.' + workshop_domain
  client = boto3.client('route53')
  response = client.change_resource_record_sets(
      HostedZoneId = HostedZoneId,
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

ec2 = boto3.client('ec2')
node_filters = [
    {'Name': 'tag:workshop', 'Values': [workshop_name]},
    {'Name': 'key-name', 'Values': [pem]},
    {'Name': 'instance-state-name', 'Values': ['running']}
]

response = ec2.describe_instances(Filters=node_filters)
#print(response)

Reservations = response['Reservations']

# Reservations is a list of dictionaries.
# Each dictionary includes a list of Groups and a list of Instances

nodes_list = []
jobs_list = []
hosthash = {}

for res_dict in Reservations:
    instance_list = res_dict['Instances']
    for instance_dict in instance_list:
        try:
            instance_dict['PublicDnsName']
        except KeyError:
            public_dns = "NULL"
        else:
            public_dns = instance_dict['PublicDnsName']
        try:
            instance_dict['PublicIpAddress']
        except KeyError:
            public_ip = "NULL"
        else:
            public_ip = instance_dict['PublicIpAddress']
        tags = instance_dict['Tags']
        for tag_dict in tags:
            for key in tag_dict:
                if tag_dict.get(key) == 'Name':
                    ec2_name = tag_dict['Value']
                elif tag_dict.get(key) == 'workshop_hostname':
                    workshop_hostname = tag_dict['Value']
                elif tag_dict.get(key) == 'workshop_name':
                    workshop_name = tag_dict['Value']

    host_info = {
        'ec2_name': ec2_name,
        'workshop_hostname': workshop_hostname,
        'public_ip': public_ip,
        'public_dns': public_dns,
        }

    create_dns_record(workshop_hostname, public_ip)

