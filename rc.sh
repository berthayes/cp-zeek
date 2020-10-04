#!/bin/sh


key="aws_key.pem"

# This script was originally designed to handle multiple, different kinds of hosts.  C3 server, ksqldb server, or all servers, etc.

if [ $1 = "c" ]; then
	for i in `cat c3_nodes.txt`;
	do (/usr/bin/ssh -i $key ubuntu@$i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess") & done
	wait



elif [ $1 = "a" ]; then
	for i in `cat all_nodes.txt`;
	do (/usr/bin/ssh -i $key ubuntu@$i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess") & done
	wait

elif [ $1 = "k" ]; then
	for i in `cat ksqldb_nodes.txt`;
	do (/usr/bin/ssh -i $key ubuntu@$i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess") & done
	wait

fi


