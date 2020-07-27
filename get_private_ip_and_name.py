#!/usr/local/bin/python3

import boto3
import re

ec2 = boto3.client('ec2')
host_pattern = re.compile(r'ksqldb|c3')
bert_filters = [
    {'Name': 'tag:workshop', 'Values': ['dsd']},
    {'Name': 'key-name', 'Values': ['bert_confluent_aws_key.pem']},
    {'Name': 'instance-state-name', 'Values': ['running']}
]

response = ec2.describe_instances(Filters=bert_filters)

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
                        wh_hostname = 'netcom'
                    wh_number = wh[1]
        print(workshop_host, workshop_hostname, private_ip, public_ip, wh_hostname + wh_number)
