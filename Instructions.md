 These instructions are for creating any number of EC2 hosts running Confluent Platform and ksqlDB

 The various scripts assume that the boto3 library can find your .aws/config and .aws/credentials files (in ~/ by default)

 ## git clone the repo
 Do this on one host (e.g. your laptop or other EC2 host), then distribute it to additional EC2 hosts later on
git clone https://github.com/berthayes/cp-zeek.git

 Got it?  Get in there!

`cd cp-zeek`

## Edit the config file
Edit the config file yak_shaving.conf to reflect your AWS environment

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

`vim yak_shaving.conf`

Optional (recommended) - edit the create_aws_instances.py script to specify how many EC2 instances you want created.  Ideally, 1 per student.

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

## Create host lists
This repo contains a few shell scripts that run a ```for i in `cat hosts.txt`; do``` 
kind of loops.  These are designed to distribute files and run commands
remotely

If your central control node is in AWS in the same VPC, run this command:

`cat aws_host_info.txt | awk {'print $3'} > all_nodes.txt`

If your central control node is NOT in AWS network space (e.g. your laptop), run this command:

`cat aws_host_info.txt | awk {'print $4'} > all_nodes.txt`

These shell scripts are used for copying files to each host, and/or running commands on each host.
Edit them so that $key points to the correct AWS ssh pem file.

`chmod 755 rscp.sh`
`chmod 755 rc.sh`

ssh connect to each host to get rid of banner warnings

```for i in `cat all_nodes.txt`; do ssh -oStrictHostKeyChecking=no -i your_aws.pem ubuntu@$i ls; done```

## Update EC2 Host OS
Optional (recommended) run `apt-get update` and `apt-get upgrade`

May as well be on the latest software and avoid any bugs.

```./rc.sh a "sudo apt-get update && sudo apt-get upgrade -y"```
This will take a little while.


## Create DNS records for hosts in Route 53

```cat aws_host_info.txt | awk {'print $2, $4'} > dns_script_hosts.txt```

`python3 name_a_host.py`

By default this script reads dns_script_hosts.txt


Run a script to name the hostname on each host
This is done so that hostname matches DNS (set later) and brokers et al are happy
Be sure to edit this file re: `$public_ip` or `$private_ip` for the SSH commands
Also specify the correct ssh key file

`./hostname_changer.sh`

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

## Get the GitHub repo on each host
`./rc.sh a "git clone https://github.com/berthayes/cp-zeek"`

## Change docker-compose
Run shell script to edit the docker-compose.yml file to reflect hostname

`./rc.sh a "chmod 755 ~/cp-zeek/edit-docker-compose.sh"`

`./rc.sh a "sudo /bin/hostname | xargs ~/cp-zeek/edit-docker-compose.sh"`


## Start docker
`./rc.sh a "docker-compose -f /home/ubuntu/cp-zeek/docker-compose.yml up -d"`

Helpful if you need to restart Docker:

`./rc.sh a "sudo systemctl enable docker"`


`sudo systemctl start docker`

## Using your own PCAP file
(Optional) Copy a juicy pcap to cp-zeek/pcaps/
Start reading the pcap and loop for a bzillion times
Note that the zeek-streamer Docker image starts reading the zeek-streamer.pcap file automatically
`./rc.sh a "docker exec -d zeek-streamer /usr/bin/tcpreplay --loop=1000000000 -i dummy0 /pcaps/some_other.pcap"`

TODO: automate deletion of DNS records when workshop is over - this is currently a manual process via Route 53 console.