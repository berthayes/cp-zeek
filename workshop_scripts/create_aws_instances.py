import boto3
from configparser import ConfigParser

# create a bunch of  new EC2 instance
# TODO: create command line args to specify config file at least

cfg = ConfigParser()
cfg.read('yak_shaving.conf')

how_many_hosts_to_create = 3
hosts_already_created = 0

snapshot_id = cfg.get('aws', 'snapshot_id')
security_group_id = cfg.get('aws', 'security_group_id')
ami = cfg.get('aws', 'ami')
InstanceType = cfg.get('aws', 'InstanceType')
pem = cfg.get('aws', 'your_pem')
Owner_Name = cfg.get('aws', 'Owner_Name')
your_email = cfg.get('aws', 'your_email')
your_workshop_name = cfg.get('workshop', 'workshop_name')

def create_instance(host_job, iteration):
    ec2 = boto3.resource('ec2')
    vm_name = cfg.get('aws', 'vm_name')
    vm_name = vm_name + "-" + host_job + "-" + iteration
    workshop_host = host_job
    workshop_hostname = host_job + "-" + iteration
    SecurityGroupIds = []
    SecurityGroupIds.append(security_group_id)
    print("Creating Instance ", workshop_host)
    ec2.create_instances(
        # DryRun=True,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': True,
                    'SnapshotId': snapshot_id,
                    'VolumeSize': 250,
                    'VolumeType': 'gp2',
                    'Encrypted': False
                }
            }
        ],
        ImageId=ami,
        MinCount=1,
        MaxCount=1,
        InstanceType=InstanceType,
        KeyName=pem,
        SecurityGroupIds=SecurityGroupIds,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': vm_name
                    },
                    {
                        'Key': 'Owner_Name',
                        'Value': Owner_Name
                    },
                    {
                        'Key': 'Owner_Email',
                        'Value': your_email
                    },
                    {
                        'Key': 'workshop_host',
                        'Value': workshop_host
                    },
                    {
                        'Key': 'workshop',
                        'Value': your_workshop_name
                    },
                    {
                        'Key': 'workshop_hostname',
                        'Value': workshop_hostname
                    }
                ]
            }
        ]
    )
    print(vm_name, " has been created")


for i in range(hosts_already_created, how_many_hosts_to_create):
    # This script was originally designed to configure 2 hosts for
    # each student - one for ksqlDB and one for everything else (C3).
    # In the end, the only 'host_job' was C3, which ran everything.

    # create_instance('ksqldb', str(i + 1))
    create_instance('c3', str(i + 1))
