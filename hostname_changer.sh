#!/bin/bash
# This file gets run on the controller
file='aws_host_info.csv'
key='/home/ubuntu/bert_confluent_aws_keypem.pem'

while IFS= read -r line; do
  echo $line
  hostnumber=$(echo $line | awk {'print $2'})
  private_ip=$(echo $line | awk {'print $3'})
  host=$(echo $hostnumber | awk -F- {'print $1'})
  number=$(echo $hostnumber | awk -F- {'print $2'})

  if echo $host | grep -q c3; then
    host='netcom'
  elif echo $host | grep -q ksqldb; then
    host='ksqldb'
  fi
  hostname="${host}${number}"
  # shellcheck disable=SC2095
  echo "Changing hostname for $hostname"
  # shellcheck disable=SC2095
  /usr/bin/ssh -T -i $key $private_ip "echo $hostname > hostname && sudo cp hostname /etc/hostname" > /dev/null 2>&1 &

  # shellcheck disable=SC2095
  /usr/bin/ssh -T -i $key $private_ip "sudo /bin/hostname $hostname" > /dev/null 2>&1 &
done <"$file"