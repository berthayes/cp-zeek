#!/bin/sh


key="/home/ubuntu/.ssh/id_rsa"


if [ $1 = "c" ]; then
	for i in `cat c3_nodes.txt`;
	do /usr/bin/ssh -i $key $i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess";
	done



elif [ $1 = "a" ]; then
	for i in `cat all_nodes.txt`;
	do /usr/bin/ssh -i $key $i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess";
	done

elif [ $1 = "k" ]; then
	for i in `cat ksqldb_nodes.txt`;
	do /usr/bin/ssh -i $key ubuntu@$i $2 && echo && echo "remote_command_successful on $(/usr/bin/nslookup $i | grep name | awk {'print $4'}) I guess"
	done

fi


