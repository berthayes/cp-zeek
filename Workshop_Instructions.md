# Running Multiple Instances for an Instructor Led Workshop

This workshop is a customization based on the Quick Start for Apache Kafka Using Confluent Platform (Docker) documentation available here: https://docs.confluent.io/current/quickstart/ce-docker-quickstart.html

These instructions are for creating a classroom environment for a ksqlDB workshop.
The python scripts use boto3 to talk to the AWS API for automating provisioning, and the shell scripts manage the hosts once they're running.

The various scripts assume that the boto3 library can find your .aws/config and .aws/credentials files (in ~/ by default)
 
The scripts are meant to be run from a single controller node (e.g. your laptop/workstation or an EC2 host in the same VPC), which then spins up EC2 instances and runs commands remotely via SSH.

Admittedly, this is pretty stone-age. There are probably easier ways to do this, but I didn't have time to learn Ansible when I wrote this.


## git clone the repo
Do this on one host (e.g. your laptop or other EC2 host), then distribute it to additional EC2 hosts later on

`git clone https://github.com/berthayes/cp-zeek.git`

Got it?  Get in there!

`cd cp-zeek/workshop_scripts/`

## Edit the config file
Edit the config file yak_shaving.conf to reflect your AWS environment

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

Optional (recommended) - edit the create_aws_instances.py script to specify how many EC2 instances you want created.  Ideally, 1 per student.  By default, the script creates 3 instances.

`vim create_aws_instances.py`

## Run create_aws_instances.py

`python3 create_aws_instances.py`

Wait for completion
`sleep 90`
sleep longer than that, depending on the number of systems you're spinning up
You can check the AWS console to see when all of your hosts are up

Get IP addresses for hosts
This will retrieve the public and private IP addresses for each host
These will be used to centrally manage each host via scripts.

`./get_private_ip_and_name.py > aws_host_info.txt`

Take a look at the `aws_host_info.txt` file just for a sanity check.

`cat aws_host_info.txt`

## Create host lists
This repo contains a few shell scripts that run a ```for i in `cat hosts.txt`; do``` 
kind of loops.  These are designed to distribute files and run commands
remotely on multiple flavors of nodes (in this case, all nodes) using a BASH trick to run each command on each host at the same time, instead of run on one host, then the next,etc.

If your central control node is in AWS in the same VPC, run this command (uses private IP space for hosts):

`cat aws_host_info.txt | awk {'print $3'} > all_nodes.txt`

If your central control node is NOT in AWS network space (e.g. your laptop), run this command (uses public IP space for hosts):

`cat aws_host_info.txt | awk {'print $4'} > all_nodes.txt`

These shell scripts are used for copying files to each host, and/or running commands on each host.
Edit them so that $key points to the correct AWS ssh pem file.

`chmod 755 rscp.sh`

`chmod 755 rc.sh`

SSH to each host to get rid of banner warnings

```for i in `cat all_nodes.txt`; do ssh -oStrictHostKeyChecking=no -i your_aws.pem ubuntu@$i ls; done```

## Update EC2 Host OS
Optional (recommended) run `apt-get update` and `apt-get upgrade`

May as well be on the latest software and avoid any bugs.

```./rc.sh a "sudo apt-get update && sudo apt-get upgrade -y"```

This will take a little while.


## Create DNS records for hosts in Route 53

```cat aws_host_info.txt | awk {'print $2, $4'} > dns_script_hosts.txt```

`python3 name_a_host.py`

By default this script reads the `dns_script_hosts.txt` file.


Run a script to name the hostname on each host
This is done so that hostname matches DNS (set later) and brokers et al are happy
Be sure to edit this file re: `$public_ip` or `$private_ip` for the SSH commands
Also specify the correct ssh key file

`./hostname_changer.sh`

Good idea: run a sanity check to make sure each host has had its hostname changed.

`./rc.sh a hostname`


## Turn off ipv6 because it's a PITA

`./rscp.sh a grub`

`./rc.sh a "sudo cp grub /etc/default/grub"`

`./rc.sh a "sudo update-grub"`

`./rc.sh a "sudo reboot"`

Maybe remind yourself how long it takes an EC2 instance to reboot..

`sleep 90`

## Install openjdk and other packages as required

`./rc.sh a "sudo apt-get install -y openjdk-11-jdk docker docker-compose"`


Add the ubuntu user to the docker group

`./rc.sh a "sudo usermod -a -G docker ubuntu"`

## Get the GitHub repo on each host & copy config
`./rc.sh a "git clone https://github.com/berthayes/cp-zeek"`

`./rscp.sh a yak_shaving.conf`

`./rc.sh a "mv ~/yak_shaving.conf ~/cp-zeek/workshop_scripts/yak_shaving.conf"`

## Change docker-compose
Run shell script to edit the docker-compose.yml file to reflect hostname; also optionally change ports for ksqldb-server and Control Center.

Take a look at the `edit-docker-compose.sh` script before you run it.  By default it moves Confluent Control Center from port 9021 to port 80, and ksqlDB from port 8088 to 443 (plaintext).

`vim edit-docker-compose.sh`

`./rc.sh a "chmod 755 ~/cp-zeek/workshop_scripts/edit-docker-compose.sh"`

`./rc.sh a "/bin/hostname | xargs ~/cp-zeek/workshop_scripts/edit-docker-compose.sh"`

Sanity check (recommended): Check for the presence of `workshop-docker-compose.yml` on remote systems.

`./rc.sh a "ls -al ~/cp-zeek/workshop-docker-compose.yml"`

## Using your own PCAP file
(Optional) Copy your own pcap to `cp-zeek/pcaps/zeek-streamer.pcap`

The zeek-streamer Docker image begins reading the zeek-streamer.pcap file automatically at startup.

## Start docker
`./rc.sh a "docker-compose -f /home/ubuntu/cp-zeek/workshop-docker-compose.yml up -d"`

When Docker finishes spinning everything up, start up the syslog connector and spooldir connector:

`./rc.sh a "./cp-zeek/start_syslog_connector.sh"`

`./rc.sh a "./cp-zeek/start_urlhaus_spooldir.sh"`

Helpful if you need to restart Docker:

`./rc.sh a "sudo systemctl enable docker"`

`sudo systemctl start docker`

## Read Additional PCAP
If you have another pcap file you'd like to read simultaneously, copy it to the `cp-zeek/pcaps` directory

`cp some_other.pcap cp-zeek/pcaps/`

Start reading the pcap and loop for a bzillion times

`./rc.sh a "docker exec -d zeek-streamer /usr/bin/tcpreplay --loop=1000000000 -i dummy0 /pcaps/some_other.pcap"`

TODO: automate deletion of DNS records when workshop is over - this is currently a manual process via Route 53 console.