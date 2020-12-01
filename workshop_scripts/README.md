# Running Multiple Instances for an Instructor Led Workshop

This workshop is a customization based on the Quick Start for Apache Kafka Using Confluent Platform (Docker) documentation available here: https://docs.confluent.io/current/quickstart/ce-docker-quickstart.html

These instructions are for creating a classroom environment for a ksqlDB workshop.
The Python scripts use boto3 automate EC2 provisioning, and the included ansible playbook ```all.yml``` takes care of the rest.

The various scripts assume that the boto3 library can find your .aws/config and .aws/credentials files (in ~/ by default)
 
These Python scripts and Ansible playbook are meant to be run from a single controller node (e.g. your laptop/workstation or an EC2 host in the same VPC), which then spins up EC2 instances and runs the all.yml playbook.


## git clone the repo
Do this on one host (e.g. your laptop or other EC2 host).  Workshop hosts will clone it during when the Ansible playbook runs.

`git clone https://github.com/berthayes/cp-zeek.git`

Got it?  Get in there!

`cd cp-zeek/workshop_scripts/`

## Edit the config file
Edit the config file yak_shaving.conf to reflect your AWS environment.  Alternatively, the Python scripts will take a `-f` flag to specify an alternate config file.

`vim yak_shaving.conf`

Make sure to change these fields in the [aws] section:
```
vm_name = Name_tag_in_AWS
security_group_id = sg-XXXXXXXXXXXXXXX
owner_name = 'Your Name'
your_pem = which_aws.pem
your_email = 'you@your.org'
```
Change these fields in the [workshop] section:
```
workshop_name = 'your_workshop'
workshop_hostname_root = 'zeekqsl'
workshop_domain = yourdomain.com
HostedZoneId = route53_hosted_zone_id
```

## Run create_aws_instances.py

The ```create_aws_instances.py``` requires a ```-n``` argument to specify how many instances to create.  There is no default and if this is not specified the script dies.

```
python3 create_aws_instances.py -n 5
```

Wait for completion.
```
sleep 30
```
Sleep longer than that, depending on the number of systems you're spinning up
You can check the AWS console to see when all of your hosts are up

## Create an Ansible inventory File

```
python3 create_hosts_dot_yaml.py
```

Check the new hosts.yml file and host connectivity by running the Ansible ping module:

```
ansible -i hosts.yml -m ping all
```

You should replies coming back as JSON encoded PONGs.

## Create DNS records for hosts in Route 53

```
python3 name_a_host.py
```

By default this script reads the `hosts.yml` file.

## Run the all.yml Ansible Playbook

The `all.yml` file is an Ansible playbook that handles updating the OS, installing required Python modules, cloning the GitHub repo, and starting up Docker (among other things).

```
ansible-playbook -i hosts.yml all.yml
```