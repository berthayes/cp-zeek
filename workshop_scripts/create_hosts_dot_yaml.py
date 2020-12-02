#!/usr/local/bin/python3

import boto3
from configparser import ConfigParser
import ruamel.yaml
import argparse

parser = argparse.ArgumentParser(description=
    '''This script creates a bunch of EC2 hosts in AWS for running Docker & Demos''')
parser.add_argument('-f', dest='config_file', action='store', help='the full path of the config file')
parser.add_argument('-o', dest='output_file', action='store', help='the full path to the output file', default='hosts.yml')

args = parser.parse_args()

if args.output_file:
    output_file = args.output_file

#output_file = 'hosts.yml'


if args.config_file:
    config_file = args.config_file
else:
    config_file = 'yak_shaving.conf'

cfg = ConfigParser()
cfg.read(config_file)

pem = cfg.get('aws', 'your_pem')
workshop_name = cfg.get('workshop', 'workshop_name')

ec2 = boto3.client('ec2')
node_filters = [
    {'Name': 'tag:workshop', 'Values': [workshop_name]},
    {'Name': 'key-name', 'Values': [pem]},
    {'Name': 'instance-state-name', 'Values': ['running']}
]

response = ec2.describe_instances(Filters=node_filters)
#print(response)

# response is a dictionary
# response['Reservations'] is a list
Reservations = response['Reservations']

# Reservations is a list of dictionaries.
# Each dictionary includes a list of Groups and a list of Instances

nodes_list = []
jobs_list = []
hosthash = {}

for res_dict in Reservations:
    instance_list = res_dict['Instances']
    for instance_dict in instance_list:
        node_job = 'docker_host'
        try:
            instance_dict['PrivateIpAddress']
        except KeyError:
            private_ip = "NULL"
        else:
            private_ip = instance_dict['PrivateIpAddress']
        try:
            instance_dict['PrivateDnsName']
        except KeyError:
            private_dns = "NULL"
        else:
            private_dns = instance_dict['PrivateDnsName']
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
                #elif tag_dict.get(key) == 'node_job':
                    #node_job = tag_dict['Value']
                elif tag_dict.get(key) == 'workshop_name':
                    workshop_name = tag_dict['Value']

    host_info = {
        'ec2_name': ec2_name,
        'node_job': node_job,
        'workshop_name': workshop_name,
        'public_ip': public_ip,
        'private_ip': private_ip,
        'public_dns': public_dns,
        'private_dns': private_dns
        }

    hosthash[public_dns] = node_job

    jobs_list.append(node_job)
    nodes_list.append(public_dns)

dedup = list(dict.fromkeys(jobs_list))

# create dictionary of 'all' common variables
all = {}
vars = {}
vars['vars'] = {
    'ansible_connection': 'ssh',
    'ansible_user': 'ubuntu',
    'ansible_become': 'true',
    'ansible_ssh_private_key_file': '~/aws.pem'
}

all['all'] = vars

common_vars = ruamel.yaml.round_trip_dump(all)

with open(output_file, 'wt') as output:
    for role in dedup:
        hosts = {}
        for n in nodes_list:
            if hosthash[n] == role:
                hosts[n] = None

            mcgilla = {}
            mcgilla[role] = {'hosts': hosts}

        #print(mcgilla)
        nodes_yaml = ruamel.yaml.round_trip_dump(mcgilla)
        output.write(str(nodes_yaml))

    output.write(str(common_vars))
