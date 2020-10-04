#!/usr/local/bin/python3

import boto3
import re
from configparser import ConfigParser

cfg = ConfigParser()
cfg.read('yak_shaving.conf')

pem = cfg.get('aws', 'your_pem')
your_workshop_name = cfg.get('workshop', 'workshop_name')
workshop_hostname_root = cfg.get('workshop', 'workshop_hostname_root')

# hosts will be generated as: cp1.somedomain.com

ec2 = boto3.client('ec2')
host_pattern = re.compile(r'ksqldb|c3')
workshop_filters = [
    {'Name': 'tag:workshop', 'Values': [your_workshop_name]},
    {'Name': 'key-name', 'Values': [pem]},
    {'Name': 'instance-state-name', 'Values': ['running']}
]

response = ec2.describe_instances(Filters=workshop_filters)

# response is a dictionary
# response['Reservations'] is a list
Reservations = response['Reservations']

# Reservations is a list of dictionaries.
# Each dictionary includes a list of Groups and a list of Instances


for dict in Reservations:
    instance_list = dict['Instances']
    for instance_dict in instance_list:
        try:
            instance_dict['PrivateIpAddress']
        except KeyError:
            private_ip = "NULL"
        else:
            private_ip = instance_dict['PrivateIpAddress']
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
                    workshop_host = tag_dict['Value']
                elif tag_dict.get(key) == 'workshop_hostname':
                    workshop_hostname = tag_dict['Value']
                    wh = workshop_hostname.split("-")
                    wh_hostname = wh[0]
                    if re.match(r'c3', wh_hostname):
                        wh_hostname = workshop_hostname_root
                    wh_number = wh[1]
        print(workshop_host, workshop_hostname, private_ip, public_ip, wh_hostname + wh_number)
