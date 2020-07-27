import boto3

# create a bunch of  new EC2 instance

how_many_hosts_to_create = 3
hosts_already_created = 0


def create_instance(host_job, iteration):
    ec2 = boto3.resource('ec2')
    vm_name = 'bhayes-workshop-' + host_job + "-" + iteration
    workshop_host = host_job
    workshop_hostname = host_job + "-" + iteration
    print("Creating Instance ", workshop_host)
    ec2.create_instances(
        #DryRun=True,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': True,
                    # 'Iops': 123,
                    'SnapshotId': 'snap-085c8383cc8833286',
                    'VolumeSize': 250,
                    'VolumeType': 'gp2',
                    # 'KmsKeyId': 'string',
                    'Encrypted': False
                }
            }
        ],
        ImageId='ami-0fc20dd1da406780b',
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.2xlarge',
        KeyName='bert_confluent_aws_key.pem',
        SecurityGroupIds=['sg-0af62df04855a3b2d'],
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
                        'Value': 'Bert Hayes'
                    },
                    {
                        'Key': 'Owner_Email',
                        'Value': 'bhayes@confluent.io'
                    },
                    {
                        'Key': 'workshop_host',
                        'Value': workshop_host
                    },
                    {
                        'Key': 'workshop',
                        'Value': 'dsd'
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
    create_instance('ksqldb', str(i + 1))
    create_instance('c3', str(i + 1))
