#!/bin/bash
# This script gets run on the controller
# This script changes the hostname for each host spun up for the workshop

file='aws_host_info.txt'
key='path_to_aws_keypem.pem'
conf_file='yak_shaving.conf'
workshop_hostname_root=$(cat $conf_file | grep workshop_hostname_root | awk {'print $3'})
#echo $workshop_hostname_root

while IFS= read -r line; do
  echo $line
  hostnumber=$(echo $line | awk {'print $2'})
  public_ip=$(echo $line | awk {'print $4'})
  private_ip=$(echo $line | awk {'print $3'})
  host=$(echo $hostnumber | awk -F- {'print $1'})
  number=$(echo $hostnumber | awk -F- {'print $2'})

  if echo $host | grep -q c3; then
    host=$workshop_hostname_root
  elif echo $host | grep -q ksqldb; then
    host='ksqldb'
  fi
  hostname="${host}${number}"
  # shellcheck disable=SC2095
  echo "Changing hostname for $hostname"
  # shellcheck disable=SC2095

  # Change these lines below from ubuntu@$public_ip to ubuntu@$private_ip
  # depending on whether your control node is another EC2 instance or your laptop, etc.
  /usr/bin/ssh -T -i $key ubuntu@$public_ip "echo $hostname > hostname && sudo cp hostname /etc/hostname" > /dev/null 2>&1 &

  # shellcheck disable=SC2095
  /usr/bin/ssh -T -i $key ubuntu@$public_ip "sudo /bin/hostname $hostname" > /dev/null 2>&1 &
done <"$file"
